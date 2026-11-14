from ui_helpers import select_primary
from datetime import date
from pathlib import Path
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from benefit_journeys import empty_progress, validate_progress
import profile_backup
import test_decision_engine as fixtures

APP=Path(__file__).resolve().parents[1]/'app.py'

class GuidedJourneyTests(unittest.TestCase):
 def setUp(self):self.app=AppTest.from_file(str(APP),default_timeout=30).run()
 def widget(self,kind,label):return next(w for w in getattr(self.app,kind) if w.label==label)
 def click(self,label):self.widget('button',label).click().run();self.assertFalse(self.app.exception)
 def go(self,name):select_primary(self.app,name);self.assertFalse(self.app.exception)
 def open_fhtb(self):self.go('Home');self.click('Housing')
 def test_complete_preparation_flow_and_context_return(self):
  self.open_fhtb();self.click('Continue')
  self.assertTrue(any('Unable to verify entitlement' in m.value for m in self.app.info))
  self.click('Ask a related housing question')
  self.assertIn('Forces Help to Buy',self.widget('text_input','What do you need help with?').value)
  self.click('Continue your home-buying guide')
  self.assertEqual(self.app.session_state.benefits['fhtb']['step'],'Assess')
  self.click('Continue');self.click('Edit purchase figures')
  for label,value in [('Property price (£)',200000.0),('Your cash deposit (£)',20000.0),('Proposed advance — assumption (£)',10000.0),('Proposed mortgage (£)',170000.0),('Solicitor / conveyancing quote (£)',1500.0)]:self.widget('number_input',label).set_value(value)
  self.click('Save purchase figures')
  self.assertEqual(next(m.value for m in self.app.metric if m.label=='Funding gap'),'£1,500')
  self.click('Continue');self.click('Continue')
  self.widget('checkbox','Ask the lender or broker whether the proposed funding is acceptable').check().run()
  self.assertTrue(self.app.session_state.benefits['fhtb']['checklist']['lender'])
  self.click('← Back to benefits');self.open_fhtb()
  self.assertEqual(self.app.session_state.benefits['fhtb']['step'],'Progress')
 def test_completed_benefit_is_not_repeatedly_promoted(self):
  self.open_fhtb()
  for _ in range(4):self.click('Continue')
  self.widget('checkbox','I have already claimed or completed this journey').check().run()
  self.go('Home')
  self.assertFalse(any(b.label=='Plan a home purchase' for b in self.app.button))
  self.assertTrue(any(b.label=='Revisit home-buying plan' for b in self.app.button))
 def test_progress_is_encrypted_and_restored_in_new_session(self):
  self.open_fhtb()
  for _ in range(4):self.click('Continue')
  self.widget('checkbox','Read the current official FHTB guidance and confirm scheme conditions').check().run()
  profile=self.app.session_state.profile;benefits=self.app.session_state.benefits
  data=profile_backup.save(profile,[],'a long passphrase for tests',benefits)
  restored=profile_backup.load(data,'a long passphrase for tests')
  other=AppTest.from_file(str(APP),default_timeout=30).run();other.session_state.pending_profile_restore=restored;other.run()
  other.button(key='dashboard_Housing').click().run()
  self.assertFalse(other.exception)
  self.assertTrue(next(w for w in other.checkbox if w.label=='Read the current official FHTB guidance and confirm scheme conditions').value)
 def test_invalid_progress_does_not_restore_free_text_or_arbitrary_actions(self):
  with self.assertRaises(ValueError):validate_progress({'checklist':{'service_number':'sensitive'}})
  with self.assertRaises(ValueError):validate_progress({'facts':{'fhtb.secret':{'value':'x'*1000,'provenance':'user_confirmed'}}})
 def test_no_production_rules_issue_eligible_decision_for_private_or_wo1(self):
  for rank in ['Private / equivalent','Warrant Officer Class 1']:
   self.go('Profile');self.widget('selectbox','Rank').select(rank).run();self.click('Update linked demo profile')
   self.go('Policy');self.widget('text_input','What do you need help with?').input('Can I claim my lunch back yesterday?').run()
   self.assertTrue(any('Unable to verify entitlement against current policy' in m.value for m in self.app.markdown))
   self.assertFalse(any(w.label.startswith('Synthetic') for w in self.app.radio))
 def test_verified_fixture_asks_only_one_missing_question_and_reuses_previous_answer(self):
  fixture=fixtures.DecisionTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
  rule=fixtures.synthetic_rule()
  with patch('decision_engine.load_rules',return_value=[rule]),patch('policy_ui.PolicyIndex',return_value=fixture.index):
   self.go('Policy');self.widget('text_input','What do you need help with?').input('Can I claim my lunch back yesterday?').run()
   questions=[w for w in self.app.radio if w.label.startswith('Synthetic test')]
   self.assertEqual(len(questions),1)
   questions[0].set_value('Yes').run()
   questions=[w for w in self.app.radio if w.label.startswith('Synthetic test')]
   self.assertEqual(len(questions),1);self.assertIn('provided',questions[0].label)
   self.click('Change my answers')
   questions=[w for w in self.app.radio if w.label.startswith('Synthetic test')]
   self.assertEqual(len(questions),1);self.assertIn('duty',questions[0].label);self.assertEqual(questions[0].value,'Not sure')
   questions[0].set_value('Yes').run()
   questions=[w for w in self.app.radio if w.label.startswith('Synthetic test')]
   questions[0].set_value('No').run()
   self.assertTrue(any('Appears eligible, subject to stated conditions' in m.value for m in self.app.markdown))
   self.go('Money');self.go('Policy')
   self.assertTrue(any('Appears eligible, subject to stated conditions' in m.value for m in self.app.markdown))
   self.assertFalse(any(w.label.startswith('Synthetic test') for w in self.app.radio))

 def test_question_is_restored_after_widget_cleanup_but_clearing_is_respected(self):
  self.go('Policy');self.widget('text_input','What do you need help with?').input('Lunch yesterday?').run()
  self.go('Money')
  try:del self.app.session_state['input:📚 JSP finder:guided_search']
  except KeyError:pass
  self.go('Policy')
  self.assertEqual(self.widget('text_input','What do you need help with?').value,'Lunch yesterday?')
  self.widget('text_input','What do you need help with?').input('').run()
  self.go('Money');self.go('Policy')
  self.assertEqual(self.widget('text_input','What do you need help with?').value,'')
