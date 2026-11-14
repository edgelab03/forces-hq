"""Claim UI regressions. Synthetic rules exercise interaction, not MOD policy."""
from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from decision_engine import assess
from policy_engine import PolicyIndex, write_index
from test_decision_engine import synthetic_rule, QUOTE, DIGEST
from ui_helpers import select_primary

APP=Path(__file__).resolve().parents[1]/'app.py'


class ClaimConversationTests(unittest.TestCase):
 def open_ask(self):
  app=AppTest.from_file(str(APP),default_timeout=30).run()
  select_primary(app,'Ask')
  return app

 def test_prompt_starts_a_check_without_inventing_policy_questions(self):
  app=self.open_ask()
  app.button(key='claim_prompt_meal').click().run()
  self.assertFalse(app.exception)
  self.assertEqual(app.session_state.active_question,'Can I claim a meal?')
  self.assertTrue(any('Unable to verify entitlement' in m.value for m in app.markdown))
  self.assertEqual(len(app.radio),0)
  self.assertEqual(len(app.get('chat_message')),2)
  select_primary(app,'Money');select_primary(app,'Ask')
  self.assertEqual(app.session_state.active_question,'Can I claim a meal?')

 def test_new_claim_clears_only_current_claim_and_home_draft(self):
  app=self.open_ask()
  other={'mileage.approved':{'value':'No','provenance':'user_confirmed'}}
  app.session_state.decision_facts={'mileage':other}
  next(w for w in app.text_input if w.label=='What do you need help with?').input('Lunch yesterday?').run()
  self.assertIn('meals.incident_date',app.session_state.decision_facts['meals'])
  profile=dict(app.session_state.profile)
  app.button(key='new_claim_check').click().run()
  self.assertFalse(app.exception)
  self.assertEqual(app.session_state.decision_facts['meals'],{})
  self.assertEqual(app.session_state.decision_facts['mileage'],other)
  self.assertEqual(app.session_state.profile,profile)
  self.assertEqual(app.session_state.active_question,'')
  select_primary(app,'Home')
  self.assertEqual(next(w.value for w in app.text_input if w.label=='Ask Forces HQ'),'')

 def test_reviewed_fixture_asks_one_question_and_keeps_answer_in_conversation(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'index.sqlite3'
   write_index(path,[{'source_id':'TEST ONLY','document_id':'synthetic','title':'TEST ONLY',
    'url':'https://assets.publishing.service.gov.uk/synthetic-not-policy.pdf',
    'retrieved_at':date.today().isoformat(),'sha256':DIGEST,
    'pages':['CHAPTER 99 TEST ONLY\nSECTION 98 TEST ONLY\n99.9801. '+QUOTE]}])
   rule=synthetic_rule()
   with patch('policy_ui.PolicyIndex',return_value=PolicyIndex(path)),patch('policy_ui.assess',side_effect=lambda category,facts,index:assess(category,facts,index,[rule])):
    app=self.open_ask()
    next(w for w in app.text_input if w.label=='What do you need help with?').input('Lunch yesterday?').run()
    self.assertEqual([w.label for w in app.radio],['Synthetic test duty condition?'])
    app.radio[0].set_value('Yes').run()
    self.assertFalse(app.exception)
    self.assertEqual([w.label for w in app.radio],['Synthetic test provided-meal condition?'])
    self.assertTrue(any(w.value=='Yes' for w in app.text))
    select_primary(app,'Home');select_primary(app,'Ask')
    self.assertEqual([w.label for w in app.radio],['Synthetic test provided-meal condition?'])
    app.radio[0].set_value('No').run()
    self.assertFalse(app.exception)
    self.assertEqual(len(app.radio),0)
    self.assertTrue(any('Appears eligible' in m.value for m in app.markdown))
    self.assertTrue(any(w.value=='No' for w in app.text))
    app.button(key='new_claim_check').click().run()
    app.button(key='claim_prompt_meal').click().run()
    self.assertEqual(len(app.radio),0)
    self.assertEqual([w.label for w in app.date_input],['On which date did this happen?'])
