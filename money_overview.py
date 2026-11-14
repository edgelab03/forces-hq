"""Useful saved-profile information before dedicated modelling screens."""
from datetime import date
import streamlit as st


def render_money_overview(profile,applied,open_budget,open_model,open_profile,summary=None):
 st.subheader('Your money, at a glance')
 if applied and profile.get('salary_verified') and profile.get('verified_pensionable_salary'):
  annual=float(profile['verified_pensionable_salary'])
  with st.container(border=True):
   st.caption('USER-CHECKED ANNUAL PENSIONABLE EARNINGS')
   st.markdown(f'### £{annual:,.0f}')
   st.write(f'£{annual/12:,.2f} per month, gross equivalent')
   st.caption('Annual earnings ÷ 12. Not take-home pay; tax, deductions and allowances are excluded. Not independently checked against a live pay source.')
 else:
  st.info('Add earnings you have checked against your statement to see a gross-pay overview. Rank alone is not enough to calculate your salary.')
  st.button('Update earnings in Profile',on_click=open_profile,key='overview_profile')
 schemes=profile.get('pension_schemes',[]) if applied else []
 st.markdown('**Pension scheme**')
 st.write(', '.join(schemes) if schemes and schemes!=['Not sure'] else 'Not yet confirmed')
 if applied and profile.get('join_date'):
  st.caption('Entered enlistment date: '+str(profile['join_date'])+' · Calendar dates do not establish qualifying service')
 if applied and profile.get('planned_exit'):st.caption('Your planned exit: '+str(profile['planned_exit']))
 if summary:
  st.markdown('**Your last AFPS 15 future-accrual scenario**')
  st.write(f"£{summary['annual_pension']:,.0f} new gross annual pension from the modelled years only")
  st.caption('Saved scenario assumptions, not total pension, EDP or an amount payable on leaving.')
 with st.container(horizontal=True):
  st.button('Edit budget & savings',on_click=open_budget,key='overview_budget',use_container_width=True)
  st.button('Model pay & pension',on_click=open_model,key='overview_pension',use_container_width=True)
 st.caption('AFPS 05 reconstruction and EDP calculation were not implemented in the inherited app. Those missing calculations are not replaced with guessed formulas.')
