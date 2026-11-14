from ui_helpers import select_primary
from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest
from app_context import question_handoff, linked_milestones

APP=Path(__file__).resolve().parents[1]/'app.py'

class ConnectedJourneys(unittest.TestCase):
    def setUp(self):
        self.app=AppTest.from_file(str(APP),default_timeout=30).run()
    def field(self,kind,label):return next(w for w in getattr(self.app,kind) if w.label==label)
    def go(self,destination):
        select_primary(self.app,destination)
        self.assertFalse(self.app.exception)
    def test_home_question_handoff_and_clarifications_survive_navigation(self):
        self.field('text_input','Ask Forces HQ').input('Can I claim my lunch back today?')
        self.field('button','Open Ask').click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.field('text_input','What do you need help with?').value,'Can I claim my lunch back today?')
        self.assertTrue(any('Meals and subsistence' in m.value for m in self.app.subheader))
        self.assertFalse(any('motor mileage' in m.value.lower() for m in self.app.markdown))
        self.app.session_state.decision_facts={'meals':{'meals.provided':{'value':'No','provenance':'user_confirmed'}}}
        self.go('Money');self.go('Policy')
        self.assertEqual(self.app.session_state.decision_facts['meals']['meals.provided']['value'],'No')
        self.assertTrue(any('Source unavailable' in w.value for w in self.app.warning))
    def test_entitlement_to_policy_carries_subject_and_profile(self):
        self.go('Profile')
        self.field('selectbox','Service').select('Royal Navy').run()
        self.field('button','Update linked demo profile').click().run()
        self.go('Claims')
        self.field('button','Start your home-buying guide').click().run()
        self.field('button','Continue').click().run()
        self.field('button','Ask a related housing question').click().run()
        self.assertIn('Forces Help to Buy',self.field('text_input','What do you need help with?').value)
        self.assertTrue(any('Royal Navy' in m.value for m in self.app.caption))
    def test_helper_does_not_lose_question_when_policy_widget_is_hidden(self):
        state={}
        question_handoff(state,'meal on exercise','policy')
        self.assertEqual(state['input:policy:guided_search'],'meal on exercise')
        self.assertIn('input:policy:guided_search',state['_input_keys'])
    def test_career_events_are_visible_in_profile(self):
        self.go('Career')
        self.field('button','Add milestone').click().run()
        self.go('Profile')
        self.assertTrue(any('Objectives agreed' in m.value for m in self.app.markdown))

    def test_restore_updates_already_rendered_profile_widgets(self):
        self.go('Profile')
        self.assertEqual(self.field('selectbox','Service').value,'British Army')
        self.app.session_state.pending_profile_restore={'profile':{'service':'Royal Navy','verified_pensionable_salary':47000,'salary_verified':True},'events':[]}
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.field('selectbox','Service').value,'Royal Navy')
        self.assertEqual(self.field('number_input','Verified annual pensionable earnings (£) — optional').value,47000)
