import os
import sys
import unittest
from unittest.mock import patch


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import dashboard_settings


class DashboardSettingsTest(unittest.TestCase):
    def test_default_dashboard_settings(self):
        with patch("dashboard_settings.random.randint", return_value=2):
            settings = dashboard_settings.default_dashboard_settings()

        self.assertEqual(settings["dashboard_default_root"], "/Uninitliazed_dashboard_root")
        self.assertEqual(settings["dashboard_view_name"], "Uninitliazed_dashboard_view_name")
        self.assertEqual(settings["room_icon"], "Uninitliazed_room_icon")
        self.assertEqual(settings["room_theme"], "ios-dark-mode-dark-green")


if __name__ == "__main__":
    unittest.main()
