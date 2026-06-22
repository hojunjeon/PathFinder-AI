from pathlib import Path
from django.test import SimpleTestCase


class TestDiscoveryShapeTests(SimpleTestCase):
    def test_app_test_packages_do_not_conflict_with_tests_py(self):
        backend_dir = Path(__file__).resolve().parent.parent
        for app_name in ['accounts', 'analysis', 'companies']:
            app_dir = backend_dir / app_name
            self.assertFalse((app_dir / 'tests.py').exists())
            self.assertTrue((app_dir / 'tests' / '__init__.py').exists())
            self.assertTrue(list((app_dir / 'tests').glob('test_*.py')))
