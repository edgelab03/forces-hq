from ui_helpers import select_primary
"""Policy rendering must tolerate retained caches from earlier app sessions."""
from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest

APP=Path(__file__).resolve().parents[1]/'app.py'

class PolicyStateRegressionTests(unittest.TestCase):
    def app_with_state(self, state):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        for key,value in state.items():app.session_state[key]=value
        select_primary(app,'Ask')
        return app

    def test_retained_topic_must_be_a_mapping_before_membership_and_union(self):
        for old in (None, [], 'old question state'):
            for query in ('Can I claim lunch yesterday?','Can I claim lunch?'):
                with self.subTest(old=old,query=query):
                    app=self.app_with_state({'decision_facts':{'meals':old}})
                    next(w for w in app.text_input if w.label=='What do you need help with?').input(query).run()
                    self.assertFalse(app.exception,str(app.exception))
                    self.assertIsInstance(app.session_state.decision_facts['meals'],dict)
                    self.assertTrue(any('Unable to verify entitlement' in m.value for m in app.markdown))

    def test_returning_to_cached_question_does_not_union_dict_with_none(self):
        query='Can I claim lunch?'
        app=self.app_with_state({'active_question':query,'assessment_questions':{'meals':query},'decision_facts':{'meals':None}})
        self.assertFalse(app.exception,str(app.exception))
        self.assertIsNone(app.session_state['_policy_cache_recovery']['decision_facts.meals'])
        self.assertEqual(next(w.value for w in app.text_input if w.label=='What do you need help with?'),query)

    def test_legacy_scalar_incident_date_does_not_get_indexed_as_a_fact_record(self):
        app=self.app_with_state({'decision_facts':{'meals':{'meals.incident_date':'2026-11-13'}}})
        next(w for w in app.text_input if w.label=='What do you need help with?').input('Can I claim lunch yesterday?').run()
        self.assertFalse(app.exception,str(app.exception))
        self.assertIsInstance(app.session_state.decision_facts['meals']['meals.incident_date'],dict)

    def test_invalid_cache_roots_and_nullable_question_are_recovered(self):
        for state in ({'decision_facts':None},{'assessment_questions':[]},{'condition_types':None},{'active_question':None}):
            with self.subTest(state=state):
                app=self.app_with_state(state)
                self.assertFalse(app.exception,str(app.exception))
                next(w for w in app.text_input if w.label=='What do you need help with?').input('Duty mileage yesterday?').run()
                self.assertFalse(app.exception,str(app.exception))

    def test_valid_answers_profile_and_other_topics_survive_recovery_and_navigation(self):
        valid={'mileage.approved':{'value':'No','provenance':'user_confirmed'}}
        app=self.app_with_state({'decision_facts':{'meals':None,'mileage':valid}})
        original_profile=dict(app.session_state.profile)
        next(w for w in app.text_input if w.label=='What do you need help with?').input('Lunch yesterday?').run()
        for destination in ['Home','Claims','Money','Career','Profile','Policy']:
            select_primary(app,destination)
            self.assertFalse(app.exception,str(app.exception))
        self.assertEqual(app.session_state.decision_facts['mileage'],valid)
        self.assertEqual(app.session_state.profile,original_profile)
        self.assertEqual(next(w.value for w in app.text_input if w.label=='What do you need help with?'),'Lunch yesterday?')
