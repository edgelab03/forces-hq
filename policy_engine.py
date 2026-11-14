"""Evidence retrieval from locally indexed official documents. No generated citations.

Intent rules select clarification questions and expand retrieval vocabulary; they do
not decide eligibility. Answers are extractive, not an LLM or an entitlement engine.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import sqlite3

DATA_DIR = Path(os.environ.get('FORCES_POLICY_DIR', Path(__file__).parent / 'policy_data'))
CATALOGUE = {
 'JSP 752': ('Expenses and allowances', 'https://www.gov.uk/government/publications/jsp-752-tri-service-regulations-for-expenses-and-allowances'),
 'JSP 905': ('AFPS 15 and Early Departure Payments', 'https://www.gov.uk/government/publications/armed-forces-pension-scheme-2015-and-early-departure-payments-scheme-2015-jsp-905-part-one'),
 'JSP 464': ('Accommodation', 'https://www.gov.uk/government/publications/jsp-464-tri-service-accommodation-regulations-tsars'),
 'JSP 760': ('Leave and absence', 'https://www.gov.uk/government/publications/jsp-760-tri-service-regulations-for-leave-and-other-types-of-absences'),
 'JSP 534': ('Resettlement', 'https://www.gov.uk/government/publications/tri-service-resettlement-manual-jsp-534'),
}
INTENTS = {
 'meals': {
  'label':'Meals and subsistence', 'sources':['JSP 752'],
  'pattern':r'\b(lunch|dinner|breakfast|evening meal|food|meals?|messing|subsistence)\b',
  'terms':'meal meals subsistence food messing breakfast lunch dinner',
  'answer':'This is a meals/subsistence question. Buying a meal does not by itself establish an entitlement.',
  'questions':[
   ('meal_duty','Were you on authorised duty away from your normal workplace?',['Not sure','Yes','No']),
   ('meal_provided','Was a suitable meal provided or available through Service catering?',['Not sure','Yes','No']),
   ('meal_timing','Which meal and duty times were involved?',['Not specified','Breakfast','Lunch','Evening meal','Overnight / several meals']),
   ('meal_evidence','Do you have the duty details and any required receipt?',['Not sure','Yes','No'])],
  'related':'entitlements',
 },
 'mileage': {
  'label':'Duty mileage and travel', 'sources':['JSP 752'],
  'pattern':r'\b(mileage|fuel|petrol|diesel|driv\w*|commut\w*|travel|journey|htd|gyh)\b',
  'terms':'motor mileage allowance official duty travel private vehicle',
  'answer':'The journey category and authorisation matter. Ordinary commuting and official duty mileage have different conditions.',
  'questions':[
   ('v07_journey','What sort of journey was this?',['Please select','Ordinary home-to-work journey','Authorised duty journey','Travel home from an assignment','Moving on assignment']),
   ('v07_approved','Was the journey / private vehicle authorised where required?',['Not sure','Yes','No']),
   ('v07_evidence','Do you have supporting documents or mileage records?',['Not sure','Yes','No'])],
  'related':'entitlements',
 },
 'edp': {'label':'Early Departure Payments','sources':['JSP 905'],
  'pattern':r'\b(edp|early departure|pension|afps|retirement|added pension)\b',
  'terms':'early departure payments qualifying service pension age AFPS',
  'answer':'EDP and pension benefits depend on your scheme and qualifying history. Calendar time since enlistment is not necessarily qualifying service.',
  'questions':[('scheme','Which scheme are you checking?',['Not sure','AFPS 15','AFPS 05','AFPS 75','Mixed schemes']),('breaks','Were there breaks, transfers or changes in service type?',['Not sure','Yes','No'])], 'related':'pension'},
 'posting': {'label':'Posting and relocation','sources':['JSP 752','JSP 464'],
  'pattern':r'\b(posting|posted|assignment|relocat\w*|removals?|moving|move)\b',
  'terms':'assignment relocation disturbance removal expenses',
  'answer':'A posting can make relocation and accommodation provisions relevant; it does not establish entitlement on its own.',
  'questions':[('assignment','Do you have official assignment instructions?',['Not sure','Yes','No']),('move_family','Will dependants move with you?',['Not sure','Yes','No'])], 'related':'entitlements'},
 'housing': {'label':'Accommodation and housing','sources':['JSP 464'],
  'pattern':r'\b(housing|accommodation|sfa|sla|mortgage|house|home buy|forces help to buy|fhtb)\b',
  'terms':'accommodation housing family help buy', 'answer':'Accommodation provision depends on the scheme and your circumstances.',
  'questions':[('housing_type','What housing support are you checking?',['Not sure','SFA','SLA','Forces Help to Buy'])], 'related':'entitlements'},
 'family': {'label':'Family and education','sources':['JSP 752'],
  'pattern':r'\b(cea|child\w*|education|school\w*|dependants?|family)\b',
  'terms':'education continuity allowance children dependants', 'answer':'Having dependants does not by itself establish eligibility for a family or education allowance.',
  'questions':[('family_topic','Which support are you checking?',['Not sure','Education continuity','Childcare','Family travel'])], 'related':'entitlements'},
 'leave': {'label':'Leave and absence','sources':['JSP 760'],
  'pattern':r'\b(leave|absence|parental|maternity|paternity|holiday)\b',
  'terms':'leave absence parental annual', 'answer':'Leave depends on the category and current Service instructions.',
  'questions':[('leave_type','Which leave category?',['Not sure','Annual','Parental','Compassionate','Other'])], 'related':'career'},
 'career': {'label':'Career and reporting','sources':['JSP 534'],
  'pattern':r'\b(resettlement|leaving|transition|civilian|career|mpar|sjar|ojar|appraisal|promotion)\b',
  'terms':'resettlement career training employment', 'answer':'Reporting windows require current Service instructions; resettlement support depends on qualifying circumstances. Public reporting policy may be unavailable.',
  'questions':[], 'related':'career'},
}
STOP = set('a an the i my can do does am is are was were be to for of in on at today back me you it this what when how while with and or claim entitled please'.split())


def classify(question):
    """Return a subject, not an entitlement. Meals precede incidental travel."""
    for name, item in INTENTS.items():
        if re.search(item['pattern'], question.lower()):
            return name
    return None


def normalise(text):
    return re.sub(r'\s+', ' ', text).strip()


def split_pages(pages):
    """Keep printed paragraph identifiers; never derive a reference from an intent."""
    chapter = section = ''
    for number, raw in enumerate(pages, 1):
        chunk = []
        paragraph = ''
        for line in raw.splitlines():
            line = line.strip()
            heading = re.match(r'^(CHAPTER|SECTION)\s+(\d+)\b.*', line, re.I)
            para = re.match(r'^(\d{2}\.\d{4}[a-zA-Z]?)[.\s]+(.*)', line)
            if heading or para:
                if chunk:
                    yield dict(page=number, chapter=chapter, section=section, paragraph=paragraph, text=normalise(' '.join(chunk)))
                chunk = []
                if heading:
                    if heading[1].upper() == 'CHAPTER':
                        chapter, section = line, ''
                    else:
                        section = line
                    paragraph = ''
                else:
                    paragraph, line = para[1], para[2]
            chunk.append(line)
        if chunk:
            # Limit unnumbered blocks; page is always a precise, verified locator.
            text = normalise(' '.join(chunk))
            for start in range(0, len(text), 2000):
                yield dict(page=number, chapter=chapter, section=section, paragraph=paragraph, text=text[start:start+2200])


class PolicyIndex:
    def __init__(self, path=DATA_DIR / 'index.sqlite3'):
        self.path = Path(path)

    def connect(self):
        return sqlite3.connect(f'file:{self.path}?mode=ro', uri=True)

    def search(self, question, limit=3):
        if not self.path.exists():
            return []
        intent = classify(question)
        terms = re.findall(r'[a-z0-9]+', question.lower())
        terms = [t for t in terms if t not in STOP and len(t) > 2]
        if intent:
            terms += INTENTS[intent]['terms'].split()
        if not terms:
            return []
        expression = ' OR '.join('"'+t+'"' for t in dict.fromkeys(terms))
        try:
            with self.connect() as db:
                db.row_factory = sqlite3.Row
                rows = db.execute('SELECT p.*, bm25(passages) AS score FROM passages p WHERE passages MATCH ? ORDER BY score LIMIT 80', (expression,)).fetchall()
        except sqlite3.Error:
            return []
        results = []
        for row in rows:
            hit = dict(row)
            if intent and hit['source_id'] not in INTENTS[intent]['sources']:
                continue
            if intent == 'meals' and not re.search(r'\b(meals?|subsistence|messing|food|breakfast|lunch|dinner)\b', hit['text'], re.I):
                continue
            if intent == 'mileage' and not re.search(r'\b(mileage|travel|vehicle|journey)\b', hit['text'], re.I):
                continue
            # Do not display an isolated heading/contents line as policy evidence.
            if len(hit['text']) < 100:
                continue
            if any(h['document_id'] == hit['document_id'] and h['page'] == hit['page'] and h['paragraph'] == hit['paragraph'] for h in results):
                continue
            results.append(hit)
            if len(results) == limit:
                break
        return results

    def status(self):
        manifest = self.path.parent / 'manifest.json'
        if not manifest.exists():
            return {'documents': [], 'errors': [], 'state':'unavailable'}
        try:
            data=json.loads(manifest.read_text())
            if not isinstance(data,dict) or data.get('state') not in ('ready','partial','unavailable') or not isinstance(data.get('documents'),list) or not isinstance(data.get('errors'),list):raise ValueError('Invalid manifest')
            return data
        except (ValueError, OSError):
            return {'documents': [], 'errors':[{'source':'Index','error':'Index manifest is unreadable'}], 'state':'unavailable'}


def write_index(path, documents, retain_existing=False):
    """Build off to the side, then atomically replace a complete public index."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    previous=[]
    if retain_existing and path.exists():
        replaced={doc['source_id'] for doc in documents}
        with sqlite3.connect(f'file:{path}?mode=ro',uri=True) as existing:
            previous=[row for row in existing.execute('SELECT * FROM passages') if row[0] not in replaced]
    staging = path.with_suffix('.building')
    staging.unlink(missing_ok=True)
    with sqlite3.connect(staging) as db:
        db.execute('CREATE VIRTUAL TABLE passages USING fts5(source_id UNINDEXED, document_id UNINDEXED, title, url UNINDEXED, retrieved_at UNINDEXED, sha256 UNINDEXED, page UNINDEXED, chapter, section, paragraph, text)')
        if previous:db.executemany('INSERT INTO passages VALUES (?,?,?,?,?,?,?,?,?,?,?)',previous)
        for doc in documents:
            for item in split_pages(doc['pages']):
                db.execute('INSERT INTO passages VALUES (?,?,?,?,?,?,?,?,?,?,?)', (doc['source_id'],doc['document_id'],doc['title'],doc['url'],doc['retrieved_at'],doc['sha256'],item['page'],item['chapter'],item['section'],item['paragraph'],item['text']))
    staging.replace(path)


def profile_context(profile):
    """Only selected, non-identifying context. Never send it to an external API."""
    parts = [f"{profile.get('service','Not specified')} · {profile.get('rank','Not specified')}"]
    for label,key in [('Scheme','pension_schemes'),('Service type','employment_type'),('Posting','posting'),('Dependants','dependent_count'),('Accommodation','accommodation_type')]:
        value = profile.get(key)
        if isinstance(value,list): value = ', '.join(value)
        if value is not None: parts.append(f'{label}: {value}')
    if profile.get('join_date'):
        parts.append(f"Entered start date: {profile['join_date']} (not verified qualifying service)")
    parts.append(f"Self-reported qualifying years: {profile.get('years','unknown')}")
    return ' · '.join(parts)


def answer(question, profile, circumstances, index=None):
    index = index or PolicyIndex()
    intent = classify(question)
    topic = INTENTS.get(intent, {})
    # Clarifications stay keyed by topic in session state; include actual values
    # in retrieval, without letting an incidental answer override the subject.
    expanded = question + ' ' + ' '.join(str(v) for v in circumstances.values() if v not in ('Yes','No','Not sure','Please select','Not specified'))
    hits = index.search(expanded)
    missing = [label for key,label,_ in topic.get('questions',[]) if circumstances.get(key) in (None,'Not sure','Please select','Not specified')]
    return {'intent':intent,'subject':topic.get('label','Policy document search'),
            'answer':topic.get('answer','I cannot confidently identify this subject. Search results below are passages, not a determination of entitlement.'),
            'status':'Cannot determine entitlement', 'missing':missing,'hits':hits,
            'context':profile_context(profile),'related':topic.get('related'),
            'source_ids':topic.get('sources',[]),
            'unavailable':not hits}
