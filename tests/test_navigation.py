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
        self.field('radio', 'Primary navigation').set_value(name).run()
        self.assertFalse(self.app.exception)

    def test_destinations_and_every_section_are_synchronised(self):
        groups = {'Home':[0], 'Explore':[3,4,5,6,7], 'Money':[2,8], 'Profile':[1]}
        pages = self.field('selectbox', 'Go to section').options
        for destination, indices in groups.items():
            self.go(destination)
            self.assertEqual(self.field('selectbox', 'Go to section').value, pages[indices[0]])
            for index in indices:
                self.field('selectbox', 'Go to section').select(pages[index]).run()
                self.assertEqual(self.field('radio', 'Primary navigation').value, destination)
                self.assertFalse(self.app.exception)

    def test_primary_navigation_retains_unsaved_inputs(self):
        self.go('Profile')
        self.field('text_input', 'Trade / role (optional)').input('Fictional draft role').run()
        self.go('Money')
        self.field('number_input', 'Monthly take-home income (£)').set_value(3600).run()
        self.go('Explore')
        self.go('Home')
        self.go('Profile')
        self.assertEqual(self.field('text_input', 'Trade / role (optional)').value, 'Fictional draft role')
        self.go('Money')
        self.assertEqual(self.field('number_input', 'Monthly take-home income (£)').value, 3600)

    def test_policy_entry_and_group_shortcut(self):
        self.field('button', 'Ask a policy question').click().run()
        self.assertEqual(self.field('radio', 'Primary navigation').value, 'Explore')
        self.field('button', '✍️ Achievement assistant').click().run()
        self.assertEqual(self.field('selectbox', 'Go to section').value, '✍️ Achievement assistant')
        self.assertFalse(self.app.exception)
