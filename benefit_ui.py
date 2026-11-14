"""A single connected FHTB planning flow with explicit evidence gates."""
import streamlit as st
from session_inputs import SessionInputs, rerun_with_retained_inputs
from benefit_journeys import empty_progress, STEPS, TASKS, TAX_LINKS, FHTB_URL, JSP464_URL, JSP752_URL
from decision_engine import assess, verified_profile_facts, advance_limit, repayment_estimate, purchase_budget, UNVERIFIED, benefit_result
from policy_engine import PolicyIndex


def render_proofs(result):
 if not result['evidence']:
  st.warning('No reviewed, current primary-source rule is available. Exact scheme restrictions, amounts, deadlines and JPA instructions cannot be verified here.')
  st.link_button('Official Forces Help to Buy guidance',FHTB_URL)
  return
 rule=result['rule']
 st.caption('Rule '+rule['id']+' · '+rule['version']+' · Effective '+rule['effective_from']+' · Reviewed '+rule['reviewed_on'])
 for proof in result['evidence']:
  st.markdown('**'+proof['source_id']+' — '+proof['title']+'**')
  st.caption(' · '.join([proof['document_version'],proof['chapter'],proof['section'],'paragraph '+proof['paragraph']]))
  st.write(proof['quote'])
  st.link_button('Read exact source provision',proof['url']+'#page='+str(proof['page']))
 for restriction in rule.get('exceptions',[]):st.write('Restriction: '+restriction)


def render_condition(condition, ui, facts, on_answer=None):
 """One necessary missing condition at a time; answers remain in SessionInputs."""
 key=condition['fact']
 kind=condition.get('input_type','choice')
 st.session_state.setdefault('condition_types',{})[ui.key('condition:'+key)]=kind
 if kind=='date':
  value=ui.date_input(condition['question'],value=None,key='condition:'+key)
  if value is not None:value=value.isoformat()
 elif kind=='number':
  value=ui.number_input(condition['question'],min_value=0.0,max_value=1000000.0,value=None,key='condition:'+key)
 else:
  options=['Not sure']+[x for x in condition['options'] if x!='Not sure']
  value=ui.radio(condition['question'],options,key='condition:'+key)
 if value not in ('Not sure',None):
  facts[key]={'value':value,'provenance':'user_confirmed'}
  if on_answer:on_answer()
  rerun_with_retained_inputs()


def render_benefit_card(profile,applied,progress,open_journey):
 state=benefit_result('fhtb',verified_profile_facts(profile,applied)|progress['facts'],PolicyIndex(),progress)
 if state['completed']:
  with st.expander('Completed journeys'):
   st.caption('Forces Help to Buy · User-confirmed completed')
   st.button('Revisit home-buying plan',on_click=open_journey,key='revisit_fhtb')
  return
 if not progress['interested'] and (not applied or state['status']=='Policy verification required'):
  st.caption('Personalised benefit recommendations need your applied profile and reviewed policy rules.')
  return
 with st.container(border=True,key='benefit_summary'):
  st.markdown('**Your home-buying plan**')
  st.caption(state['status'])
  st.caption('Suggested because you selected a home-buying goal.' if progress['interested'] else 'Available guided journey. Your profile alone does not establish eligibility.')
  st.button('Plan a home purchase',on_click=open_journey,use_container_width=True,key='open_fhtb_home')


def render_fhtb(profile,applied,open_policy,close_journey,open_profile):
 progress=st.session_state.setdefault('benefits',{}).setdefault('fhtb',empty_progress())
 ui=SessionInputs('journey:fhtb')
 st.button('← Back to benefits',on_click=close_journey,key='leave_fhtb')
 st.subheader('Your home-buying plan')
 step=progress['step'];number=STEPS.index(step)
 st.caption(f'{number+1} of {len(STEPS)} · {step}')
 st.progress((number+1)/len(STEPS))
 facts=verified_profile_facts(profile,applied)|progress['facts']
 result=assess('fhtb',facts,PolicyIndex())
 if step=='Start':
  st.markdown('### A route to plan your purchase')
  st.write('Forces Help to Buy is a MOD home-buying scheme. This guide connects your assessment, purchase budget, preparation and saved progress.')
  st.caption('It cannot submit a JPA application, retrieve service records or monitor official approval.')
  progress['interested']=ui.checkbox('I want to plan a home purchase',value=progress['interested'],key='interested')
  st.info(result['status'])
  st.write(result['reason'])
  st.caption('Scheme values and restrictions will appear only when a current reviewed rule pack is available.')
  st.link_button('Read the official scheme overview',FHTB_URL)
 elif step=='Assess':
  st.markdown('### What applies to you?')
  st.info(result['status'])
  st.write(result['reason'])
  if not applied:st.caption('The example profile is excluded from eligibility decisions. Apply your profile first to reuse its fields.')
  if result['missing']:render_condition(result['missing'][0],ui,progress['facts'])
  if result['trace']:
   with st.expander('How the conditions were evaluated'):
    for item in result['trace']:st.write(('✓ ' if item['passed'] else '✕ ')+item['reason'])
  with st.expander('Exact policy, exceptions and review dates'):render_proofs(result)
  st.button('Ask a related housing question',on_click=open_policy,args=('Forces Help to Buy eligibility for a home purchase',),key='fhtb_ask')
 elif step=='Budget':
  st.markdown('### Build a purchase budget')
  salary_key=(result.get('rule') or {}).get('financials',{}).get('salary_fact')
  salary_fact=facts.get(salary_key,{})
  maximum=advance_limit(salary_fact.get('value'),result) if salary_fact.get('provenance') in ('user_confirmed','document_checked') else None
  if maximum is not None:st.metric('Potential scheme maximum under the reviewed rule',f'£{maximum:,.2f}')
  else:st.caption('FHTB maximum unavailable: verified scheme terms and applicable salary are required. Proposed advance below is your assumption, not an award.')
  values=progress['budget']
  labels={'price':'Property price (£)','deposit':'Your cash deposit (£)','advance':'Proposed advance — assumption (£)','mortgage':'Proposed mortgage (£)','tax':'Tax quote / external calculation (£)','legal':'Solicitor / conveyancing quote (£)','survey':'Survey estimate (£)','searches':'Searches estimate (£)','registration':'Registration / Land Registry estimate (£)','other':'Other purchase costs (£)'}
  for key in labels:values.setdefault(key,0.0)
  budget=purchase_budget(**{key:values[key] for key in labels})
  if values['price']:
   st.metric('Purchase costs and price',f"£{budget['total_cost']:,.0f}")
   st.metric('Funding gap',f"£{budget['shortfall']:,.0f}")
  else:st.info('Add a property price and your proposed funding to see a purchase budget. No property values are assumed.')
  if st.button('Edit purchase figures',key='fhtb_edit_budget_button'):st.session_state.fhtb_edit_budget=True
  if st.session_state.get('fhtb_edit_budget'):
   with st.form('purchase_figures'):
    for key in ('price','deposit','advance','mortgage'):
     values[key]=ui.number_input(labels[key],min_value=0.0,max_value=10000000.0,value=float(values[key]),step=100.0,key='budget:'+key)
    with st.expander('Tax, legal and other costs'):
     for key in ('tax','legal','survey','searches','registration','other'):
      values[key]=ui.number_input(labels[key],min_value=0.0,max_value=10000000.0,value=float(values[key]),step=100.0,key='budget:'+key)
    if st.form_submit_button('Save purchase figures'):
     st.session_state.fhtb_edit_budget=False
     rerun_with_retained_inputs()
  progress['nation']=ui.radio('Where is the property?',list(TAX_LINKS),index=list(TAX_LINKS).index(progress['nation']),key='nation')
  tax_title,tax_url=TAX_LINKS[progress['nation']]
  st.link_button(tax_title,tax_url)
  st.caption('Use a current official tax calculation or professional quote. No tax rates or relief are assumed; buyer, residence and additional-property circumstances matter.')
  st.caption('Keep cash deposit and proposed advance separate to avoid counting funding twice.')
  if values['advance'] or values['mortgage']:
   with st.expander('Repayment and affordability assumptions'):
    values['years']=ui.number_input('Illustrative repayment period (years)',min_value=1,max_value=40,value=int(values.get('years',10)),key='budget:years')
    values['mortgage_rate']=ui.number_input('Illustrative mortgage annual rate (%)',min_value=0.0,max_value=30.0,value=float(values.get('mortgage_rate',5)),step=.25,key='budget:mortgage_rate')
    st.metric('Advance cashflow at assumed 0% interest',f"£{repayment_estimate(values['advance'],values['years']):,.2f} / month")
    st.metric('Mortgage repayment illustration',f"£{repayment_estimate(values['mortgage'],values['years'],values['mortgage_rate']):,.2f} / month")
    st.caption('Generic cashflow, not verified FHTB terms, benefit-in-kind tax treatment or mortgage affordability approval. Confirm terms, fees and acceptance of an advance with your lender.')
 elif step=='Prepare':
  st.markdown('### Prepare your application')
  if result['claim_steps']:
   for idx,item in enumerate(result['claim_steps'],1):
    st.write(f"{idx}. {item['text']}")
    if item.get('url'):st.link_button('Open verified application resource',item['url'])
  else:
   st.warning('The exact JPA process, current forms, deadlines and approval/legal sequence are not verified. These planning tasks are not official application instructions.')
  st.write('Ask unit admin for the authorised route and timing; ask the lender and solicitor to confirm their requirements before committing funds.')
  st.link_button('Official FHTB guidance and application signposting',FHTB_URL)
  with st.expander('Refund of Legal Expenses — separate assessment'):
   st.write('FHTB eligibility does not establish entitlement to Refund of Legal Expenses (New Buyer). No refund is assumed or deducted from this budget.')
   st.button('Check legal-expense circumstances separately',on_click=open_policy,args=('Refund of Legal Expenses New Buyer eligibility and restrictions',),key='fhtb_rle')
   st.link_button('Official expenses publication',JSP752_URL)
  with st.expander('Policy evidence and scheme restrictions'):render_proofs(result)
 else:
  st.markdown('### Your preparation checklist')
  st.caption('User-confirmed progress only. These tasks do not imply MOD approval or official application tracking.')
  for key,label in TASKS.items():progress['checklist'][key]=ui.checkbox(label,value=progress['checklist'].get(key,False),key='task:'+key)
  progress['completed']=ui.checkbox('I have already claimed or completed this journey',value=progress['completed'],key='completed')
  if progress['completed']:st.success('Recorded as completed. It will no longer be promoted on Home.')
  st.caption('Progress is retained in this session. Download the encrypted profile from Profile to keep it between sessions; restore that file when returning.')
  st.button('Open profile saving',on_click=open_profile,key='fhtb_save')
 with st.container(horizontal=True,key='journey_controls'):
  if number>0:
   if st.button('Previous',key='fhtb_previous'):progress['step']=STEPS[number-1];rerun_with_retained_inputs()
  if number<len(STEPS)-1:
   if st.button('Continue',key='fhtb_continue',type='primary',disabled=bool(step=='Budget' and st.session_state.get('fhtb_edit_budget'))):progress['step']=STEPS[number+1];rerun_with_retained_inputs()
