from datetime import date, timedelta
from html import escape
import json
import streamlit as st

st.set_page_config(page_title='Forces HQ | Career, Money & Policy', page_icon='🛡️', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.stApp{background:linear-gradient(150deg,#0b1425,#101d32);color:#e8eff9}
[data-testid="stSidebar"]{background:#0a182c}
.hero{padding:22px;border-radius:17px;background:linear-gradient(110deg,#15385c,#15263f);border:1px solid #365374;margin-bottom:15px}
.hero h1{margin:0;font-size:2rem;color:white}.hero p{margin:5px 0;color:#b9d3ee}
.tile{padding:15px;border:1px solid #334b69;background:#14283f;border-radius:12px;min-height:110px}
.tile small{color:#afd0eb}.tile strong{display:block;color:white;font-size:1.55rem;margin-top:7px}
a{color:#82d7ff!important}
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

if 'profile' not in st.session_state:st.session_state.profile={'service':'British Army','rank':'Sergeant','years':12,'report':'SJAR'}
if 'records' not in st.session_state:st.session_state.records=[]
if 'events' not in st.session_state:st.session_state.events=[]
if 'budget' not in st.session_state:st.session_state.budget={}
PAGES=['🏠 Dashboard','🎖️ My profile','💷 My money','🎯 Entitlements','📚 JSP finder','📅 My career','✍️ Achievement assistant','🏡 Life & future']
with st.sidebar:
 st.title('🛡️ FORCES HQ')
 st.caption('Career • Money • Policy | V0.2')
 page=st.radio('Navigate',PAGES,label_visibility='collapsed')
 st.divider()
 st.warning('DEMO ONLY: do not enter personal financial records, service numbers, names, official appraisals or restricted information. Inputs remain in this temporary session; no accounts or database.')
 st.caption('Independent educational project; not an MOD service or financial adviser.')
st.markdown('<div class="hero"><h1>🛡️ Forces HQ</h1><p>Make sense of military money, benefits, policy and career decisions.</p></div>',unsafe_allow_html=True)
p=st.session_state.profile

def tile(label,value):st.markdown(f'<div class="tile"><small>{escape(str(label))}</small><strong>{escape(str(value))}</strong></div>',unsafe_allow_html=True)
def money(v):return f'£{v:,.0f}'
def policy_link(rec):st.markdown(f'**[{rec["id"]}: {rec["title"]}]({rec["url"]})**')

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
 st.subheader('📚 JSP & official policy finder')
 st.write('Search ordinary words such as **travel**, **housing**, **SJAR**, **leave**, **pension**, or a JSP number. Results link to official publications.')
 query=st.text_input('Search policy',placeholder='e.g. posting, JSP 752, CEA, MPAR')
 def matches(x,q):
  t=(x['id']+' '+x['title']+' '+x['tags']+' '+x['note']).lower()
  return all(s in t for s in q.lower().split())
 found=[x for x in POLICIES if not query.strip() or matches(x,query)]
 if not found:st.info('No matching curated entries. Try a broader term. This is a small verified index, not full-text JSP search.')
 for x in found:
  with st.expander(f"{x['id']} — {x['title']}",expanded=bool(query.strip())):
   st.write(x['note'])
   st.caption('Reference check: '+x['review'])
   st.link_button('Read official guidance',x['url'])
 st.caption('V0.2 searches hand-curated metadata only. It does not retrieve full JSP text, inspect document paragraphs or interpret exceptions. Some authoritative current policies are Defence-only.')

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
 st.info('Future versions may add guided journeys and opt-in reminders; neither is active in V0.2.')

st.divider()
st.caption('Forces HQ V0.2 • Independent educational prototype • No database, real AI, account login, policy full-text search, reminders or JPA integration')
