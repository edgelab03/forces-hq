from ui_helpers import select_primary
"""Four-destination navigation and session regression coverage (FHQ-01)."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


class PrimaryNavigationTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()

    def field(self, kind, label):
        return next(w for w in getattr(self.app, kind) if w.label == label)

    def go(self, name):
        select_primary(self.app,name)
        self.assertFalse(self.app.exception)

    def test_destinations_and_every_section_are_synchronised(self):
        groups = {'Home':[0], 'Ask':[4], 'Explore':[3,5,6,7], 'Money':[2,8], 'Me':[1]}
        pages = ['🏠 Dashboard','🎖️ My profile','💷 My money','🎯 Entitlements','📚 JSP finder','📅 My career','✍️ Achievement assistant','🏡 Life & future','🏦 Pension planner']
        for destination, indices in groups.items():
            self.go(destination)
            self.assertEqual(self.app.session_state.nav_page, pages[indices[0]])
            for index in indices:
                if index in (2,5,6,7,8):self.app.button(key='group_nav_'+str(index)).click().run()
                self.assertEqual(self.app.session_state.nav_primary, destination)
                self.assertFalse(self.app.exception)

    def test_primary_navigation_retains_unsaved_inputs(self):
        self.go('Profile')
        self.field('text_input', 'Trade / role (optional)').input('Fictional draft role').run()
        self.go('Money')
        self.app.button(key='group_nav_2').click().run()
        self.field('number_input', 'Monthly take-home income (£)').set_value(3600).run()
        self.go('Claims')
        self.go('Home')
        self.go('Profile')
        self.assertEqual(self.field('text_input', 'Trade / role (optional)').value, 'Fictional draft role')
        self.go('Money')
        self.app.button(key='group_nav_2').click().run()
        self.assertEqual(self.field('number_input', 'Monthly take-home income (£)').value, 3600)

    def test_policy_entry_and_group_shortcut(self):
        self.field('text_input', 'Ask Forces HQ').input('meal on duty')
        self.field('button', 'Open Ask').click().run()
        self.assertEqual(self.app.session_state.nav_primary, 'Ask')
        self.go('Career')
        self.field('button', 'Achievements').click().run()
        self.assertEqual(self.app.session_state.nav_page, '✍️ Achievement assistant')
        self.assertFalse(self.app.exception)

    def test_all_dashboard_cards_have_useful_destinations(self):
        for label,target in [('Your pay','💷 My money'),('Pension','🏦 Pension planner'),('Learning','📅 My career')]:
            self.go('Home')
            self.field('button',label).click().run()
            self.assertEqual(self.app.session_state.nav_page,target)
            self.assertFalse(self.app.exception)
        self.go('Home')
        self.field('button','Housing').click().run()
        self.assertEqual(self.app.session_state.active_journey,'fhtb')
        self.assertFalse(self.app.exception)
