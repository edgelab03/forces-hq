"""Modern Forces presentation only. All actions delegate to existing routes."""
from pathlib import Path
from datetime import date
import streamlit as st
from benefit_ui import render_benefit_card
from decision_engine import benefit_result, verified_profile_facts
from policy_engine import PolicyIndex


def apply_styles():
    st.markdown('<style>'+Path(__file__).with_name('modern_ui.css').read_text()+'</style>',unsafe_allow_html=True)


def brand():
    st.markdown('''<div class="mf-brand"><span class="mf-mark" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M7 19V5h11M7 11h8" stroke="#25483E" stroke-width="2.2" stroke-linecap="round"/><path d="M17 15v4" stroke="#C89B48" stroke-width="2.2" stroke-linecap="round"/></svg></span><div><div class="mf-wordmark">Forces HQ</div><div class="mf-tagline">Your service. Simplified.</div></div></div>''',unsafe_allow_html=True)


def render_home(profile,applied,benefits,events,*,ask,open_money,open_housing,open_pension,open_learning,open_career):
    with st.container(key='welcome'):
        st.subheader('Welcome back' if applied else 'Make your next move')
        if applied:st.caption(profile['rank']+' · '+profile['service'])
        st.write('Ask, plan and take your next step.')
    with st.container(key='ask_panel'):
        st.markdown('### Ask Forces HQ')
        st.caption('What can I help you with?')
        if 'home_question' not in st.session_state:st.session_state.home_question=st.session_state.get('active_question') or ''
        with st.container(horizontal=True,wrap=False,key='ask_entry'):
            st.text_input('Ask Forces HQ',key='home_question',placeholder='Ask about your service…',label_visibility='collapsed',on_change=ask)
            st.button('Voice input unavailable',icon=':material/mic_off:',disabled=True,key='voice_unavailable',help='Voice input is not available in this version.')
            st.button('Open Ask',icon=':material/arrow_forward:',on_click=ask,key='home_ask',help='Open Ask with your question')
    st.markdown('### Quick access')
    with st.container(key='dashboard'):
        cards=[('Your pay',':material/account_balance_wallet:',open_money),('Housing',':material/home:',open_housing),('Pension',':material/account_balance:',open_pension),('Learning',':material/school:',open_learning)]
        for start in (0,2):
            for col,(label,icon,action) in zip(st.columns(2,gap='small'),cards[start:start+2]):
                with col:st.button(label,icon=icon,on_click=action,key='dashboard_'+label,use_container_width=True)
    # Reuse the existing decision result; never add a visual-only eligibility rule.
    progress=benefits['fhtb']
    recommendation=None
    if applied or progress['interested'] or progress['completed']:
        recommendation=benefit_result('fhtb',verified_profile_facts(profile,applied)|progress['facts'],PolicyIndex(),progress)
    if progress['completed'] or (applied and not progress['interested'] and recommendation['status']!='Policy verification required'):
        render_benefit_card(profile,applied,progress,open_housing)
    relevant=[e for e in events if str(e['date'])>=date.today().isoformat()]
    if progress['interested'] and not progress['completed']:
        with st.container(border=True,key='next_step'):
            st.caption('YOUR NEXT STEP')
            st.markdown('**Your home-buying plan**')
            st.write(progress['step']+' · Pick up where you left off.')
            st.caption(recommendation['status']+' · You chose a home-buying goal.')
            st.button('Continue your plan',icon=':material/arrow_forward:',on_click=open_housing,key='resume_journey',use_container_width=True)
    elif relevant:
        milestone=min(relevant,key=lambda e:str(e['date']))
        with st.container(border=True,key='next_step'):
            st.caption('COMING UP')
            st.markdown('**'+milestone['label']+'**')
            st.caption(str(milestone['date']))
            st.button('View career milestones',icon=':material/arrow_forward:',on_click=open_career,key='next_career')
