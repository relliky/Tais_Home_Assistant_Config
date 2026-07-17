import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import dashboard_colors


class DashboardColorsTest(unittest.TestCase):
    def test_known_colors(self):
        self.assertEqual(dashboard_colors.get_color("transparent"), "rgba(245, 245, 245, 0)")
        self.assertEqual(dashboard_colors.get_color("ios_yellow"), "rgba(253,204,0,1)")
        self.assertEqual(dashboard_colors.get_color("less_transparent_grey"), "rgba(10, 10, 10, 0.7)")

    def test_unknown_color_passes_through(self):
        self.assertEqual(dashboard_colors.get_color("red"), "red")
        self.assertEqual(dashboard_colors.get_color("#ffffff"), "#ffffff")


if __name__ == "__main__":
    unittest.main()
