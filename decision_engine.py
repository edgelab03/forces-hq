"""Versioned deterministic assessment, gated by reviewed primary-source evidence.

Production has no approved rules until source/exception review is complete.
Tests inject explicitly synthetic rule packs; no fixture is a policy authority.
"""
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlsplit
import json
import math
import re

RULE_FILE=Path(__file__).parent/'policies'/'rules.json'
ELIGIBLE='Appears eligible, subject to stated conditions'
INELIGIBLE='Appears ineligible'
MORE='Further information required'
UNVERIFIED='Unable to verify entitlement against current policy'
BENEFIT_STATUS={ELIGIBLE:'Appears eligible — supporting conditions verified', INELIGIBLE:'Not currently eligible', MORE:'Potentially eligible — further information required', UNVERIFIED:'Policy verification required'}
OFFICIAL_HOSTS={'www.gov.uk','assets.publishing.service.gov.uk','www.publishing.service.gov.uk','www.legislation.gov.uk','www.revenue.scot','www.gov.wales'}


def load_rules(path=RULE_FILE):
    try:
        data=json.loads(Path(path).read_text())
        if data.get('schema_version')!=1 or not isinstance(data.get('rules'),list):return []
        return data['rules']
    except (OSError,ValueError,AttributeError):return []


def _valid_url(url):
    try:
        parts=urlsplit(url)
        return parts.scheme=='https' and parts.hostname in OFFICIAL_HOSTS and not parts.username and not parts.password and parts.port in (443,None)
    except ValueError:return False


def evidence_gate(rule,index,today=None):
    """Check exact document identity and quote, not a loosely related search hit."""
    today=today or date.today()
    try:
        if rule['review_status']!='approved' or not rule['reviewed_by'].strip() or not rule['version'].strip() or not rule['exceptions_reviewed'] or not rule.get('coverage_complete'):
            return False,'Policy and exception review is incomplete.'
        effective=date.fromisoformat(rule['effective_from']);until=date.fromisoformat(rule['review_until']);reviewed=date.fromisoformat(rule['reviewed_on'])
        if rule.get('effective_until') and date.fromisoformat(rule['effective_until'])<effective:return False,'Policy version dates are invalid.'
        if not effective<=today<=until or not reviewed<=today:return False,'The rule is not current for this assessment date.'
        if not rule['conditions'] or not isinstance(rule['conditions'],list) or not rule['evidence']:
            return False,'The decision rule is incomplete.'
        if all(c.get('fact') in ('profile.rank','profile.years','profile.service') for c in rule['conditions']):return False,'Rank, Service and seniority alone cannot establish entitlement.'
        with index.connect() as db:
            for proof in rule['evidence']:
                if not _valid_url(proof['url']) or not re.fullmatch(r'[0-9a-f]{64}',proof['sha256']):return False,'The evidence source is not an identified official document.'
                if not all(proof.get(k) for k in ('source_id','title','chapter','section','paragraph','quote','document_version')) or len(proof['quote'])<30 or int(proof['page'])<1:
                    return False,'Exact source/version/paragraph evidence is missing.'
                rows=db.execute('SELECT text, retrieved_at, chapter, section FROM passages WHERE sha256=? AND source_id=? AND paragraph=? AND page=? AND url=?',(proof['sha256'],proof['source_id'],proof['paragraph'],proof['page'],proof['url'])).fetchall()
                quote=' '.join(proof['quote'].split())
                matching=[row for row in rows if quote in ' '.join(row[0].split()) and row[2]==proof['chapter'] and row[3]==proof['section']]
                if not matching:return False,'The reviewed quotation or locator no longer matches the indexed source.'
                if not any(today-timedelta(days=30)<=date.fromisoformat(row[1][:10])<=today for row in matching):return False,'The indexed source needs a fresh publication check.'
        prior_facts=set()
        for condition in rule['conditions']:
            if condition['evidence_index'] not in range(len(rule['evidence'])):return False,'A condition is missing its supporting provision.'
            if condition.get('input_type','choice') not in ('choice','number','date'):return False,'Unsupported question type.'
            if condition.get('when'):
                dependency=condition['when']
                if not isinstance(dependency,dict) or set(dependency)!={'fact','equals'} or dependency['fact'] not in prior_facts:return False,'A dependent condition lacks a preceding question.'
            prior_facts.add(condition['fact'])
            if 'value' not in condition:return False,'A condition comparison is missing.'
            if condition['operator'] not in ('eq','in','gte','lte'):return False,'Unsupported condition operator.'
            if not condition.get('fact') or not condition.get('question') or (condition.get('input_type','choice')=='choice' and not condition.get('options')):return False,'A condition cannot be clarified.'
        if rule.get('category')=='fhtb' and not rule.get('financials'):return False,'FHTB limits have not been verified.'
        if rule.get('financials') and (not rule['financials'].get('salary_fact') or not rule['financials'].get('salary_basis')):return False,'The scheme salary basis has not been verified.'
        if rule.get('financials') and rule.get('financials_evidence_index') not in range(len(rule['evidence'])):return False,'Financial limits lack supporting evidence.'
        if rule.get('claim_process_verified'):
            if not rule.get('claim_steps'):return False,'Verified claim steps are missing.'
            for step in rule['claim_steps']:
                if not step.get('text') or step.get('evidence_index') not in range(len(rule['evidence'])) or (step.get('url') and not _valid_url(step['url'])):return False,'Application instructions lack verified sources.'
        return True,''
    except Exception:
        return False,'Reviewed primary-source evidence is unavailable or malformed.'


def verified_profile_facts(profile,applied=False):
    """User-confirmed profile values, never assume service years establish eligibility."""
    if not applied:return {}
    facts={}
    for field in ('service','rank','employment_type','join_date','pension_schemes','dependent_count','posting','accommodation_type'):
        value=profile.get(field)
        if value not in (None,'','Not specified','Not sure'):
            facts['profile.'+field]={'value':value,'provenance':'user_confirmed'}
    if profile.get('salary_verified') and profile.get('verified_pensionable_salary'):
        facts['profile.salary']={'value':profile['verified_pensionable_salary'],'provenance':'user_confirmed'}
    return facts


def assess(category,facts,index,rules=None,today=None):
    rules=load_rules() if rules is None else rules
    matches=[r for r in rules if isinstance(r,dict) and r.get('category')==category]
    base={'category':category,'status':UNVERIFIED,'reason':'No current reviewed rule pack is available for this question. A search passage alone cannot establish eligibility.', 'missing':[], 'trace':[], 'evidence':[], 'rule':None,'preliminary':True,'claim_steps':[]}
    if len(matches)!=1:
        if len(matches)>1:base['reason']='Conflicting rule versions require policy review.'
        return base
    rule=matches[0];valid,reason=evidence_gate(rule,index,today)
    if not valid:return {**base,'reason':reason}
    if category in ('meals','mileage'):
        incident=facts.get(category+'.incident_date',{})
        try:
            event_date=date.fromisoformat(str(incident.get('value')))
            if incident.get('provenance') not in ('user_confirmed','user_stated','document_checked'):raise ValueError()
        except (ValueError,TypeError,AttributeError):
            return {**base,'status':MORE,'reason':'The date is needed to choose the applicable policy version.','rule':rule,'evidence':rule['evidence'],'missing':[{'fact':category+'.incident_date','question':'On which date did this happen?','input_type':'date','evidence_index':0}]}
        if event_date>(today or date.today()) or event_date<date.fromisoformat(rule['effective_from']) or (rule.get('effective_until') and event_date>date.fromisoformat(rule['effective_until'])):
            return {**base,'reason':'The reviewed policy version does not cover the stated incident date.'}
    trace=[];missing=[]
    for condition in rule['conditions']:
        dependency=condition.get('when')
        if dependency:
            control=facts.get(dependency['fact'],{})
            if control.get('provenance') not in ('user_confirmed','user_stated','document_checked') or control.get('value')!=dependency['equals']:continue
        supplied=facts.get(condition['fact'])
        if not isinstance(supplied,dict) or supplied.get('provenance') not in ('user_confirmed','user_stated','document_checked') or supplied.get('value') in (None,'Not sure','Not specified','Please select',''):
            missing.append(condition);continue
        value=supplied['value'];target=condition['value'];op=condition['operator']
        try:
            if condition.get('input_type')=='date':
                value=date.fromisoformat(str(value));target=date.fromisoformat(str(target))
            if op=='eq':passed=value==target
            elif op=='in':passed=value in target
            elif op=='gte':passed=(isinstance(value,date) and value>=target) if isinstance(value,date) else type(value) in (int,float) and math.isfinite(value) and value>=target
            else:passed=(isinstance(value,date) and value<=target) if isinstance(value,date) else type(value) in (int,float) and math.isfinite(value) and value<=target
        except (ValueError,TypeError):missing.append(condition);continue
        trace.append({'fact':condition['fact'],'passed':passed,'reason':condition.get('failure_reason','The stated condition is not met.'),'evidence_index':condition['evidence_index']})
    failed=[x for x in trace if not x['passed']]
    status=INELIGIBLE if failed else MORE if missing else ELIGIBLE
    reason=failed[0]['reason'] if failed else 'Only the remaining questions below need answers.' if missing else rule.get('plain_english','All conditions in this reviewed rule are satisfied on the information supplied.')
    return {**base,'status':status,'reason':reason,'missing':[] if failed else missing,'trace':trace,'evidence':rule['evidence'],'rule':rule,'claim_steps':rule.get('claim_steps',[]) if rule.get('claim_process_verified') else []}


def benefit_result(category,facts,index,history=None,rules=None):
    if history and history.get('completed'):
        return {'status':'Already claimed or completed','reason':'You marked this journey completed. This is your record, not official approval.','completed':True}
    result=assess(category,facts,index,rules)
    return {'status':BENEFIT_STATUS[result['status']],'reason':result['reason'],'completed':False,'assessment':result}


def advance_limit(salary,assessment):
    """Calculate only from a currently evidence-gated rule, never legacy constants."""
    if assessment.get('status') not in (ELIGIBLE,MORE) or not assessment.get('rule'):return None
    values=assessment['rule'].get('financials',{})
    try:
        fraction=float(values['salary_fraction']);cap=float(values['advance_cap'])
        if not 0<fraction<=1 or cap<=0 or not math.isfinite(cap) or not math.isfinite(salary) or salary<0:return None
        return round(min(salary*fraction,cap),2)
    except (KeyError,ValueError,TypeError):return None


def repayment_estimate(amount,years,annual_rate=0):
    """Generic cashflow estimate. Does not assert FHTB terms or lender approval."""
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in (amount,years,annual_rate)) or amount<0 or not 1<=years<=40 or not 0<=annual_rate<=30:
        raise ValueError('Check amount, years and interest-rate assumptions.')
    months=round(years*12);r=annual_rate/1200
    return round(amount/months if r==0 else amount*r/(1-(1+r)**(-months)),2)


def purchase_budget(price,deposit,advance,mortgage,tax,legal,survey,searches,registration,other=0):
    values=[price,deposit,advance,mortgage,tax,legal,survey,searches,registration,other]
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in values):raise ValueError('Costs and funding must be finite non-negative amounts.')
    cost=sum([price,tax,legal,survey,searches,registration,other]);funding=deposit+advance+mortgage
    return {'total_cost':round(cost,2),'funding':round(funding,2),'shortfall':round(max(0,cost-funding),2),'surplus':round(max(0,funding-cost),2)}


def facts_from_question(category,question,today=None):
    """Extract only explicit dates/meal names; never infer authorisation or eligibility."""
    today=today or date.today();text=question.lower();facts={}
    if category not in ('meals','mileage'):return facts
    stated=None
    match=re.search(r'\b(\d{4}-\d{2}-\d{2})\b',text)
    if match:
        try:stated=date.fromisoformat(match[1])
        except ValueError:pass
    elif re.search(r'\byesterday\b',text) and 'not yesterday' not in text:stated=today-timedelta(days=1)
    elif re.search(r'\btoday\b',text) and 'not today' not in text:stated=today
    if stated:facts[category+'.incident_date']={'value':stated.isoformat(),'provenance':'user_stated'}
    if category=='meals':
        for word,name in [('breakfast','Breakfast'),('lunch','Lunch'),('evening meal','Evening meal'),('dinner','Evening meal')]:
            if re.search(r'\b'+word+r'\b',text):facts['meals.type']={'value':name,'provenance':'user_stated'};break
    return facts
