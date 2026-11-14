from datetime import date
from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest
from ui_helpers import select_primary
from ui_navigation import transition, back

APP=Path(__file__).resolve().parents[1]/'app.py'

class ModernRoutes(unittest.TestCase):
 def setUp(self):self.app=AppTest.from_file(str(APP),default_timeout=30).run()
 def test_five_native_buttons_replace_main_navigation_radio(self):
  self.assertFalse(any(r.label=='Primary navigation' for r in self.app.radio))
  for tab,target in [('Ask','📚 JSP finder'),('Money','💷 My money'),('Explore','🎯 Entitlements'),('Me','🎖️ My profile'),('Home','🏠 Dashboard')]:
   select_primary(self.app,tab);self.assertFalse(self.app.exception);self.assertEqual(self.app.session_state.nav_page,target)
 def test_enter_question_handoff_and_app_back_keep_text(self):
  next(w for w in self.app.text_input if w.label=='Ask Forces HQ').input('Can I claim lunch yesterday?').run()
  self.assertEqual(self.app.session_state.nav_page,'📚 JSP finder')
  self.assertEqual(next(w.value for w in self.app.text_input if w.label=='What do you need help with?'),'Can I claim lunch yesterday?')
  self.app.button(key='route_back').click().run();self.assertFalse(self.app.exception)
  self.assertEqual(self.app.session_state.nav_page,'🏠 Dashboard')
  self.assertEqual(next(w.value for w in self.app.text_input if w.label=='Ask Forces HQ'),'Can I claim lunch yesterday?')
 def test_profile_icon_and_learning_return_to_previous_screen(self):
  self.app.button(key='profile_button').click().run();self.assertEqual(self.app.session_state.nav_primary,'Me')
  self.app.button(key='route_back').click().run()
  self.app.button(key='dashboard_Learning').click().run();self.assertTrue(self.app.session_state.learning_focus)
  self.assertTrue(any(h.value=='Learning & development' for h in self.app.subheader))
  self.assertIn('Course / qualification',next(w.options for w in self.app.selectbox if w.label=='Milestone'))
  self.app.button(key='route_back').click().run();self.assertEqual(self.app.session_state.nav_primary,'Home')
 def test_next_step_has_no_empty_placeholder_and_uses_saved_milestone(self):
  self.assertFalse(any(w.label=='View career milestones' for w in self.app.button))
  self.app.session_state.events=[{'label':'MPAR','date':date(2070,1,1)}];self.app.run()
  self.assertTrue(any(w.label=='View career milestones' for w in self.app.button))
  self.assertTrue(any('MPAR' in m.value for m in self.app.markdown))
 def test_route_history_does_not_touch_user_data_or_duplicate_current_route(self):
  state={'nav_page':'home','profile':{'service':'Royal Navy'},'draft':'keep'}
  transition(state,'home','Home');self.assertEqual(state['route_history'],[])
  transition(state,'money','Money',money=True);transition(state,'policy','Ask')
  back(state,lambda p:{'home':'Home','money':'Money','policy':'Ask'}[p])
  self.assertEqual(state['nav_page'],'money');self.assertTrue(state['money_overview'])
  self.assertEqual(state['profile'],{'service':'Royal Navy'});self.assertEqual(state['draft'],'keep')
