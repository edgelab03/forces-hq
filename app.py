from datetime import date, timedelta
from html import escape
import json
import re
import difflib
import streamlit as st

st.set_page_config(page_title='Forces HQ | Career, Money & Policy', page_icon='🛡️', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.stApp{background:linear-gradient(150deg,#0b1425,#101d32);color:#e8eff9}
[data-testid="stSidebar"]{background:#0a182c}
.hero{padding:22px;border-radius:17px;background:linear-gradient(110deg,#15385c,#15263f);border:1px solid #365374;margin-bottom:15px}
.hero h1{margin:0;font-size:2rem;color:white}.hero p{margin:5px 0;color:#b9d3ee}
.tile{padding:15px;border:1px solid #334b69;background:#14283f;border-radius:12px;min-height:110px}
.tile small{color:#afd0eb}.tile strong{display:block;color:white;font-size:1.55rem;margin-top:7px}
a{color:#82d7ff!important}.guide{padding:16px;border-radius:14px;background:#122c42;border:1px solid #356179;margin:12px 0}.guide h4{color:#fff;margin:0 0 8px 0}.guide p{color:#d4e5f3;margin:0}
@media(max-width:600px){.hero{padding:15px}.hero h1{font-size:1.6rem}.tile strong{font-size:1.17rem}}
</style>''',unsafe_allow_html=True)

POLICIES=[
 {'id':'JSP 752','title':'Expenses and allowances','tags':'travel relocation disturbance home to duty subsistence separation assignment claims mileage', 'url':'https://www.gov.uk/government/publications/jsp-752-tri-service-regulations-for-expenses-and-allowances','review':'October 2026','note':'Authoritative allowances policy. Check the current version, precise paragraph and any exceptions before claiming.'},
 {'id':'JSP 464','title':'Accommodation and Forces Help to Buy','tags':'SFA SLA housing accommodation married living together mortgage forces help to buy home purchase', 'url':'https://www.gov.uk/government/publications/jsp-464-tri-service-accommodation-regulations-tsars','review':'October 2026','note':'Accommodation policy; Forces Help to Buy is covered by Volume 1, Part 1, Chapter 6.'},
 {'id':'JSP 760','title':'Leave and absence','tags':'annual leave parental maternity paternity compassionate absence holiday', 'url':'https://www.gov.uk/government/publications/jsp-760-tri-service-regulations-for-leave-and-other-types-of-absences','review':'Public page last updated March 2023','note':'Check current authorised instructions for amendments or Service-specific rules.'},
 {'id':'JSP 534','title':'Resettlement and employment support','tags':'leaving service transition resettlement civilian career training employment CTP', 'url':'https://www.gov.uk/government/publications/tri-service-resettlement-manual-jsp-534','review':'March 2025','note':'Covers tri-service resettlement policy and support.'},
 {'id':'JSP 757','title':'Appraisal reporting (SJAR / OJAR / MPAR)','tags':'sjar ojar mpar appraisal report performance promotion reporting window objectives', 'url':'https://www.gov.uk/government/collections/joint-service-publication-jsp','review':'Check authorised current copy','note':'Public JSP index only; detailed current reporting rules and windows may require authorised Defence access.'},
 {'id':'Official MOD benefits','title':'Discover My Benefits','tags':'allowances child childcare education family support CEA all benefits', 'url':'https://discovermybenefits.mod.gov.uk/','review':'Live official website','note':'The official starting point for exploring potential benefits by Service.'},
 {'id':'Pension calculator','title':'Official Armed Forces pension forecast','tags':'AFPS 05 AFPS 15 EDP pension retirement leaving pay forecast', 'url':'https://www.gov.uk/armed-forces-pension-calculator','review':'Live official website','note':'Use the official calculator for scheme-specific estimates rather than the app guessing your pension.'},
]

OPPORTUNITIES=[
 {'name':'Forces Help to Buy','topic':'Buying a home','when':'Planning a property purchase or eligible move','summary':'Interest-free advance, potentially up to 50% of annual salary with a £25,000 cap, subject to conditions.','policy':'JSP 464, Vol 1 Pt 1 Ch 6','url':'https://www.gov.uk/guidance/forces-help-to-buy','action':'Check criteria and apply through JPA where eligible.','keywords':['property','home','buying']},
 {'name':'Disturbance and relocation expenses','topic':'Being posted / moving','when':'An assignment requires a qualifying move','summary':'Potential disturbance and other relocation support; rules differ by circumstances.','policy':'JSP 752','url':'https://www.gov.uk/government/publications/jsp-752-tri-service-regulations-for-expenses-and-allowances','action':'Check current assignment policy with unit HR before spending.','keywords':['posting','moving']},
 {'name':'Travel and subsistence','topic':'Duty travel','when':'Authorised travel or temporary duty','summary':'Potential travel, mileage and subsistence allowances where conditions are met.','policy':'JSP 752','url':'https://www.gov.uk/government/publications/guide-to-expenses-and-allowances-for-service-personnel/guide-to-expenses-and-allowances-for-service-personnel','action':'Check authorisation, receipts, relevant rates and JPA claim rules.','keywords':['travel','posting']},
 {'name':'Service accommodation','topic':'Accommodation','when':'Considering SFA, SLA or substitute accommodation','summary':'Accommodation provision depends on your status and current policy.','policy':'JSP 464','url':'https://www.gov.uk/government/publications/jsp-464-tri-service-accommodation-regulations-tsars','action':'Review housing guidance and the authorised application route.','keywords':['accommodation','posting','family']},
 {'name':'Family and childcare support','topic':'Family','when':'Supporting children or arranging childcare','summary':'Several schemes may be relevant; eligibility depends on the scheme and household.','policy':'Discover My Benefits / scheme-specific rules','url':'https://discovermybenefits.mod.gov.uk/','action':'Review the official family benefits hub and compare applicable schemes.','keywords':['family']},
 {'name':'Education support / CEA','topic':'Family','when':'Researching school continuity during assignments','summary':'Education allowances are tightly conditional and must not be assumed simply from having children.','policy':'JSP 752 and authorised education rules','url':'https://www.gov.uk/government/publications/jsp-752-tri-service-regulations-for-expenses-and-allowances','action':'Review the current scheme and consult specialist education/allowances staff.','keywords':['family','posting']},
 {'name':'Resettlement support','topic':'Leaving the Services','when':'Preparing to transition to civilian life','summary':'Employment support, training and resettlement opportunities depend on your circumstances.','policy':'JSP 534','url':'https://www.gov.uk/government/publications/tri-service-resettlement-manual-jsp-534','action':'Speak with your Service Resettlement Adviser and review CTP options.','keywords':['leaving']},
]


# From AFPRB 55th Report (2026), Appendix 1 Tables 1.1–1.3; annual salary includes X-Factor.
# Scoped intentionally: only OR7 main-spine levels 1–12, trade supplements 1–3.
PAY_2026_OR7={
 1:{1:51615,2:51615,3:52396,4:53219,5:54014,6:54845,7:56024,8:56024,9:57199,10:58310,11:59279,12:60271},
 2:{1:53739,2:53739,3:54641,4:55465,5:56259,6:57090,7:58567,8:58567,9:59742,10:60555,11:61362,12:62145},
 3:{1:55631,2:55631,3:56605,4:57581,5:58583,6:59737,7:61393,8:61393,9:62254,10:62693,11:63086,12:63456},
}
AFPRB_2026_URL='https://assets.publishing.service.gov.uk/media/6a27f8383b15d05a7ce31f52/AFPRB_55th_Report_2026.pdf'

if 'profile' not in st.session_state:st.session_state.profile={'service':'British Army','rank':'Sergeant','years':12,'report':'SJAR'}
if 'records' not in st.session_state:st.session_state.records=[]
if 'events' not in st.session_state:st.session_state.events=[]
if 'budget' not in st.session_state:st.session_state.budget={}
PAGES=['🏠 Dashboard','🎖️ My profile','💷 My money','🎯 Entitlements','📚 JSP finder','📅 My career','✍️ Achievement assistant','🏡 Life & future','🏦 Pension planner']
with st.sidebar:
 st.title('🛡️ FORCES HQ')
 st.caption('Career • Money • Policy | V0.5')
 page=st.radio('Navigate',PAGES,label_visibility='collapsed')
 st.divider()
 st.warning('DEMO ONLY: do not enter personal financial records, service numbers, names, official appraisals or restricted information. Inputs remain in this temporary session; no accounts or database.')
 st.caption('Independent educational project; not an MOD service or financial adviser.')
st.markdown('<div class="hero"><h1>🛡️ Forces HQ</h1><p>Make sense of military money, benefits, policy and career decisions.</p></div>',unsafe_allow_html=True)
p=st.session_state.profile

def tile(label,value):st.markdown(f'<div class="tile"><small>{escape(str(label))}</small><strong>{escape(str(value))}</strong></div>',unsafe_allow_html=True)
def money(v):return f'£{v:,.0f}'
def policy_link(rec):st.markdown(f'**[{rec["id"]}: {rec["title"]}]({rec["url"]})**')

# Guided question routing: curated public policy pointers, not full-text extraction.
GUIDES=[
 {'title':'Fuel, mileage and travel claims','questions':['Can I claim fuel driving to work?','Can I claim mileage for duty travel?','What if I travel to a temporary duty location?'], 'terms':'fuel petrol diesel mileage car commute commuting driving travel duty transport motor home to duty htd get you home gyh', 'answer':'Ordinary commuting, authorised duty travel and travel arising from an assignment have different rules. A claim cannot be established from the word “fuel” alone. Check the type of journey, authorisation and the relevant allowances rules before spending or claiming.', 'ask':['Was this ordinary home-to-work travel or authorised duty travel?','Was it a temporary duty journey, change of assignment or separated-service journey?','Do you have the required approval and evidence?'], 'sources':['JSP 752'], 'next':'Confirm the journey category with your unit HR/admin team, then find the relevant travel provision in the current JSP 752 and applicable JPA claim route.'},
 {'title':'Posting, removals and disturbance allowance','questions':['What can I claim when I get posted?','Can I claim removals or disturbance?'], 'terms':'posting posted relocation move moving removals disturbance assignment new unit packing travel expenses', 'answer':'A qualifying assignment may trigger certain relocation, removal, travel or disturbance provisions. Amounts and conditions vary, so a move alone does not establish an entitlement.', 'ask':['Is this an assignment, voluntary move or other move?','Will your family move with you?','Have you received official assignment instructions?'], 'sources':['JSP 752','JSP 464'], 'next':'Check your assignment instructions, the appropriate JSP 752 relocation provisions and unit HR advice before incurring costs.'},
 {'title':'Housing and Forces Help to Buy','questions':['Can I use Forces Help to Buy?','Am I entitled to service family accommodation?'], 'terms':'housing house buy mortgage forces help to buy fhtb accommodation sfa sla married property advance', 'answer':'Forces Help to Buy and service accommodation are distinct schemes, with separate criteria. Do not assume eligibility from rank or family status alone.', 'ask':['Are you buying a qualifying property or seeking Service accommodation?','Are you currently serving and meeting the scheme-specific conditions?'], 'sources':['JSP 464'], 'next':'Review JSP 464 and the official Forces Help to Buy guidance; seek a formal eligibility check before making financial commitments.'},
 {'title':'Children, schooling and CEA','questions':['Can I claim CEA for boarding school?','What support is there for childcare?'], 'terms':'cea boarding school children education childcare child schooling continuity family nursery dependants', 'answer':'Continuity of Education Allowance and childcare support have separate eligibility requirements. Having children does not automatically qualify a family for either scheme.', 'ask':['Is the query about education continuity or childcare?','Do assignment circumstances meet the current scheme requirements?'], 'sources':['JSP 752','Official MOD benefits'], 'next':'Read the latest education-allowance provisions and official family benefits guidance, and consult the specialist education or unit allowances staff.'},
 {'title':'SJAR, OJAR, MPAR and reporting','questions':['When is my MPAR due?','How do I prepare for my SJAR?'], 'terms':'sjar ojar mpar appraisal reporting reports window promotion officer review objectives career board', 'answer':'Appraisal reviews, report submissions and promotion windows depend on Service-specific policy and the relevant reporting cycle. No universal date can safely be assumed.', 'ask':['Which Service and appraisal type applies?','What is your confirmed reporting cycle and latest instruction?'], 'sources':['JSP 757'], 'next':'Use your unit career-management or reporting chain for current authorised windows. Track your confirmed dates in the Career page.'},
 {'title':'Added Pension and AFPS forecasts','questions':['Can I pay more into AFPS 15?','How does Added Pension affect my retirement?'], 'terms':'pension afps edp retirement added overpay contributions extra pay more quote benefits forecasting leave 05 15', 'answer':'AFPS 15 members can apply to buy Added Pension, subject to scheme conditions. The cost comes from an official quotation; it is not equivalent to investing a fixed monthly amount at a chosen rate.', 'ask':['Which pension schemes do you have benefits in?','Have you obtained an official Added Pension quote?','At what age or service point might you leave?'], 'sources':['Pension calculator'], 'next':'Open the Pension Planner within Forces HQ, then use the official Armed Forces pension/Added Pension calculators and Form 6 to request a quote.'},
 {'title':'Leave and family absence','questions':['How much leave can I take?','What about parental leave?'], 'terms':'leave absence annual parental compassionate maternity paternity holiday special leave', 'answer':'Leave type and eligibility depend on the applicable regulations and Service-specific arrangements.', 'ask':['What leave category is involved?','Have you checked local and Service instructions?'], 'sources':['JSP 760'], 'next':'Check the relevant leave provisions and confirm booking/approval with your chain of command.'},
 {'title':'Resettlement and leaving service','questions':['What help do I get when leaving the Army?','When can I access resettlement training?'], 'terms':'resettlement leaving exit transition civilian employment career training ctp discharge', 'answer':'Resettlement assistance varies by qualifying service and circumstances. Check your entitlement and timescales before booking courses.', 'ask':['What is your anticipated leaving date?','How much qualifying service will you have?'], 'sources':['JSP 534'], 'next':'Contact your Service Resettlement Adviser and check JSP 534 and Career Transition Partnership guidance.'}
]

def rank_guides(query):
 q=re.sub(r'[^a-z0-9 ]',' ',query.lower())
 words=set(q.split())-{'can','i','the','a','of','my','to','for','is','do','how','what','when','be','and','in','get','claim','am','with','on','an'}
 matches=[]
 for item in GUIDES:
  terms=set(item['terms'].split())
  common=len(words & terms)
  candidates=[item['title']]+item['questions']
  similarity=max(difflib.SequenceMatcher(None,q,ex.lower()).ratio() for ex in candidates)
  score=common*3+similarity
  if common or similarity>.48:matches.append((score,item))
 return [item for _,item in sorted(matches,key=lambda t:-t[0])]


if page==PAGES[0]:
 st.subheader('Your military life, in one place')
 cols=st.columns(3)
 for col,l,v in zip(cols,['Service','Rank','Career milestones'],[p['service'],p['rank'],len(st.session_state.events)]):
  with col:tile(l,v)
 st.markdown('### Explore your tools')
 a,b=st.columns(2)
 with a:
  st.info('💷 **Money** — budget your monthly income and model savings.')
  st.info('🎯 **Entitlements** — find schemes worth checking, plus application routes.')
  st.info('📚 **JSP finder** — find the right official policy and its source.')
 with b:
  st.info('📅 **Career** — record your own verified MPAR and reporting dates.')
  st.info('✍️ **Achievements** — prepare truthful evidence, MPAR notes and potential examples.')
  st.info('🏡 **Life & future** — explore housing, postings, pensions and resettlement.')
 st.caption('Use the sidebar to choose a section. All demo data disappears when the session ends.')

elif page==PAGES[1]:
 st.subheader('🎖️ My military profile')
 st.caption('Optional fictional test profile. This does not establish individual entitlement.')
 ranks=['Private / equivalent','Lance Corporal / equivalent','Corporal / equivalent','Sergeant','Staff Sergeant','Warrant Officer','Commissioned Officer']
 services=['British Army','Royal Navy','Royal Air Force','Royal Marines']
 with st.form('profile'):
  service=st.selectbox('Service',services,index=services.index(p['service']))
  rank=st.selectbox('Rank (simplified)',ranks,index=ranks.index(p['rank']))
  years=st.number_input('Completed years served',0,45,int(p['years']))
  report=st.selectbox('Appraisal type',['SJAR','OJAR'],index=['SJAR','OJAR'].index(p['report']))
  if st.form_submit_button('Update demo profile',use_container_width=True):
   st.session_state.profile={'service':service,'rank':rank,'years':years,'report':report};st.success('Profile updated for this session.')
 st.info('Detailed eligibility rules, appraisal calendars and reporting windows must be checked against current authorised guidance.')

elif page==PAGES[2]:
 st.subheader('💷 My money')
 st.caption('Illustrative numbers only — not personalised financial advice.')
 left,right=st.columns(2)
 with left:
  st.markdown('#### Monthly budget')
  income=st.number_input('Monthly take-home income (£)',0,30000,2600,50)
  housing=st.number_input('Housing and essential bills (£)',0,30000,1050,25)
  food=st.number_input('Food and household (£)',0,10000,400,25)
  transport=st.number_input('Transport (£)',0,10000,250,25)
  debts=st.number_input('Debt repayments (£)',0,15000,300,25)
  leisure=st.number_input('Leisure / other (£)',0,15000,250,25)
  surplus=income-housing-food-transport-debts-leisure
  st.metric('Illustrative monthly surplus',money(surplus))
  if surplus<0:st.error('Illustrative spending exceeds income.')
  elif surplus>0:st.success('This is your unallocated monthly amount, not guaranteed savings.')
 with right:
  st.markdown('#### Savings & investment scenarios')
  monthly=st.slider('Monthly contribution (£)',0,1500,200,25)
  years=st.slider('Years',1,35,15)
  annual=st.slider('Illustrative annual return after fees (%)',0.,10.,5.,.5)
  inflation=st.slider('Illustrative annual inflation (%)',0.,8.,2.5,.5)
  r=(1+annual/100)**(1/12)-1
  future=monthly*years*12 if r==0 else monthly*((1+r)**(years*12)-1)/r
  st.metric('Future nominal value',money(future))
  st.metric('In today’s money (inflation-adjusted)',money(future/(1+inflation/100)**years))
  st.caption(f'Your contributions: {money(monthly*12*years)}; projected growth: {money(future-monthly*12*years)}.')
 st.info('Market returns fluctuate and losses are possible. The model assumes steady returns, end-of-month contributions, no withdrawal and no taxes; it is not a pension forecast.')
 st.markdown('**Next:** See the official [Armed Forces pension calculator](https://www.gov.uk/armed-forces-pension-calculator) for service pension estimates.')

elif page==PAGES[3]:
 st.subheader('🎯 Entitlements explorer')
 st.write('Choose a situation to find **schemes to investigate**, not an automatic entitlement decision.')
 situations=['All opportunities','Buying a home','Being posted / moving','Duty travel','Accommodation','Family','Leaving the Services']
 selected=st.selectbox('What is happening in your life?',situations)
 shown=OPPORTUNITIES if selected=='All opportunities' else [x for x in OPPORTUNITIES if x['topic']==selected or (selected=='Being posted / moving' and 'posting' in x['keywords'])]
 for x in shown:
  with st.expander(x['name'],expanded=len(shown)<=2):
   st.write(x['summary'])
   st.caption('When to investigate: '+x['when'])
   st.write('**Policy / guidance:** '+x['policy'])
   st.write('**What to do next:** '+x['action'])
   st.link_button('Open official source',x['url'])
 st.warning('The app does not assess final eligibility, calculate claim values or submit claims. Confirm the current policy, application route and exceptions with authorised unit staff.')

elif page==PAGES[4]:
 st.subheader('🔎 Ask Forces HQ')
 st.write('**Describe your situation in plain English.** We identify the closest topic, then ask what matters before linking you to the policy. This is curated guidance rather than full-document search.')
 query=st.text_input('What do you need help with?',placeholder='e.g. Can I claim fuel when I drive to my new unit?',key='guided_search')
 st.caption('Try: “Claiming fuel”, “My MPAR is due”, “I am moving house”, or “Can I buy extra pension?”')
 if not query.strip():
  st.markdown('#### Popular questions')
  for guide in GUIDES:
   with st.expander(guide['title']):
    for question in guide['questions']:st.write('• '+question)
 else:
  ranked=rank_guides(query)
  if not ranked:
   st.warning('We cannot confidently match that question to the curated guidance yet. Try a simpler description; do not rely on a guessed policy result.')
  else:
   for pos,g in enumerate(ranked[:3]):
    with st.container(border=True):
     st.markdown(('#### Best matching guide: ' if pos==0 else '#### Related guide: ')+g['title'])
     st.write(g['answer'])
     st.markdown('**A few details that could change the answer:**')
     for qn in g['ask']:st.write('• '+qn)
     if pos==0:
      st.markdown('**Quick checks — narrow down your situation:**')
      for idx,question in enumerate(g['ask']):
       st.selectbox(question,['Select an answer','Yes','No','Not sure / depends'],key=f'v05_search_{idx}_{g["title"]}')
      st.caption('These answers identify the facts you need to check; they are not an eligibility decision or an automatic search of the JSP text.')
     st.markdown('**Your next step:** '+g['next'])
     st.markdown('**Official sources:**')
     for sid in g['sources']:
      source=next((x for x in POLICIES if x['id']==sid),None)
      if source:st.link_button(source['id']+' — '+source['title'],source['url'])
   st.info('These are topic-level matches, not verified paragraph-level answers or decisions on eligibility. Ask unit admin or authorised specialists when policy details or exceptions determine your claim.')
 with st.expander('Browse the full starter policy index'):
  for x in POLICIES:
   st.markdown(f'**{x["id"]} — {x["title"]}**')
   st.caption('Source information: '+x['review'])
   st.link_button('Open '+x['id'],x['url'])
 st.caption('V0.5 uses locally curated topic guides and keyword matching, not live JSP retrieval, generative AI or paragraph-level verification. This limitation is intentional to prevent invented policy advice.')

elif page==PAGES[5]:
 st.subheader('📅 Career & reporting milestones')
 st.write('Enter dates you have independently confirmed. **There is no universal SJAR/OJAR or promotion window assumed here.**')
 with st.form('milestones',clear_on_submit=True):
  label=st.selectbox('Milestone',['Objectives agreed','MPAR','SJAR / OJAR drafting','SJAR / OJAR submission','Promotion / board window (verify)','Course / qualification','Posting / assignment','Other'])
  due=st.date_input('Your confirmed date',date.today()+timedelta(days=60))
  if st.form_submit_button('Add milestone'):st.session_state.events.append({'label':label,'date':due});st.success('Added for this session.')
 for i,event in enumerate(st.session_state.events):
  a,b=st.columns([5,1]);a.write(f"**{event['label']}** — {event['date']:%d %b %Y} ({(event['date']-date.today()).days} days)")
  if b.button('Remove',key=f'del{i}'):st.session_state.events.pop(i);st.rerun()
 if not st.session_state.events:st.info('No personal milestones entered yet.')
 st.markdown('**Appraisal guidance:** Refer to your latest authorised JSP 757 and single-Service reporting instructions. For this demo, do not upload official reports.')

elif page==PAGES[6]:
 st.subheader('✍️ Achievement & appraisal preparation')
 st.warning('Use fictional, generic or non-sensitive examples only. Do not paste official reports, names, private personnel assessments or restricted material.')
 with st.form('evidence',clear_on_submit=True):
  action=st.text_area('What did you do?',placeholder='e.g. Planned weekly training for 12 fictional team members')
  result=st.text_area('What changed? Include evidence you could verify.',placeholder='e.g. Improved attendance from 75% to 95%')
  theme=st.selectbox('Development theme',['Leadership','Delivery','Planning','Teamwork','Communication','Developing others','Other'])
  if st.form_submit_button('Add practice achievement'):
   if action.strip() and result.strip():st.session_state.records.append({'action':action.strip(),'result':result.strip(),'theme':theme});st.success('Practice example added.')
   else:st.error('Please provide both the action and the result.')
 if st.session_state.records:
  mode=st.radio('Output style',['SJAR / OJAR evidence','MPAR preparation','Promotion evidence'],horizontal=True)
  rendered=[]
  for i,e in enumerate(st.session_state.records,1):
   base=f"{e['action'].rstrip('.')} . Outcome: {e['result'].rstrip('.')} .".replace(' .','.')
   if mode=='SJAR / OJAR evidence':part=f"{i}. [{e['theme']}] {base}"
   elif mode=='MPAR preparation':part=f"{i}. Achievement: {e['action']}\n   Evidence / impact: {e['result']}\n   Discuss: What worked, what support is needed, and what objective follows?"
   else:part=f"{i}. Evidence theme: {e['theme']}\n   Contribution: {e['action']}\n   Impact: {e['result']}\n   Reflection: Which greater responsibilities does this genuinely evidence?"
   rendered.append(part)
  output='\n\n'.join(rendered)
  st.text_area('Editable draft — review all claims before use',value=output,height=230)
  st.download_button('Download practice draft',output,file_name='forces_hq_practice_notes.txt',mime='text/plain')
  if st.button('Clear practice examples'):st.session_state.records=[];st.rerun()
  st.markdown('#### Evidence quality review')
  for e in st.session_state.records:
   st.write(f"**{e['theme']}** — "+ ('✅ Numbers included' if any(ch.isdigit() for ch in e['result']) else '⚠️ Consider adding verifiable measurements if available'))
   if len(e['action'].split())<8:st.write('⚠️ Consider explaining your individual contribution more clearly.')
 else:st.info('Add a fictional practice achievement above to generate three alternative structured outputs.')
 st.caption('This is a rule-based drafting assistant, not generative AI. It does not invent outcomes, assert promotion potential or access JPA.')

elif page==PAGES[7]:
 st.subheader('🏡 Military life & future')
 topic=st.selectbox('What are you planning?',['Posting / relocation','Housing / buying','Family / education','Leaving / resettlement','Pension planning','Leave'])
 keys={'Posting / relocation':['JSP 752','JSP 464'],'Housing / buying':['JSP 464'],'Family / education':['Official MOD benefits','JSP 752'],'Leaving / resettlement':['JSP 534'],'Pension planning':['Pension calculator'],'Leave':['JSP 760']}
 st.write('**Start with these verified sources:**')
 for entry in POLICIES:
  if entry['id'] in keys[topic]:policy_link(entry)
 st.markdown('**Suggested checklist:** Check current eligibility → confirm with authorised staff → plan timings → retain only the appropriate records in approved systems.')
 st.info('Future versions may add guided journeys and opt-in reminders; neither is active in V0.4.')

elif page==PAGES[8]:
 st.subheader('🏦 Armed Forces pension planning')
 st.write('Understand your pension options using verified pay-table entries and official-quote Added Pension scenarios. This is educational: NOT a personal pension statement, entitlement or purchase quotation.')
 st.markdown('#### 1. Pensionable pay and career forecast (beta)')
 with st.expander('✅ Real 2026 pay-table lookup — SSgt (OR7), trade supplements 1–3',expanded=True):
  st.caption('Verified limited extract from the 2026 Armed Forces Pay Review Body, Appendix 1, Tables 1.1–1.3. Annual salary figures INCLUDE X-Factor. These are recommended 1 April 2026 rates, not a live JPA payslip or proof of pensionable earnings. Check that the rates were implemented and apply to your personal situation.')
  a,b=st.columns(2)
  with a: band=st.selectbox('Trade supplement', [1,2,3],key='pay_band_lookup')
  with b: point=st.selectbox('OR7 increment level',list(range(1,13)),key='pay_inc_lookup')
  tabular=PAY_2026_OR7[band][point]
  st.metric('2026 published annual salary (including X-Factor)',money(tabular))
  st.caption('Special Forces, RRP, bespoke pay and other additional payments are NOT added automatically. Their pensionability must be confirmed under the relevant scheme rules.')
  st.link_button('View official 2026 pay report',AFPRB_2026_URL)
  if st.button('Use this pay figure in the AFPS 15 scenario',key='use_pay_v05'):
   st.session_state['v05_salary']=float(tabular)
   st.success('Pay figure selected for this browser session. Confirm your pensionable earnings before modelling.')
 st.info('For other ranks, officers, Supplement 4, bespoke pay spines or historic rates: use the verified pensionable amount from your statement instead. We will not fabricate missing tables.')
 st.info('Start with **pensionable annual salary**, not total take-home pay. The pay table uses trade supplements and increment points. Specialist or other extra payments count only where officially classified as pensionable. This beta projects **AFPS 15 future accrual only**; it does not reconstruct AFPS 05, McCloud, EDP or your existing accumulated pension.')
 with st.expander('Why do pay bands and specialist payments matter?',expanded=False):
  st.write('Other Ranks pay varies by rank, trade supplement and increment level. Some groups use bespoke pay spines. The MOD 2026 pay review has pay tables that include X-Factor for the applicable main scales. Do not add X-Factor a second time if it is already included.')
  st.write('Recruitment and Retention Pay, temporary duty additions and many allowances are excluded from pensionable earnings unless specifically deemed pensionable by the Scheme manager. An SF-related payment cannot be treated as pensionable merely because it appears on a payslip.')
  st.link_button('2026 AFPRB pay report (pay tables)', 'https://assets.publishing.service.gov.uk/media/6a27f8383b15d05a7ce31f52/AFPRB_55th_Report_2026.pdf')
  st.link_button('JSP 905: AFPS 15 rules', 'https://www.gov.uk/government/publications/armed-forces-pension-scheme-2015-and-early-departure-payments-scheme-2015-jsp-905-part-one')
  st.link_button('MOD pay explanation','https://discovermybenefits.mod.gov.uk/army/your-pay-and-pension/annual-salary/')
 with st.form('pension_pay_v04'):
  c1,c2=st.columns(2)
  with c1:
   pay_category=st.selectbox('Pay category',['Other Ranks main scale','Officer scale','Bespoke / specialist spine','Other / not sure'])
   supplement=st.selectbox('Trade supplement (where applicable)',['Not sure / not applicable','Supplement 1','Supplement 2','Supplement 3','Supplement 4'])
   increment=st.number_input('Pay increment / level',1,20,1)
   annual=st.number_input('Current annual pensionable salary (£) — check payslip',min_value=0.0,max_value=300000.0,value=float(st.session_state.get('v05_salary',0.0)),step=100.0,help='Enter the pensionable salary amount confirmed by official payslip / pay statement. Include X-Factor if already in salary.')
  with c2:
   special=st.selectbox('Specialist / SF / RRP payment',['None','Specialist / bespoke pay spine','Special Forces-related pay','Recruitment & Retention Pay','Other supplement'])
   add=st.number_input('Other ANNUAL payment confirmed pensionable by official documentation (£)',min_value=0.0,max_value=100000.0,value=0.0,step=100.0)
   confirmed=st.checkbox('I have verified that the additional payment above is pensionable (or it is zero)',value=False)
   horizon=st.slider('More years of AFPS 15 accrual to model',1,30,10)
  c3,c4=st.columns(2)
  with c3: pay_growth=st.slider('Illustrative annual rise in pensionable salary (%)',0.0,6.0,2.0,0.5)
  with c4: revalue=st.slider('Illustrative active-service revaluation (%)',0.0,6.0,2.0,0.5)
  done=st.form_submit_button('Calculate future AFPS 15 accrual',use_container_width=True)
 if done:
  if annual<=0:st.warning('Enter a verified pensionable annual salary. A rank and supplement alone are not enough to establish the correct figure.')
  elif not confirmed:st.warning('Confirm additional payment pensionability first, or enter £0 and tick the checkbox to exclude it.')
  else:
   pensionable=annual+add
   cumulative=0.0
   for yr in range(horizon):
    cumulative=cumulative*(1+revalue/100)+pensionable*((1+pay_growth/100)**yr)/47
   with st.container(border=True):
    st.metric('Estimated pension accrued in first modelled year',money(pensionable/47)+' per year')
    st.metric('Indicative annual pension from the FUTURE years modelled',money(cumulative)+' per year')
    st.caption('This is the modelled future AFPS 15 accrual only, not your total pension or an amount payable on leaving. Assumes full-year pensionable earnings, constant salary-growth and active revaluation assumptions, no breaks or flexible-service adjustment. Past accrual, legacy schemes, retirement timing, post-service uprating, EDP and tax are excluded. Your future earnings and rates will vary.')
   if special!='None':st.warning('Specialist pay selected: ensure the amount is incorporated in the pensionable salary or confirmed as pensionable before relying on this scenario. Some specialist/temporary payments are excluded.')
 st.divider()
 st.markdown('#### 2. Get your official full-service pension forecast')

 st.link_button('Official Armed Forces pension calculator', 'https://www.gov.uk/armed-forces-pension-calculator')
 st.caption('Your exact benefits can depend on legacy service, AFPS 05/15, the 2015 Remedy, service dates and other factors. Use official figures, not guessed accrual.')
 st.divider()
 st.markdown('#### 3. Understand purchasing Added Pension')
 st.write('AFPS 15 members may be able to buy additional annual pension through an Added Pension contract. There are member-only and member-and-dependants options. Official pricing uses actuarial factors and scheme rules. A quotation can be requested with **Form 6**; a separate **Form 6A** covers purchasing or cancelling.')
 st.link_button('Official Added Pension forms (6 / 6A)', 'https://www.gov.uk/guidance/veterans-uk-armed-forces-pensions-forms')
 st.link_button('Official pensions guidance and Added Pension tools', 'https://www.gov.uk/guidance/pensions-and-compensation-for-veterans')
 st.divider()
 st.markdown('#### 4. Explore an official-quote scenario')
 st.write('Only enter figures from an **actual official quote**, or choose the fictional demo. We do **not** convert a £200/month contribution into guaranteed extra pension without a quote.')
 demo=st.checkbox('Use fictional demonstration figures',value=True)
 if demo:
  cost=st.number_input('Fictional one-off contract cost (£)',100,100000,6000,100,disabled=True)
  extra=st.number_input('Fictional extra gross annual pension at payment (£)',10,20000,420,10,disabled=True)
 else:
  cost=st.number_input('Cost of Added Pension contract from your quote (£)',0,1000000,0,100)
  extra=st.number_input('Extra gross annual pension from your quote (£)',0,100000,0,10)
 years=st.slider('Illustrative number of years in payment',1,40,20)
 with st.container(border=True):
  st.metric('Additional gross pension each year (quoted scenario)',money(extra))
  st.metric('Total gross payments across illustrated years',money(extra*years))
  st.metric('Illustrative gross payments minus quoted cost',money(extra*years-cost))
  st.caption('Simple nominal arithmetic ONLY. Not a break-even recommendation: ignores timing, tax, inflation, survivor benefits, life expectancy, scheme limits, EDP effects and the time value of money. It is not a forecast of an investment balance. Fictional demonstration costs and benefits are invented solely for testing.')
 st.info('If you qualify for AFPS 15 Early Departure Payments, qualifying Added Pension may also affect EDP benefits. This app does not calculate EDP: use official calculators and a scheme-specific quote.')
 st.markdown('#### 5. Key questions before deciding')
 for item in ['Which AFPS schemes and remedy options apply to my service?','Do I need member-only or member-and-dependants benefits?','What does the official quote say, including permitted payment methods?','How do inflation, tax, EDP eligibility and retirement dates affect the outcome?','Would a different savings or pension arrangement better suit my wider objectives?']:
  st.write('• '+item)
 st.warning('Do not enter service numbers, official statements or identifiable financial data into this public demonstration. Seek regulated independent financial advice for individual pension decisions.')

st.divider()
st.caption('Forces HQ V0.5 • Independent educational prototype • No database, real AI, account login, full-text JSP search, official pension calculations, reminders or JPA integration')
