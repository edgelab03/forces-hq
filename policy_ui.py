"""ASK → ASSESS → EXPLAIN → EVIDENCE → ACT, with source-gated decisions."""
import streamlit as st
from policy_engine import PolicyIndex, INTENTS, CATALOGUE, classify
from decision_engine import assess, verified_profile_facts, ELIGIBLE, INELIGIBLE, MORE, UNVERIFIED, facts_from_question
from benefit_ui import render_condition
from session_inputs import SessionInputs


def _retain_invalid_cache(path, value):
 """Keep old cache values in this session; never upgrade them to verified facts."""
 recovery=st.session_state.get('_policy_cache_recovery')
 if not isinstance(recovery,dict):
  recovery={}
  st.session_state['_policy_cache_recovery']=recovery
 recovery[path]=value


def _cache_mapping(parent,key,path):
 value=parent.get(key)
 if isinstance(value,dict):return value
 if key in parent:_retain_invalid_cache(path,value)
 parent[key]={}
 return parent[key]


def _cached_facts(parent,key,path):
 facts=_cache_mapping(parent,key,path)
 for name,record in list(facts.items()):
  if not isinstance(name,str) or not isinstance(record,dict) or 'value' not in record:
   _retain_invalid_cache(path+'.'+str(name),record)
   del facts[name]
 return facts


def render_question(profile,navigate,pages,open_benefit=None):
 ui=SessionInputs(pages[4]);index=PolicyIndex()
 if ui.key('guided_search') not in st.session_state:st.session_state[ui.key('guided_search')]=st.session_state.get('active_question') or ''
 question=ui.text_input('What do you need help with?',placeholder='Can I claim my lunch back yesterday?',key='guided_search',max_chars=1500) or ''
 st.session_state.active_question=question
 if not question.strip():
  st.caption('Ask about a meal, mileage, buying a home, pay or career support.')
  return
 st.session_state.active_question=question
 category=classify(question);topic=INTENTS.get(category,{})
 applied=st.session_state.get('profile_applied',False)
 st.caption(profile['service']+' · '+profile['rank']+' · User-confirmed profile' if applied else 'Example profile excluded from eligibility assessment')
 topics=_cache_mapping(st.session_state,'decision_facts','decision_facts')
 stored=_cached_facts(topics,category or 'unknown','decision_facts.'+str(category or 'unknown'))
 if category=='fhtb':stored=_cached_facts(st.session_state.benefits['fhtb'],'facts','benefits.fhtb.facts')
 signatures=_cache_mapping(st.session_state,'assessment_questions','assessment_questions')
 condition_types=_cache_mapping(st.session_state,'condition_types','condition_types')
 if signatures.get(category)!=question:
  derived=facts_from_question(category,question)
  date_key=str(category)+'.incident_date'
  if date_key in derived and date_key in stored and derived[date_key]['value']!=stored[date_key]['value']:
   stored.clear()
   for key,kind in condition_types.items():
    if key.startswith(ui.key('condition:')):st.session_state[key]='Not sure' if kind=='choice' else None
  stored.update(derived)
  signatures[category]=question
 result=assess(category,verified_profile_facts(profile,applied)|stored,index)
 st.subheader(topic.get('label','Your question'))
 with st.container(border=True,key='assessment_result'):
  st.markdown('**'+result['status']+'**')
  st.write(result['reason'])
  st.caption('Preliminary assessment from stated circumstances; not an authoritative determination.')
 if result['missing']:
  st.caption('One detail to continue')
  render_condition(result['missing'][0],ui,stored)
 if category in ('fhtb','rle') and open_benefit:
  st.button('Continue your home-buying guide',on_click=open_benefit,key='ask_fhtb',type='primary',use_container_width=True)
 else:
  related={'meals':(3,'Explore claim support'),'mileage':(3,'Explore claim support'),'edp':(8,'Open pension modelling'),'housing':(3,'Explore housing support'),'career':(5,'Open career milestones')}
  if category in related:
   target,label=related[category];st.button(label,on_click=navigate,args=(pages[target],),key='assessment_action',use_container_width=True)
 if result['status']==UNVERIFIED:
  st.caption('The next step is source verification. Supplying more yes/no answers cannot replace missing policy evidence.')
 with st.expander('Evidence, exceptions and reasoning'):
  if result['evidence']:
   rule=result['rule'];st.caption('Rule '+rule['id']+' · '+rule['version']+' · Effective '+rule['effective_from']+' · Reviewed '+rule['reviewed_on'])
   for proof in result['evidence']:
    st.markdown('**'+proof['source_id']+' — '+proof['title']+'**')
    st.caption(proof['document_version']+' · '+proof['chapter']+' · '+proof['section']+' · paragraph '+proof['paragraph'])
    st.write(proof['quote'])
    st.link_button('Open exact supporting provision',proof['url']+'#page='+str(proof['page']))
   for exception in rule.get('exceptions',[]):st.write('Restriction: '+exception)
   for item in result['trace']:st.write(('Satisfied: ' if item['passed'] else 'Not satisfied: ')+item['fact'])
  else:
   st.warning('Source unavailable for a verified decision: no approved current rule has matching primary-source evidence. No paragraph, quotation or eligibility ruling is invented.')
   hits=index.search(question)
   if hits:st.caption('Retrieved passages below have not been reviewed as eligibility rules.')
   for hit in hits:
    st.write(hit['text'][:500])
    st.caption(hit['source_id']+' · '+(hit['paragraph'] or 'Unnumbered passage')+' · Retrieved '+hit['retrieved_at'][:10])
    st.link_button('Read retrieved passage at its PDF page',hit['url']+'#page='+str(hit['page']))
   for source_id in topic.get('sources',[]):
    if source_id in CATALOGUE:st.link_button('Official publication — '+source_id,CATALOGUE[source_id][1])
  if stored:
   st.caption('Your retained answers')
   for key,value in stored.items():st.write(key+': '+str(value['value']))
   def reset_answers():
    stored.clear()
    signatures.pop(category,None)
    for key,kind in condition_types.items():
     if key.startswith(ui.key('condition:')):st.session_state[key]='Not sure' if kind=='choice' else None
   st.button('Change my answers',key='reset_decision_answers',on_click=reset_answers)
  st.caption('Deterministic assessment and local document retrieval. No official service-record or JPA integration.')
 if result['claim_steps']:
  with st.expander('Verified application process'):
   for step in result['claim_steps']:
    st.write(step['text'])
    if step.get('url'):st.link_button('Open application resource',step['url'])
