from ui_helpers import select_primary
"""Session and calculation regression tests; all entered data is fictional."""
from datetime import date
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / 'app.py'


class AppRegressionTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(APP), default_timeout=30).run()
        self.pages = ['🏠 Dashboard','🎖️ My profile','💷 My money','🎯 Entitlements','📚 JSP finder','📅 My career','✍️ Achievement assistant','🏡 Life & future','🏦 Pension planner']
        self.healthy()

    def field(self, kind, label):
        return next(widget for widget in getattr(self.app, kind) if widget.label == label)

    def healthy(self):
        self.assertEqual(len(self.app.exception), 0, str(self.app.exception))

    def page(self, index):
        destination = {0:'Home',1:'Me',2:'Money',3:'Explore',4:'Ask',5:'Explore',6:'Explore',7:'Explore',8:'Money'}[index]
        select_primary(self.app,destination)
        if index in (2,5,6,7,8):
            self.app.button(key='group_nav_'+str(index)).click().run()
        self.healthy()

    def click(self, label):
        self.field('button', label).click().run()
        self.healthy()

    def round_trip(self, index):
        self.page(0)
        self.page(index)

    def test_all_pages_and_navigation_stay_in_sync(self):
        for index in range(9):
            with self.subTest(page=index):
                self.page(index)
                self.assertEqual(self.app.session_state.nav_sidebar, self.pages[index])
        self.page(0)
        self.click('Pension')
        self.assertEqual(self.app.session_state.nav_page, self.pages[8])
        self.assertEqual(self.app.session_state.nav_sidebar, self.pages[8])

    def test_budget_and_savings_survive_navigation(self):
        self.page(2)
        self.field('number_input', 'Monthly take-home income (£)').set_value(3500).run()
        self.field('slider', 'Monthly contribution (£)').set_value(300).run()
        self.field('slider', 'Illustrative annual return after fees (%)').set_value(0.0).run()
        before = [m.value for m in self.app.metric]
        self.round_trip(2)
        self.assertEqual(self.field('number_input', 'Monthly take-home income (£)').value, 3500)
        self.assertEqual([m.value for m in self.app.metric], before)
        self.assertEqual(before[0], '£1,250')
        self.assertEqual(before[1], '£54,000')

    def test_nonzero_savings_and_inflation_arithmetic(self):
        self.page(2)
        rate = 1.05 ** (1 / 12) - 1
        nominal = 200 * ((1 + rate) ** 180 - 1) / rate
        self.assertEqual(self.app.metric[1].value, f'£{nominal:,.0f}')
        self.assertEqual(self.app.metric[2].value, f'£{nominal / 1.025 ** 15:,.0f}')

    def test_unsaved_profile_and_optional_dates_survive_navigation(self):
        self.page(1)
        self.field('text_input', 'Trade / role (optional)').input('Fictional role').run()
        for enabled, label, value in [
            ('Record enlistment date', 'Date joined', date(2010, 9, 1)),
            ('Record birth date', 'Date of birth', date(1990, 1, 1)),
            ('Record planned leaving date', 'Planned exit', date(2030, 1, 1)),
        ]:
            self.assertTrue(self.field('date_input', label).disabled)
            self.field('checkbox', enabled).check().run()
            self.assertFalse(self.field('date_input', label).disabled)
            self.assertIsNone(self.field('date_input', label).value)
            self.field('date_input', label).set_value(value).run()
        self.round_trip(1)
        self.assertEqual(self.field('text_input', 'Trade / role (optional)').value, 'Fictional role')
        self.assertEqual(self.field('date_input', 'Date joined').value, date(2010, 9, 1))
        self.assertIsNone(self.app.session_state.profile['join_date'])
        self.click('Update linked demo profile')
        self.assertEqual(self.app.session_state.profile['join_date'], date(2010, 9, 1))
        self.assertEqual(self.app.session_state.profile['trade'], 'Fictional role')
        self.assertTrue(any('updated' in item.value for item in self.app.success))
        self.field('checkbox', 'Record enlistment date').uncheck().run()
        self.click('Update linked demo profile')
        self.assertIsNone(self.app.session_state.profile['join_date'])

    def test_invalid_profile_does_not_replace_saved_profile(self):
        self.page(1)
        self.field('checkbox', 'Record enlistment date').check().run()
        self.click('Update linked demo profile')
        self.assertTrue(any('Choose a date joined' in e.value for e in self.app.error))
        self.field('date_input', 'Date joined').set_value(date(2010, 1, 1)).run()
        self.field('checkbox', 'Record birth date').check().run()
        self.field('date_input', 'Date of birth').set_value(date(2015, 1, 1)).run()
        self.click('Update linked demo profile')
        self.assertTrue(any('birth date must be before' in e.value for e in self.app.error))
        self.assertIsNone(self.app.session_state.profile['join_date'])
        self.field('multiselect', 'Scheme membership (self-reported; not verified)').set_value(['Not sure', 'AFPS 15']).run()
        self.click('Update linked demo profile')
        self.assertTrue(any('rather than both' in e.value for e in self.app.error))

    def test_search_and_conditional_answers_survive_navigation(self):
        self.page(4)
        self.field('text_input', 'What do you need help with?').input('Can I claim mileage for duty travel?').run()
        self.app.session_state.decision_facts={'mileage':{'mileage.approved':{'value':'No','provenance':'user_confirmed'}}}
        self.round_trip(4)
        self.assertEqual(self.field('text_input','What do you need help with?').value,'Can I claim mileage for duty travel?')
        self.assertEqual(self.app.session_state.decision_facts['mileage']['mileage.approved']['value'],'No')
        self.assertTrue(any('Unable to verify entitlement' in m.value for m in self.app.markdown))

    def test_filters_and_life_planning_survive_navigation(self):
        self.page(3)
        self.field('selectbox', 'What is happening in your life?').select('Buying a home').run()
        self.round_trip(3)
        self.assertEqual(self.field('selectbox', 'What is happening in your life?').value, 'Buying a home')
        self.page(7)
        self.field('selectbox', 'What are you planning?').select('Leave').run()
        self.round_trip(7)
        self.assertEqual(self.field('selectbox', 'What are you planning?').value, 'Leave')

    def test_career_and_rank_milestones_add_remove(self):
        self.page(5)
        due = date(2030, 2, 1)
        self.field('date_input', 'Your confirmed date').set_value(due).run()
        self.round_trip(5)
        self.assertEqual(self.field('date_input', 'Your confirmed date').value, due)
        self.click('Add milestone')
        self.assertEqual(len(self.app.session_state.events), 1)
        self.assertEqual(self.app.session_state.events[0]['date'], due)
        self.click('Remove')
        self.assertEqual(self.app.session_state.events, [])
        self.page(1)
        self.field('text_input', 'Optional non-identifying milestone (course, posting, qualification)').input('Fictional course').run()
        self.round_trip(1)
        self.click('Add dated milestone')
        self.assertEqual(len(self.app.session_state.profile['rank_history']), 1)
        self.assertEqual(self.field('text_input', 'Optional non-identifying milestone (course, posting, qualification)').value, '')
        self.click('Remove')
        self.assertEqual(self.app.session_state.profile['rank_history'], [])

    def add_achievement(self, action='Led a fictional exercise'):
        self.field('text_area', 'What did you do?').input(action).run()
        self.field('text_area', 'What changed? Include evidence you could verify.').input('Trained 12 fictional people').run()
        self.click('Add practice achievement')

    def test_promotion_before_enlistment_is_rejected_without_changing_timeline(self):
        self.page(1)
        self.field('checkbox', 'Record enlistment date').check().run()
        self.field('date_input', 'Date joined').set_value(date(2010, 1, 1)).run()
        self.click('Update linked demo profile')
        self.field('date_input', 'Effective date of rank').set_value(date(2015, 1, 1)).run()
        self.click('Add dated milestone')
        saved = list(self.app.session_state.profile['rank_history'])
        self.field('date_input', 'Effective date of rank').set_value(date(2009, 12, 31)).run()
        self.click('Add dated milestone')
        self.assertTrue(any('cannot be before the enlistment date' in e.value for e in self.app.error))
        self.assertEqual(self.app.session_state.profile['rank_history'], saved)
        self.assertEqual(self.field('date_input', 'Effective date of rank').value, date(2009, 12, 31))
        self.field('date_input', 'Effective date of rank').set_value(date(2010, 1, 1)).run()
        self.click('Add dated milestone')
        self.assertEqual(len(self.app.session_state.profile['rank_history']), 2)
        self.round_trip(1)

    def test_empty_promotion_date_is_rejected_and_can_be_corrected(self):
        self.page(1)
        self.field('date_input', 'Effective date of rank').set_value(None).run()
        self.click('Add dated milestone')
        self.assertTrue(any('Choose an effective date of rank' in e.value for e in self.app.error))
        self.assertEqual(self.app.session_state.profile['rank_history'], [])
        self.field('date_input', 'Effective date of rank').set_value(date(2020, 1, 1)).run()
        self.click('Add dated milestone')
        self.assertEqual(len(self.app.session_state.profile['rank_history']), 1)

    def test_empty_career_date_does_not_poison_session(self):
        self.page(5)
        self.click('Add milestone')
        saved = list(self.app.session_state.events)
        self.field('date_input', 'Your confirmed date').set_value(None).run()
        self.click('Add milestone')
        self.assertTrue(any('Choose a confirmed date' in e.value for e in self.app.error))
        self.assertEqual(self.app.session_state.events, saved)
        self.round_trip(5)
        self.field('date_input', 'Your confirmed date').set_value(date(2030, 1, 1)).run()
        self.click('Add milestone')
        self.assertEqual(len(self.app.session_state.events), 2)

    def test_all_enabled_optional_profile_dates_require_a_value(self):
        self.page(1)
        for flag, label, message in [
            ('Record enlistment date', 'Date joined', 'Choose a date joined'),
            ('Record birth date', 'Date of birth', 'Choose a birth date'),
            ('Record planned leaving date', 'Planned exit', 'Choose a planned leaving date'),
        ]:
            with self.subTest(date=label):
                self.field('checkbox', flag).check().run()
                self.field('date_input', label).set_value(None).run()
                self.click('Update linked demo profile')
                self.assertTrue(any(message in e.value for e in self.app.error))
                self.assertIsNone(self.app.session_state.profile['join_date'])
                self.assertIsNone(self.app.session_state.profile['dob'])
                self.assertIsNone(self.app.session_state.profile['planned_exit'])
                self.field('checkbox', flag).uncheck().run()
        self.click('Update linked demo profile')
        self.assertEqual(len(self.app.error), 0)

    def test_editing_a_field_does_not_force_stale_values_into_active_inputs(self):
        self.page(6)
        self.field('text_area', 'What did you do?').input('Led a fictional exercise').run()
        for label in ['What did you do?', 'What changed? Include evidence you could verify.']:
            self.assertFalse(self.field('text_area', label).proto.set_value,
                             'Active inputs must not receive forced values during another field’s rerun')
        self.round_trip(6)
        self.assertEqual(self.field('text_area', 'What did you do?').value, 'Led a fictional exercise')

    def test_achievement_drafts_and_styles_preserve_edits(self):
        self.page(6)
        self.field('text_area', 'What did you do?').input('Unsubmitted fictional example').run()
        self.round_trip(6)
        self.assertEqual(self.field('text_area', 'What did you do?').value, 'Unsubmitted fictional example')
        self.add_achievement()
        draft = 'Editable draft — review all claims before use'
        self.assertIn('Led a fictional exercise', self.field('text_area', draft).value)
        self.field('text_area', draft).input('My reviewed fictional draft').run()
        self.round_trip(6)
        self.assertEqual(self.field('text_area', draft).value, 'My reviewed fictional draft')
        self.field('radio', 'Output style').set_value('MPAR preparation').run()
        self.assertIn('Discuss:', self.field('text_area', draft).value)
        self.field('radio', 'Output style').set_value('Promotion evidence').run()
        self.assertIn('Reflection:', self.field('text_area', draft).value)
        self.field('radio', 'Output style').set_value('SJAR / OJAR evidence').run()
        self.assertEqual(self.field('text_area', draft).value, 'My reviewed fictional draft')
        self.add_achievement('Planned a second fictional exercise')
        self.assertEqual(self.field('text_area', draft).value, 'My reviewed fictional draft')
        self.click('Regenerate this draft from practice examples')
        self.assertIn('second fictional exercise', self.field('text_area', draft).value)
        self.click('Clear practice examples')
        self.assertEqual(self.app.session_state.records, [])
        self.assertEqual(len(self.app.get('download_button')), 0)

    def test_unedited_draft_updates_after_another_achievement(self):
        self.page(6)
        self.add_achievement()
        self.add_achievement('A second fictional achievement')
        self.assertIn('second fictional achievement', self.field('text_area', 'Editable draft — review all claims before use').value)

    def test_pension_arithmetic_and_last_result_survive_navigation(self):
        self.page(8)
        salary = 'Current annual pensionable salary (£) — check payslip'
        self.field('number_input', salary).set_value(47000.0).run()
        self.field('checkbox', 'I have verified that the additional payment above is pensionable (or it is zero)').check().run()
        self.field('slider', 'Illustrative annual rise in pensionable salary (%)').set_value(0.0).run()
        self.field('slider', 'Illustrative active-service revaluation (%)').set_value(0.0).run()
        self.click('Calculate future AFPS 15 accrual')
        results = {m.label: m.value for m in self.app.metric}
        combined = 'Combined new annual AFPS 15 pension entitlement from ONLY the future modelled years'
        self.assertTrue(results[combined].startswith('£10,000 '))
        self.round_trip(8)
        self.assertEqual(self.field('number_input', salary).value, 47000.0)
        self.assertEqual({m.label: m.value for m in self.app.metric}, results)
        self.field('number_input', salary).set_value(48000.0).run()
        self.assertEqual(next(m.value for m in self.app.metric if m.label == combined), results[combined])
        self.assertTrue(any('last calculated scenario' in i.value for i in self.app.info))

    def test_pay_transfer_overrides_profile_for_scenario_only(self):
        self.page(1)
        self.field('number_input', 'Verified annual pensionable earnings (£) — optional').set_value(47000).run()
        self.field('checkbox', 'I have checked this pensionable earnings amount against official documentation').check().run()
        self.click('Update linked demo profile')
        self.page(8)
        salary = 'Current annual pensionable salary (£) — check payslip'
        self.assertEqual(self.field('number_input', salary).value, 47000.0)
        table_value = self.app.metric[0].value
        self.click('Use this pay figure in the AFPS 15 scenario')
        self.assertEqual(f'£{self.field("number_input", salary).value:,.0f}', table_value)
        self.assertEqual(self.app.session_state.profile['verified_pensionable_salary'], 47000.0)
        self.click('Use linked profile earnings in this scenario')
        self.assertEqual(self.field('number_input', salary).value, 47000.0)

    def test_nonzero_pension_growth_and_revaluation_arithmetic(self):
        self.page(8)
        self.field('number_input', 'Current annual pensionable salary (£) — check payslip').set_value(47000.0).run()
        self.field('number_input', 'Other ANNUAL payment confirmed pensionable by official documentation (£)').set_value(4700.0).run()
        self.field('checkbox', 'I have verified that the additional payment above is pensionable (or it is zero)').check().run()
        self.field('slider', 'Illustrative active-service revaluation (%)').set_value(3.0).run()
        self.click('Calculate future AFPS 15 accrual')
        expected = 1100 * sum(1.02 ** year * 1.03 ** (9 - year) for year in range(10))
        combined = next(m.value for m in self.app.metric if m.label.startswith('Combined new annual'))
        self.assertTrue(combined.startswith(f'£{expected:,.0f} '))

    def test_official_quote_inputs_survive_demo_toggle_and_navigation(self):
        self.page(8)
        self.field('checkbox', 'Use fictional demonstration figures').uncheck().run()
        self.field('number_input', 'Cost of Added Pension contract from your quote (£)').set_value(10000).run()
        self.field('number_input', 'Extra gross annual pension from your quote (£)').set_value(500).run()
        self.field('slider', 'Illustrative number of years in payment').set_value(25).run()
        self.assertEqual(self.app.metric[-1].value, '£2,500')
        self.field('checkbox', 'Use fictional demonstration figures').check().run()
        self.field('checkbox', 'Use fictional demonstration figures').uncheck().run()
        self.round_trip(8)
        self.assertEqual(self.field('number_input', 'Cost of Added Pension contract from your quote (£)').value, 10000)
        self.assertEqual(self.app.metric[-1].value, '£2,500')

    def test_new_session_does_not_inherit_another_users_inputs(self):
        self.page(2)
        self.field('number_input', 'Monthly take-home income (£)').set_value(3500).run()
        other = AppTest.from_file(str(APP), default_timeout=30).run()
        select_primary(other,'Money')
        other.button(key='group_nav_2').click().run()
        self.assertEqual(next(x.value for x in other.number_input if x.label == 'Monthly take-home income (£)'), 2600)


if __name__ == '__main__':
    unittest.main()
