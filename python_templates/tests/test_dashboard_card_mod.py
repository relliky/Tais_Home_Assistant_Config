import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import dashboard_card_mod


class DashboardCardModTest(unittest.TestCase):
    def test_background_color_select(self):
        card_mod = dashboard_card_mod.build_card_mod(
            style="background_color_select",
            color="ios_yellow",
        )

        self.assertEqual(
            card_mod,
            {
                "card_mod": {
                    "style": ":host { --ha-card-background:rgba(253,204,0,1);}\n"
                }
            },
        )

    def test_ios16_toggle_light_card_uses_expected_templates(self):
        style = dashboard_card_mod.build_card_mod(
            style="ios16_toggle",
            card_type="custom:mushroom-light-card",
            color="ios_yellow",
            support_dark_mode=False,
        )["card_mod"]["style"]

        self.assertIn("states(config.entity) in ['on']", style)
        self.assertNotIn("states('sun.sun')", style)
        self.assertIn("mushroom-light-brightness-control", style)
        self.assertIn("rgb{{state_attr(config.entity, 'rgb_color')}}", style)
        self.assertIn("mushroom-button:nth-child(2)", style)
        self.assertIn("mushroom-button:nth-child(3)", style)

    def test_unknown_style_raises(self):
        with self.assertRaises(TypeError):
            dashboard_card_mod.build_card_mod(style="unknown")


if __name__ == "__main__":
    unittest.main()
