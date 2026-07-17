import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import dashboard_view_helpers


class DashboardViewHelpersTest(unittest.TestCase):
    def test_build_view(self):
        self.assertEqual(
            dashboard_view_helpers.build_view(
                view_path="kitchen",
                cards=[{"type": "entities"}],
                theme="Mushroom Shadow",
                title="Kitchen",
            ),
            {
                "theme": "Mushroom Shadow",
                "title": "Kitchen",
                "path": "kitchen",
                "subview": True,
                "badges": [],
                "cards": [{"type": "entities"}],
            },
        )

    def test_mobile_layout_wraps_cards_in_grid(self):
        cards = [{"type": "button"}]

        self.assertEqual(
            dashboard_view_helpers.layout_wrapper_cards("mobile", cards=cards),
            [{"square": False, "columns": 2, "type": "grid", "cards": cards}],
        )

    def test_tablet_layout_returns_cards_directly(self):
        cards = [{"type": "button"}]

        self.assertIs(dashboard_view_helpers.layout_wrapper_cards("tablet", cards=cards), cards)

    def test_unknown_layout_raises(self):
        with self.assertRaises(TypeError):
            dashboard_view_helpers.layout_wrapper_cards("bad")


if __name__ == "__main__":
    unittest.main()
