from datetime import date, timedelta
from copy import deepcopy
from html import escape
import json
import re
import streamlit as st
from app_context import question_handoff, linked_milestones, apply_restored_profile
from policy_ui import render_question
from policy_engine import PolicyIndex, CATALOGUE
import profile_backup
from benefit_journeys import empty_progress
from benefit_ui import render_fhtb, render_benefit_card
from money_overview import render_money_overview
from build_info import build_info
from session_inputs import SessionInputs, retain_inputs, retain_hidden_inputs, rerun_with_retained_inputs

st.set_page_config(page_title='Forces HQ | Career, Money & Policy', page_icon='🛡️', layout='wide', initial_sidebar_state='collapsed')
retain_inputs()
st.markdown('''<style>
.stApp{background:linear-gradient(150deg,#0b1425,#101d32);color:#e8eff9}
[data-testid="stSidebar"]{background:#0a182c}
.hero{padding:22px;border-radius:17px;background:linear-gradient(110deg,#15385c,#15263f);border:1px solid #365374;margin-bottom:15px}
.hero h1{margin:0;font-size:2rem;color:white}.hero p{margin:5px 0;color:#b9d3ee}
.tile{padding:15px;border:1px solid #334b69;background:#14283f;border-radius:12px;min-height:110px}
.tile small{color:#afd0eb}.tile strong{display:block;color:white;font-size:1.55rem;margin-top:7px}
a{color:#82d7ff!important}.guide{padding:16px;border-radius:14px;background:#122c42;border:1px solid #356179;margin:12px 0}.guide h4{color:#fff;margin:0 0 8px 0}.guide p{color:#d4e5f3;margin:0}
div.stButton > button {min-height:44px;border-radius:14px;font-size:.95rem;font-weight:650;border:1px solid #45688b;background:#16324e;color:#f7fbff;} div.stButton > button:hover {background:#235075;border-color:#90c9f1;} @media(max-width:600px){.hero{padding:15px}.hero h1{font-size:1.6rem}.tile strong{font-size:1.17rem}}
.stMainBlockContainer{max-width:1200px;padding-top:4rem;padding-bottom:3rem}
[data-testid="stMain"] input,[data-testid="stMain"] textarea,[data-testid="stMain"] button,[data-testid="stMain"] label{scroll-margin-top:1rem}
.st-key-app_navigation [role="radiogroup"]{display:flex;flex-direction:row!important;flex-wrap:nowrap;gap:4px}
.st-key-app_navigation [role="radiogroup"] label{flex:1;box-sizing:border-box;min-width:44px;min-height:44px;justify-content:center;margin:0!important;padding:2px}
.st-key-app_navigation [role="radiogroup"] label p{font-size:12px!important}
.st-key-app_navigation [role="radiogroup"] label>div>div:first-child{display:none}
.st-key-app_navigation [role="radiogroup"] label>div{gap:0;justify-content:center}
.st-key-app_navigation [role="radiogroup"] label p{white-space:nowrap}
.st-key-app_navigation [role="radiogroup"] label:focus-within{outline:2px solid #70c8f5;outline-offset:2px}
.st-key-app_navigation [role="radiogroup"] label:has(input:checked){background:#203c59;border-radius:8px}
.st-key-dashboard [data-testid="stHorizontalBlock"]{flex-direction:row!important;gap:10px}
.st-key-dashboard [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{width:calc(50% - 5px)!important;flex:1 1 0!important;min-width:0!important}
.st-key-dashboard button{min-height:76px!important;font-size:14px!important;background:#14283f;border:1px solid #304963}
.st-key-dashboard button p{white-space:pre-line;font-size:14px}
.st-key-brand_header{flex-direction:row!important;flex-wrap:nowrap!important;justify-content:space-between}
.st-key-secondary_navigation{flex-direction:row!important;flex-wrap:wrap!important;gap:6px}
.st-key-secondary_navigation button{min-height:44px!important;font-size:13px!important}
.st-key-brand_header button{min-height:44px!important}
.st-key-brand_header h3{padding:0;font-size:1.25rem}
.st-key-welcome p{margin:0}
.st-key-policy_entry button{min-height:48px!important}
[data-testid="stMetricValue"]{white-space:normal;overflow-wrap:anywhere;font-size:1.6rem}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,textarea{font-size:16px!important}
button:focus-visible,a:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid #70c8f5!important;outline-offset:3px}
@media(max-width:640px){
 .stMainBlockContainer{padding:4rem .85rem 1rem}
 [data-testid="stHorizontalBlock"]{flex-direction:column;gap:.65rem}
 [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{width:100%!important;flex:1 1 auto!important;min-width:0!important}
 div.stButton>button,[data-testid="stDownloadButton"] button,[data-testid="stLinkButton"] a{min-height:48px;width:100%}
 .tile{min-height:0;padding:12px}
 .hero h1{font-size:1.5rem}
 [data-testid="stMetricValue"]{font-size:1.35rem}
}
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
 {'name':'Forces Help to Buy','topic':'Buying a home','when':'Planning a property purchase or eligible move','summary':'A MOD home-buying scheme. Use the connected guide for an evidence-gated assessment; current scheme amounts and terms require policy verification.','policy':'JSP 464, Vol 1 Pt 1 Ch 6','url':'https://www.gov.uk/guidance/forces-help-to-buy','action':'Check criteria and apply through JPA where eligible.','keywords':['property','home','buying']},
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

DEFAULT_PROFILE={'service':'British Army','rank':'Sergeant','years':12,'report':'SJAR','cap_badge':'Not specified','trade':'Not specified','join_date':None,'dob':None,'transfer_history':'None / not recorded','pay_supplement':None,'pay_increment':None,'verified_pensionable_salary':None,'salary_verified':False,'specialist_pay':'Not specified','accommodation':'Not specified','family':'Not specified','posting':'Not specified','planned_exit':None,'added_pension':'Not recorded','accommodation_type':'Not specified','family_status':'Prefer not to say','dependent_count':0,'dependent_ages':'','posting_location':'','expected_posting_location':'','employment_type':'Regular','pension_schemes':['Not sure'],'rank_history':[],'career_history':[],'dob_set':False,'join_date_set':False,'planned_exit_set':False}
if 'profile' not in st.session_state:st.session_state.profile=deepcopy(DEFAULT_PROFILE)
else:
 for field,default in DEFAULT_PROFILE.items():st.session_state.profile.setdefault(field,default)

if 'records' not in st.session_state:st.session_state.records=[]
if 'events' not in st.session_state:st.session_state.events=[]
if 'budget' not in st.session_state:st.session_state.budget={}
st.session_state.setdefault('benefits',{}).setdefault('fhtb',empty_progress())
PAGES=['🏠 Dashboard','🎖️ My profile','💷 My money','🎯 Entitlements','📚 JSP finder','📅 My career','✍️ Achievement assistant','🏡 Life & future','🏦 Pension planner']
if st.session_state.get('pending_profile_restore'):
 apply_restored_profile(st.session_state,st.session_state.pop('pending_profile_restore'),PAGES[1])
if 'nav_page' not in st.session_state:st.session_state.nav_page=PAGES[0]
if st.session_state.nav_page not in PAGES:st.session_state.nav_page=PAGES[0]
DESTINATIONS={'Home':[0], 'Policy':[4], 'Claims':[3], 'Money':[2,8], 'Career':[5,6,7], 'Profile':[1]}
def destination_for(page):
 return next(name for name,indices in DESTINATIONS.items() if PAGES.index(page) in indices)
st.session_state.nav_primary=destination_for(st.session_state.nav_page)
st.session_state.setdefault('nav_sidebar',st.session_state.nav_page)
st.session_state.setdefault('nav_top',st.session_state.nav_page)
def navigate(destination):
 st.session_state.active_journey=None
 st.session_state.money_overview=False
 st.session_state.nav_page=destination
 st.session_state.nav_primary=destination_for(destination)
 st.session_state.nav_sidebar=destination
 st.session_state.nav_top=destination

def open_fhtb():
 navigate(PAGES[3])
 st.session_state.active_journey='fhtb'
 st.session_state.benefits['fhtb']['interested']=True

def open_money():
 navigate(PAGES[2])
 st.session_state.money_overview=True

def change_section(source):
 navigate(st.session_state[source])

def change_destination():
 destination=st.session_state.nav_primary
 navigate(PAGES[DESTINATIONS[destination][0]])
 if destination=='Money':st.session_state.money_overview=True

def ask_question(question):
 question_handoff(st.session_state,question,PAGES[4])
 navigate(PAGES[4])

def ask_home():
 ask_question(st.session_state.get('home_question',''))

def ask_opportunity(question):
 ask_question(question)

with st.sidebar:
 st.title('🛡️ FORCES HQ')
 st.caption('Independent educational app · Not an official MOD service')
 st.warning('Use fictional/non-identifying data only. Do not enter service numbers, operational information, official assessments or identifiable family details.')
 with st.expander('All tools'):
  for index,label in enumerate(PAGES):
   st.button(label,key='sidebar_'+str(index),on_click=navigate,args=(label,),use_container_width=True)
 with st.expander('Build and source status'):
  info=build_info()
  st.json(info)
  st.caption('Local process identity only. A hosted app must be checked separately.')
  st.caption('Policy index: '+PolicyIndex().status()['state'])
# Native bottom placement reserves page space and stays outside the scroll area.
with st.bottom:
 with st.container(key='app_navigation'):
  st.radio('Primary navigation',list(DESTINATIONS),key='nav_primary',horizontal=True,on_change=change_destination,label_visibility='collapsed',width='stretch')
page=st.session_state.nav_page
ui=SessionInputs(page)
with st.container(key='brand_header',horizontal=True,vertical_alignment='center'):
 st.markdown('### 🛡️ Forces HQ')
 st.button('👤',help='Open profile',key='header_profile',on_click=navigate,args=(PAGES[1],))
current_destination=destination_for(page)
SECONDARY={'Money':[(2,'Budget & savings'),(8,'Pay & pensions')], 'Career':[(5,'Milestones'),(6,'Achievements'),(7,'Life & future')]}
if current_destination in SECONDARY:
 with st.container(key='secondary_navigation',horizontal=True):
  for index,label in SECONDARY[current_destination]:
   st.button(label,key='group_nav_'+str(index),on_click=navigate,args=(PAGES[index],),type='primary' if page==PAGES[index] else 'secondary')
p=st.session_state.profile

def tile(label,value):st.markdown(f'<div class="tile"><small>{escape(str(label))}</small><strong>{escape(str(value))}</strong></div>',unsafe_allow_html=True)
def money(v):return f'£{v:,.0f}'
def policy_link(rec):st.markdown(f'**[{rec["id"]}: {rec["title"]}]({rec["url"]})**')
def profile_pay():
 if p.get('rank')=='Staff Sergeant' and p.get('pay_supplement') in PAY_2026_OR7 and p.get('pay_increment') in PAY_2026_OR7[p['pay_supplement']]:
  return PAY_2026_OR7[p['pay_supplement']][p['pay_increment']]
 return None


if st.session_state.get('active_journey')=='fhtb':
 render_fhtb(p,st.session_state.get('profile_applied',False),ask_question,lambda:navigate(PAGES[3]),lambda:navigate(PAGES[1]))

elif page==PAGES[0]:
 with st.container(key='welcome',border=True):
  st.markdown('**Welcome back**')
  summary=' · '.join(str(p.get(field)) for field in ('rank','service') if p.get(field) and p.get(field)!='Not specified')
  st.caption(summary or 'Your demo profile')
  if not st.session_state.get('profile_applied'):st.caption('Example profile · Edit in Profile')
 with st.form('home_ask',clear_on_submit=False,border=False):
  st.text_input('Ask Forces HQ',key='home_question',placeholder='Can I claim my lunch back today?',max_chars=1500)
  st.form_submit_button('Ask Forces HQ',on_click=ask_home,use_container_width=True,type='primary')
 with st.container(key='dashboard'):
  cards=[('Claims','Check allowances',lambda:navigate(PAGES[3])),('Pay','Your money overview',open_money),('Housing','Plan a home purchase',open_fhtb),('Pensions','Explore your scheme',open_money),('Career','Your next step',lambda:navigate(PAGES[5]))]
  for start in (0,2,4):
   for col,(title,detail,action) in zip(st.columns(2),cards[start:start+2]):
    with col:st.button(title+'\n'+detail,key='dashboard_'+title,on_click=action,use_container_width=True)
 render_benefit_card(p,st.session_state.get('profile_applied',False),st.session_state.benefits['fhtb'],open_fhtb)
 if st.session_state.events:
  next_event=linked_milestones(p,st.session_state.events)[0]
  st.caption('Career: '+next_event['label']+' · '+next_event['date'])

elif page==PAGES[1]:
 st.subheader('🎖️ My military profile')
 if st.session_state.pop('profile_saved',False):st.success('Linked profile updated for this session. Other sections will use your choices.')
 st.caption('One linked test profile powers the dashboard, pay lookup, pension inputs and relevant guidance. Please use fictional/non-identifying data in this public demo.')
 ranks=['Private / equivalent','Lance Corporal / equivalent','Corporal / equivalent','Sergeant','Staff Sergeant','Warrant Officer','Warrant Officer Class 2','Warrant Officer Class 1','Commissioned Officer']
 services=['British Army','Royal Navy','Royal Air Force','Royal Marines']
 def choose_index(items,value):return items.index(value) if value in items else 0
 with st.container(border=True):
  st.caption('Draft changes stay in this session. Select Update linked demo profile to apply them to other sections.')
  a,b=st.columns(2)
  with a:
   service=ui.selectbox('Service',services,index=choose_index(services,p['service']),key='v06_service')
   rank=ui.selectbox('Rank',ranks,index=choose_index(ranks,p['rank']),key='v06_rank')
   cap=ui.text_input('Cap badge / branch (optional)',value=p['cap_badge'] if p['cap_badge']!='Not specified' else '',key='v06_cap')
   trade=ui.text_input('Trade / role (optional)',value=p['trade'] if p['trade']!='Not specified' else '',key='v06_trade')
   years=ui.number_input('Completed qualifying years (self-reported)',0,45,int(p['years']),key='v06_years')
   report=ui.selectbox('Appraisal type',['SJAR','OJAR'],index=choose_index(['SJAR','OJAR'],p['report']),key='v06_report')
   transfer=ui.selectbox('Service history', ['None / not recorded','Transfer / break in service','Commissioned from ranks','Other history — check statement'],index=choose_index(['None / not recorded','Transfer / break in service','Commissioned from ranks','Other history — check statement'],p['transfer_history']),key='v06_transfer')
  with b:
   band_options=['Not selected',1,2,3,4]
   band_default=p['pay_supplement'] if p['pay_supplement'] in band_options else 'Not selected'
   band=ui.selectbox('Trade supplement',band_options,index=choose_index(band_options,band_default),key='v06_band')
   point=ui.selectbox('Increment / level',['Not selected']+list(range(1,21)),index=choose_index(['Not selected']+list(range(1,21)),p['pay_increment']),key='v06_point')
   salary=ui.number_input('Verified annual pensionable earnings (£) — optional',0,300000,int(p['verified_pensionable_salary'] or 0),step=100,key='v06_salary',help='Use only confirmed pensionable earnings. A gross payslip total may include non-pensionable allowances.')
   sal_check=ui.checkbox('I have checked this pensionable earnings amount against official documentation',value=bool(p['salary_verified']),key='v06_salary_checked')
   specialist=ui.selectbox('Specialist pay', ['Not specified','None','SF-related payment','Recruitment and Retention Pay','Other'],index=choose_index(['Not specified','None','SF-related payment','Recruitment and Retention Pay','Other'],p['specialist_pay']),key='v06_special')
   posting=ui.selectbox('Posting circumstances',['Not specified','No planned move','Upcoming assignment / move'],index=choose_index(['Not specified','No planned move','Upcoming assignment / move'],p['posting']),key='v06_posting')
   family=ui.selectbox('Family circumstances',['Not specified','No dependants recorded','Dependants / children'],index=choose_index(['Not specified','No dependants recorded','Dependants / children'],p['family']),key='v06_family')
   added=ui.selectbox('AFPS Added Pension',['Not recorded','No contract','Purchased / active contract','Not sure'],index=choose_index(['Not recorded','No contract','Purchased / active contract','Not sure'],p['added_pension']),key='v06_added')
  st.markdown('#### Optional career and family context (fictional demo details only)')
  c,d=st.columns(2)
  with c:
   join_date_set=ui.checkbox('Record enlistment date',value=bool(p.get('join_date_set') or p.get('join_date')),key='v07_has_join')
   join_date=ui.date_input('Date joined',value=p.get('join_date'),min_value=date(1960,1,1),max_value=date.today(),disabled=not join_date_set,key='v07_join',format='DD/MM/YYYY')
   dob_set=ui.checkbox('Record birth date',value=bool(p.get('dob_set') or p.get('dob')),key='v07_has_dob')
   dob=ui.date_input('Date of birth',value=p.get('dob'),min_value=date(1940,1,1),max_value=date.today(),disabled=not dob_set,key='v07_dob',format='DD/MM/YYYY')
   employment=ui.selectbox('Service type',['Regular','Reserve','FTRS','Not specified'],index=choose_index(['Regular','Reserve','FTRS','Not specified'],p.get('employment_type','Regular')),key='v07_employment')
   posting_location=ui.text_input('Current posting (general location, optional)',value=p.get('posting_location',''),key='v07_post_loc')
   expected_posting_location=ui.text_input('Next posting / location (optional)',value=p.get('expected_posting_location',''),key='v07_next_loc')
  with d:
   family_status=ui.selectbox('Family / relationship status',['Prefer not to say','Single','Married / civil partnership','Partner','Separated / divorced','Widowed'],index=choose_index(['Prefer not to say','Single','Married / civil partnership','Partner','Separated / divorced','Widowed'],p.get('family_status','Prefer not to say')),key='v07_family_status')
   dep_count=ui.number_input('Number of dependants (fictional)',min_value=0,max_value=12,value=int(p.get('dependent_count',0)),key='v07_dep_count')
   dep_ages=ui.text_input('Dependants’ ages (optional, e.g. 8, 12)',value=p.get('dependent_ages',''),key='v07_dep_ages')
   accom=ui.selectbox('Accommodation',['Not specified','SFA','SLA','Private rented','Own home','Substitute accommodation','Other'],index=choose_index(['Not specified','SFA','SLA','Private rented','Own home','Substitute accommodation','Other'],p.get('accommodation_type','Not specified')),key='v07_accom')
   schemes=ui.multiselect('Scheme membership (self-reported; not verified)',['AFPS 75','AFPS 05','AFPS 15','RFPS 05','Not sure'],default=[x for x in p.get('pension_schemes',['Not sure']) if x in ['AFPS 75','AFPS 05','AFPS 15','RFPS 05','Not sure']],key='v07_schemes')
   exit_set=ui.checkbox('Record planned leaving date',value=bool(p.get('planned_exit_set') or p.get('planned_exit')),key='v07_exit_set')
   exit_date=ui.date_input('Planned exit',value=p.get('planned_exit'),min_value=min(date.today(),p.get('planned_exit') or date.today()),max_value=date(2080,12,31),disabled=not exit_set,key='v07_exit',format='DD/MM/YYYY')
  submitted=st.button('Update linked demo profile',use_container_width=True)
 profile_errors=[]
 if join_date_set and join_date is None:profile_errors.append('Choose a date joined, or untick Record enlistment date.')
 if dob_set and dob is None:profile_errors.append('Choose a birth date, or untick Record birth date.')
 if exit_set and exit_date is None:profile_errors.append('Choose a planned leaving date, or untick Record planned leaving date.')
 if dob_set and join_date_set and dob and join_date and dob>=join_date:profile_errors.append('The birth date must be before the enlistment date.')
 if 'Not sure' in schemes and len(schemes)>1:profile_errors.append('Choose named pension schemes or Not sure, rather than both.')
 if submitted and profile_errors:
  for error in profile_errors:st.error(error)
 if submitted and not profile_errors:
  # Draft widgets have separate keys; apply only a valid, explicitly saved profile.
  st.session_state.profile={**p,'service':service,'rank':rank,'cap_badge':cap.strip() or 'Not specified','trade':trade.strip() or 'Not specified','years':years,'report':report,'transfer_history':transfer,'pay_supplement':band if isinstance(band,int) else None,'pay_increment':point if isinstance(point,int) else None,'verified_pensionable_salary':float(salary) if salary>0 else None,'salary_verified':bool(sal_check and salary>0),'specialist_pay':specialist,'posting':posting,'family':family,'added_pension':added,'join_date':join_date if join_date_set else None,'join_date_set':join_date_set,'dob':dob if dob_set else None,'dob_set':dob_set,'employment_type':employment,'posting_location':posting_location.strip(),'expected_posting_location':expected_posting_location.strip(),'family_status':family_status,'dependent_count':dep_count,'dependent_ages':dep_ages.strip(),'accommodation_type':accom,'pension_schemes':schemes,'planned_exit':exit_date if exit_set else None,'planned_exit_set':exit_set,'family':'Dependants / children' if dep_count>0 else family}
  st.session_state.profile_applied=True
  st.session_state.profile_saved=True
  rerun_with_retained_inputs()
 st.markdown('#### Promotion and career timeline')
 st.caption('Add fictional dated promotions. Dates provide context; they do not calculate past pay, pension schemes or qualifying service.')
 with st.container(border=True):
  x,y=st.columns(2)
  with x: hist_rank=ui.selectbox('Rank attained',['Private / equivalent','Lance Corporal / equivalent','Corporal / equivalent','Sergeant','Staff Sergeant','Warrant Officer','Warrant Officer Class 2','Warrant Officer Class 1','Commissioned Officer'])
  with y: hist_date=ui.date_input('Effective date of rank',value=date(2020,1,1),min_value=date(1960,1,1),max_value=date.today())
  hist_note=ui.text_input('Optional non-identifying milestone (course, posting, qualification)')
  if st.button('Add dated milestone',use_container_width=True):
   if hist_date is None:st.error('Choose an effective date of rank before adding a promotion milestone.')
   elif p.get('join_date') and hist_date<p['join_date']:st.error('The promotion date cannot be before the enlistment date in your linked profile.')
   else:
    st.session_state.profile.setdefault('rank_history',[]).append({'rank':hist_rank,'date':hist_date.isoformat(),'note':hist_note.strip()})
    st.session_state.profile['rank_history'].sort(key=lambda e:e['date'])
    ui.clear('Rank attained','Effective date of rank','Optional non-identifying milestone (course, posting, qualification)')
    rerun_with_retained_inputs()
 for j,item in enumerate(p.get('rank_history',[])):
  ca,cb=st.columns([5,1]);ca.write(f"**{item['rank']}** — {item['date']}"+(f" · {item['note']}" if item.get('note') else ''))
  if cb.button('Remove',key=f'del_rank_{j}'):
   st.session_state.profile['rank_history'].pop(j);rerun_with_retained_inputs()
 if p.get('rank_history') and p['rank_history'][-1]['rank']!=p['rank']:
  st.info('Your latest timeline rank differs from your selected current rank. Confirm both before using this profile.')
 st.info('Cap badge alone does NOT determine supplement, pensionable pay or allowances. Confirm trade/pay point and specialist eligibility individually. Service changes, breaks and legacy scheme membership require official history before pension forecasting.')
 with st.expander('Save or restore an encrypted profile'):
  st.caption('Download a password-encrypted file to keep structured profile settings, career dates and home-buying progress/budget assumptions between sessions. No account or server database. Posting locations, free-text notes, questions and achievements are excluded. Keep this file and its passphrase safe; there is no recovery service.')
  with st.form('save_profile',clear_on_submit=True):
   backup_password=st.text_input('Backup passphrase (at least 12 characters)',type='password')
   create_backup=st.form_submit_button('Prepare encrypted profile')
  if create_backup:
   try:
    st.session_state.profile_backup_file=profile_backup.save(p,st.session_state.events,backup_password,benefits=st.session_state.benefits)
   except ValueError as exc:st.error(str(exc))
  if st.session_state.get('profile_backup_file'):
   st.download_button('Download encrypted profile',st.session_state.profile_backup_file,file_name='forces-hq-profile.fhq',mime='application/octet-stream')
  with st.form('restore_profile',clear_on_submit=True):
   uploaded=st.file_uploader('Encrypted profile file',type=['fhq'])
   restore_password=st.text_input('Restore passphrase',type='password')
   restore_confirm=st.checkbox('Replace my current structured profile, career dates and benefit progress from this file')
   restore=st.form_submit_button('Restore encrypted profile')
  if restore:
   if not uploaded or not restore_confirm:st.error('Choose a backup and confirm replacement first.')
   else:
    try:
     restored=profile_backup.load(uploaded.getvalue(),restore_password)
     st.session_state.pending_profile_restore=restored
     st.session_state.pop('profile_backup_file',None)
     rerun_with_retained_inputs()
    except ValueError as exc:st.error(str(exc))
  if st.button('Discard prepared backup from this session'):
   st.session_state.pop('profile_backup_file',None)
   rerun_with_retained_inputs()
 if st.session_state.events:
  with st.expander('Linked career milestones'):
   for event in linked_milestones(p,st.session_state.events):st.write(event['date']+' · '+event['label'])

elif page==PAGES[2] and st.session_state.get('money_overview'):
 render_money_overview(p,st.session_state.get('profile_applied',False),lambda:navigate(PAGES[2]),lambda:navigate(PAGES[8]),lambda:navigate(PAGES[1]),st.session_state.get('pension_summary'))

elif page==PAGES[2]:
 st.subheader('💷 My money')
 st.caption('Illustrative numbers only — not personalised financial advice.')
 left,right=st.columns(2)
 with left:
  st.markdown('#### Monthly budget')
  income=ui.number_input('Monthly take-home income (£)',0,30000,2600,50)
  housing=ui.number_input('Housing and essential bills (£)',0,30000,1050,25)
  food=ui.number_input('Food and household (£)',0,10000,400,25)
  transport=ui.number_input('Transport (£)',0,10000,250,25)
  debts=ui.number_input('Debt repayments (£)',0,15000,300,25)
  leisure=ui.number_input('Leisure / other (£)',0,15000,250,25)
  surplus=income-housing-food-transport-debts-leisure
  st.metric('Illustrative monthly surplus',money(surplus))
  if surplus<0:st.error('Illustrative spending exceeds income.')
  elif surplus>0:st.success('This is your unallocated monthly amount, not guaranteed savings.')
 with right:
  st.markdown('#### Savings & investment scenarios')
  monthly=ui.slider('Monthly contribution (£)',0,1500,200,25)
  years=ui.slider('Years',1,35,15)
  annual=ui.slider('Illustrative annual return after fees (%)',0.,10.,5.,.5)
  inflation=ui.slider('Illustrative annual inflation (%)',0.,8.,2.5,.5)
  r=(1+annual/100)**(1/12)-1
  future=monthly*years*12 if r==0 else monthly*((1+r)**(years*12)-1)/r
  st.metric('Future nominal value',money(future))
  st.metric('In today’s money (inflation-adjusted)',money(future/(1+inflation/100)**years))
  st.caption(f'Your contributions: {money(monthly*12*years)}; projected growth: {money(future-monthly*12*years)}.')
 st.info('Market returns fluctuate and losses are possible. The model assumes steady returns, end-of-month contributions, no withdrawal and no taxes; it is not a pension forecast.')
 st.markdown('**Next:** See the official [Armed Forces pension calculator](https://www.gov.uk/armed-forces-pension-calculator) for service pension estimates.')

elif page==PAGES[3]:
 st.subheader('🎯 Entitlements explorer')
 st.caption('Existing scheme summaries are starting points, not verified entitlement decisions. Use Check this in policy for document evidence.')
 if p.get('accommodation_type') not in (None,'Not specified'):st.caption('Linked accommodation context: '+p['accommodation_type'])
 if p.get('posting')=='Upcoming assignment / move':st.info('Based on your profile: relocation/travel and accommodation guidance may be particularly relevant.')
 if p.get('family')=='Dependants / children' or p.get('dependent_count',0)>0:st.info('Based on your profile: consider family, childcare and education support. Eligibility is not established.')
 if p.get('posting')=='Upcoming assignment / move':
  st.button('Check posting allowances',on_click=ask_opportunity,args=('What allowances might apply when I move posting?',))
 situations=['All opportunities','Buying a home','Being posted / moving','Duty travel','Accommodation','Family','Leaving the Services']
 selected=ui.selectbox('What is happening in your life?',situations)
 shown=OPPORTUNITIES if selected=='All opportunities' else [x for x in OPPORTUNITIES if x['topic']==selected or (selected=='Being posted / moving' and 'posting' in x['keywords'])]
 for x in shown:
  with st.expander(x['name'],expanded=len(shown)<=2):
   st.write(x['summary'])
   st.caption('When to investigate: '+x['when'])
   st.write('**Existing policy pointer (not verified in this session):** '+x['policy'])
   st.write('**What to do next:** '+x['action'])
   st.link_button('Open official source',x['url'])
   if x['name']=='Forces Help to Buy':st.button('Start your home-buying guide',key='benefit_fhtb',on_click=open_fhtb,type='primary')
   else:st.button('Check this in policy',key='policy_'+x['name'],on_click=ask_opportunity,args=('What conditions apply to '+x['name']+'?',))
 st.warning('The app does not assess final eligibility, calculate claim values or submit claims. Confirm the current policy, application route and exceptions with authorised unit staff.')

elif page==PAGES[4]:
 st.subheader('🔎 Ask Forces HQ')
 if not st.session_state.get('profile_applied'):st.caption('Profile context is the example profile until you apply your own choices.')
 render_question(p,navigate,PAGES,open_fhtb)
 with st.expander('Browse official policy publications'):
  for source_id,(title,url) in CATALOGUE.items():st.link_button(source_id+' — '+title,url)

elif page==PAGES[5]:
 st.subheader('📅 Career & reporting milestones')
 st.caption(f'Profile appraisal type: {p["report"]}; recorded rank: {p["rank"]}.')
 if p.get('rank_history'):
  st.markdown('#### Linked promotion timeline')
  for h in p['rank_history']:st.write(f"• **{h['date']} — {h['rank']}**"+(f" ({h['note']})" if h.get('note') else ''))
 st.write('Enter dates you have independently confirmed. **There is no universal SJAR/OJAR or promotion window assumed here.**')
 with st.container(border=True):
  label=ui.selectbox('Milestone',['Objectives agreed','MPAR','SJAR / OJAR drafting','SJAR / OJAR submission','Promotion / board window (verify)','Course / qualification','Posting / assignment','Other'])
  due=ui.date_input('Your confirmed date',date.today()+timedelta(days=60))
  if st.button('Add milestone'):
   if due is None:st.error('Choose a confirmed date before adding a career milestone.')
   else:
    st.session_state.events.append({'label':label,'date':due})
    ui.clear('Milestone','Your confirmed date')
    rerun_with_retained_inputs()
 for i,event in enumerate(st.session_state.events):
  a,b=st.columns([5,1]);a.write(f"**{event['label']}** — {event['date']:%d %b %Y} ({(event['date']-date.today()).days} days)")
  if b.button('Remove',key=f'del{i}'):st.session_state.events.pop(i);rerun_with_retained_inputs()
 if not st.session_state.events:st.info('No personal milestones entered yet.')
 st.markdown('**Appraisal guidance:** Refer to your latest authorised JSP 757 and single-Service reporting instructions. For this demo, do not upload official reports.')

elif page==PAGES[6]:
 st.subheader('✍️ Achievement & appraisal preparation')
 st.warning('Use fictional, generic or non-sensitive examples only. Do not paste official reports, names, private personnel assessments or restricted material.')
 with st.container(border=True):
  action=ui.text_area('What did you do?',placeholder='e.g. Planned weekly training for 12 fictional team members')
  result=ui.text_area('What changed? Include evidence you could verify.',placeholder='e.g. Improved attendance from 75% to 95%')
  theme=ui.selectbox('Development theme',['Leadership','Delivery','Planning','Teamwork','Communication','Developing others','Other'])
  if st.button('Add practice achievement'):
   if action.strip() and result.strip():
    st.session_state.records.append({'action':action.strip(),'result':result.strip(),'theme':theme})
    ui.clear('What did you do?','What changed? Include evidence you could verify.','Development theme')
    rerun_with_retained_inputs()
   else:st.error('Please provide both the action and the result.')
 if st.session_state.records:
  mode=ui.radio('Output style',['SJAR / OJAR evidence','MPAR preparation','Promotion evidence'],horizontal=True)
  rendered=[]
  for i,e in enumerate(st.session_state.records,1):
   base=f"{e['action'].rstrip('.')} . Outcome: {e['result'].rstrip('.')} .".replace(' .','.')
   if mode=='SJAR / OJAR evidence':part=f"{i}. [{e['theme']}] {base}"
   elif mode=='MPAR preparation':part=f"{i}. Achievement: {e['action']}\n   Evidence / impact: {e['result']}\n   Discuss: What worked, what support is needed, and what objective follows?"
   else:part=f"{i}. Evidence theme: {e['theme']}\n   Contribution: {e['action']}\n   Impact: {e['result']}\n   Reflection: Which greater responsibilities does this genuinely evidence?"
   rendered.append(part)
  output='\n\n'.join(rendered)
  draft_key=ui.key('draft_'+mode)
  source_key='draft_source:'+mode
  if draft_key not in st.session_state or st.session_state[draft_key]==st.session_state.get(source_key):
   st.session_state[draft_key]=output
  st.session_state[source_key]=output
  if st.session_state[draft_key]!=output:st.caption('Your edits are preserved. Regenerate this draft to replace them with the latest practice examples.')
  if st.button('Regenerate this draft from practice examples',help='Replaces edits for the selected output style.'):
   st.session_state[draft_key]=output
  edited_output=ui.text_area('Editable draft — review all claims before use',height=230,key='draft_'+mode)
  st.download_button('Download practice draft',edited_output,file_name='forces_hq_practice_notes.txt',mime='text/plain')
  if st.button('Clear practice examples'):
   st.session_state.records=[]
   ui.clear(*('draft_'+style for style in ['SJAR / OJAR evidence','MPAR preparation','Promotion evidence']))
   rerun_with_retained_inputs()
  st.markdown('#### Evidence quality review')
  for e in st.session_state.records:
   st.write(f"**{e['theme']}** — "+ ('✅ Numbers included' if any(ch.isdigit() for ch in e['result']) else '⚠️ Consider adding verifiable measurements if available'))
   if len(e['action'].split())<8:st.write('⚠️ Consider explaining your individual contribution more clearly.')
 else:st.info('Add a fictional practice achievement above to generate three alternative structured outputs.')
 st.caption('This is a rule-based drafting assistant, not generative AI. It does not invent outcomes, assert promotion potential or access JPA.')

elif page==PAGES[7]:
 st.subheader('🏡 Military life & future')
 topic=ui.selectbox('What are you planning?',['Posting / relocation','Housing / buying','Family / education','Leaving / resettlement','Pension planning','Leave'])
 keys={'Posting / relocation':['JSP 752','JSP 464'],'Housing / buying':['JSP 464'],'Family / education':['Official MOD benefits','JSP 752'],'Leaving / resettlement':['JSP 534'],'Pension planning':['Pension calculator'],'Leave':['JSP 760']}
 st.write('**Official publication links — check the current edition:**')
 for entry in POLICIES:
  if entry['id'] in keys[topic]:policy_link(entry)
 st.markdown('**Suggested checklist:** Check current eligibility → confirm with authorised staff → plan timings → retain only the appropriate records in approved systems.')
 st.info('Future versions may add guided journeys and opt-in reminders; neither is active in V0.8.')

elif page==PAGES[8]:
 st.subheader('🏦 Armed Forces pension planning')
 st.write('Understand your pension options using verified pay-table entries and official-quote Added Pension scenarios. This is educational: NOT a personal pension statement, entitlement or purchase quotation.')
 st.markdown('#### 1. Pensionable pay and career forecast (beta)')
 if p.get('join_date'):st.caption(f"Linked test enlistment date: {p['join_date']:%d %b %Y}. Service breaks and qualifying years remain unverified.")
 if p.get('pension_schemes') and p['pension_schemes']!=['Not sure']:st.info('Self-reported scheme history: '+', '.join(p['pension_schemes'])+'. This does not confirm legacy benefits or remedy options; check your official record.')
 if p.get('rank_history'):st.caption(f"{len(p['rank_history'])} profile promotion records captured; no historical pay reconstruction is performed in this beta.")
 if p.get('salary_verified') and p.get('verified_pensionable_salary'):st.success(f'Linked profile: verified-by-user pensionable earnings of {money(p["verified_pensionable_salary"])} per year (not independently verified by Forces HQ).')
 if p.get('transfer_history')!='None / not recorded':st.warning('Your profile indicates a change or break in service: this simple future AFPS 15 accrual model cannot account for your complete history.')
 if p.get('added_pension')=='Purchased / active contract':st.info('Added Pension recorded in profile. This beta excludes accrued Added Pension; use an official scheme statement/quote.')
 with st.expander('OR7 comparison — existing 2026 source extract',expanded=False):
  st.caption('Existing limited extract, not independently source-verified during this repair, from the 2026 Armed Forces Pay Review Body, Appendix 1, Tables 1.1–1.3. Annual salary figures INCLUDE X-Factor. These are recommended 1 April 2026 rates, not a live JPA payslip or proof of pensionable earnings. Check that the rates were implemented and apply to your personal situation.')
  a,b=st.columns(2)
  with a: band=ui.selectbox('Trade supplement', [1,2,3],index=([1,2,3].index(p['pay_supplement']) if p.get('pay_supplement') in [1,2,3] else 0),key='pay_band_lookup')
  with b: point=ui.selectbox('OR7 increment level',list(range(1,13)),index=(p['pay_increment']-1 if p.get('pay_increment') in range(1,13) else 0),key='pay_inc_lookup')
  tabular=PAY_2026_OR7[band][point]
  st.metric('2026 published annual salary (including X-Factor)',money(tabular))
  if p.get('rank')!='Staff Sergeant':st.warning('Your linked rank is not Staff Sergeant. This OR7 table is provided for comparison only, not as your personal salary.')
  elif p.get('pay_supplement') in PAY_2026_OR7 and p.get('pay_increment') in PAY_2026_OR7[p['pay_supplement']]:st.caption('The pay-table selector is prefilled from your profile; values can be changed here for comparison.')
  st.caption('Special Forces, RRP, bespoke pay and other additional payments are NOT added automatically. Their pensionability must be confirmed under the relevant scheme rules.')
  st.link_button('View official 2026 pay report',AFPRB_2026_URL)
  if st.button('Use this pay figure in the AFPS 15 scenario',key='use_pay_v05'):
   st.session_state['v05_salary']=float(tabular)
   st.session_state[ui.key('pension_annual')]=float(tabular)
   st.session_state.pop('pension_result',None)
   st.success('Pay figure selected for this browser session. Confirm your pensionable earnings before modelling.')
 st.info('For other ranks, officers, Supplement 4, bespoke pay spines or historic rates: use the verified pensionable amount from your statement instead. We will not fabricate missing tables.')
 st.info('Start with **pensionable annual salary**, not total take-home pay. The pay table uses trade supplements and increment points. Specialist or other extra payments count only where officially classified as pensionable. This beta projects **AFPS 15 future accrual only**; it does not reconstruct AFPS 05, McCloud, EDP or your existing accumulated pension.')
 if p.get('salary_verified') and p.get('verified_pensionable_salary'):
  if st.button('Use linked profile earnings in this scenario'):
   st.session_state[ui.key('pension_annual')]=float(p['verified_pensionable_salary'])
   st.session_state.pop('pension_result',None)
 if p.get('join_date') or p.get('planned_exit'):
  st.caption(f"Linked service dates: {p.get('join_date') or 'unknown'} → {p.get('planned_exit') or 'unknown'}. Calendar dates do not establish qualifying service.")
 if p.get('planned_exit') and 1 <= (p['planned_exit']-date.today()).days//365 <= 30:
  if st.button('Use complete calendar years to planned exit as scenario horizon'):
   st.session_state[ui.key('More years of AFPS 15 accrual to model')]=(p['planned_exit']-date.today()).days//365
   st.session_state.pop('pension_result',None)
 st.caption('Scenario inputs are retained separately from your profile. You can edit them or explicitly copy linked profile earnings or a comparison pay figure.')
 with st.expander('Why do pay bands and specialist payments matter?',expanded=False):
  st.write('Other Ranks pay varies by rank, trade supplement and increment level. Some groups use bespoke pay spines. The MOD 2026 pay review has pay tables that include X-Factor for the applicable main scales. Do not add X-Factor a second time if it is already included.')
  st.write('Recruitment and Retention Pay, temporary duty additions and many allowances are excluded from pensionable earnings unless specifically deemed pensionable by the Scheme manager. An SF-related payment cannot be treated as pensionable merely because it appears on a payslip.')
  st.link_button('2026 AFPRB pay report (pay tables)', 'https://assets.publishing.service.gov.uk/media/6a27f8383b15d05a7ce31f52/AFPRB_55th_Report_2026.pdf')
  st.link_button('JSP 905: AFPS 15 rules', 'https://www.gov.uk/government/publications/armed-forces-pension-scheme-2015-and-early-departure-payments-scheme-2015-jsp-905-part-one')
  st.link_button('MOD pay explanation','https://discovermybenefits.mod.gov.uk/army/your-pay-and-pension/annual-salary/')
 with st.container(border=True):
  c1,c2=st.columns(2)
  with c1:
   pay_category=ui.selectbox('Pay category',['Other Ranks main scale','Officer scale','Bespoke / specialist spine','Other / not sure'])
   supplement=ui.selectbox('Trade supplement (where applicable)',['Not sure / not applicable','Supplement 1','Supplement 2','Supplement 3','Supplement 4'])
   increment=ui.number_input('Pay increment / level',1,20,1)
   annual=ui.number_input('Current annual pensionable salary (£) — check payslip',min_value=0.0,max_value=300000.0,value=float(p['verified_pensionable_salary'] if p.get('salary_verified') and p.get('verified_pensionable_salary') else st.session_state.get('v05_salary',0.0)),step=100.0,key='pension_annual',help='Enter the pensionable salary amount confirmed by official payslip / pay statement. Include X-Factor if already in salary.')
  with c2:
   special=ui.selectbox('Specialist / SF / RRP payment',['None','Specialist / bespoke pay spine','Special Forces-related pay','Recruitment & Retention Pay','Other supplement'])
   add=ui.number_input('Other ANNUAL payment confirmed pensionable by official documentation (£)',min_value=0.0,max_value=100000.0,value=0.0,step=100.0)
   confirmed=ui.checkbox('I have verified that the additional payment above is pensionable (or it is zero)',value=False)
   horizon=ui.slider('More years of AFPS 15 accrual to model',1,30,10)
  c3,c4=st.columns(2)
  with c3: pay_growth=ui.slider('Illustrative annual rise in pensionable salary (%)',0.0,6.0,2.0,0.5)
  with c4: revalue=ui.slider('Illustrative active-service revaluation (%)',0.0,6.0,2.0,0.5)
  done=st.button('Calculate future AFPS 15 accrual',use_container_width=True)
 if done:
  if annual<=0:st.warning('Enter a verified pensionable annual salary. A rank and supplement alone are not enough to establish the correct figure.')
  elif not confirmed:st.warning('Confirm additional payment pensionability first, or enter £0 and tick the checkbox to exclude it.')
  else:
   st.session_state.pension_result=(annual,add,horizon,pay_growth,revalue,special)
 if st.session_state.get('pension_result'):
  result_annual,result_add,result_horizon,result_growth,result_revalue,result_special=st.session_state.pension_result
  st.caption(f'Last calculated inputs: annual earnings {money(result_annual)}, additional pensionable payment {money(result_add)}, {result_horizon} future years, salary rise {result_growth:g}% and active revaluation {result_revalue:g}%.')
  if not confirmed or (annual,add,horizon,pay_growth,revalue,special)!=st.session_state.pension_result:
   st.info('Inputs have changed. The results below show your last calculated scenario; select Calculate to update them.')
  pensionable=result_annual+result_add
  cumulative=0.0
  for yr in range(result_horizon):
   cumulative=cumulative*(1+result_revalue/100)+pensionable*((1+result_growth/100)**yr)/47
  st.session_state.pension_summary={'annual_pension':cumulative}
  with st.container(border=True):
   st.metric('NEW annual AFPS 15 pension entitlement accrued during first modelled year',money(pensionable/47)+' gross pension per year from scheme pension age')
   st.metric('Combined new annual AFPS 15 pension entitlement from ONLY the future modelled years',money(cumulative)+' gross pension per year from scheme pension age')
   st.caption('This is the modelled future AFPS 15 accrual only, not your total pension or an amount payable on leaving. Assumes full-year pensionable earnings, constant salary-growth and active revaluation assumptions, no breaks or flexible-service adjustment. Past accrual, legacy schemes, retirement timing, post-service uprating, EDP and tax are excluded. Your future earnings and rates will vary.')
  if result_special!='None':st.warning('Specialist pay selected: ensure the amount is incorporated in the pensionable salary or confirmed as pensionable before relying on this scenario. Some specialist/temporary payments are excluded.')
 st.divider()
 st.markdown('#### 2. Get your official full-service pension forecast')

 st.link_button('Official Armed Forces pension calculator', 'https://www.gov.uk/armed-forces-pension-calculator')
 st.caption('Your exact benefits can depend on legacy service, AFPS 05/15, the 2015 Remedy, service dates and other factors. Use official figures, not guessed accrual.')
 st.divider()
 with st.expander('Added Pension quotes and guidance'):
  st.markdown('#### 3. Understand purchasing Added Pension')
  st.write('AFPS 15 members may be able to buy additional annual pension through an Added Pension contract. There are member-only and member-and-dependants options. Official pricing uses actuarial factors and scheme rules. A quotation can be requested with **Form 6**; a separate **Form 6A** covers purchasing or cancelling.')
  st.link_button('Official Added Pension forms (6 / 6A)', 'https://www.gov.uk/guidance/veterans-uk-armed-forces-pensions-forms')
  st.link_button('Official pensions guidance and Added Pension tools', 'https://www.gov.uk/guidance/pensions-and-compensation-for-veterans')
  st.divider()
  st.markdown('#### 4. Explore an official-quote scenario')
  st.write('Only enter figures from an **actual official quote**, or choose the fictional demo. We do **not** convert a £200/month contribution into guaranteed extra pension without a quote.')
  demo=ui.checkbox('Use fictional demonstration figures',value=True)
  if demo:
   cost=ui.number_input('Fictional one-off contract cost (£)',100,100000,6000,100,disabled=True)
   extra=ui.number_input('Fictional extra gross annual pension at payment (£)',10,20000,420,10,disabled=True)
  else:
   cost=ui.number_input('Cost of Added Pension contract from your quote (£)',0,1000000,0,100)
   extra=ui.number_input('Extra gross annual pension from your quote (£)',0,100000,0,10)
  years=ui.slider('Illustrative number of years in payment',1,40,20)
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
st.caption('Forces HQ • Independent educational app · Not an official MOD service')
retain_hidden_inputs()
