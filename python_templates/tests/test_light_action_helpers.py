import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import light_action_helpers


class LightActionHelpersTest(unittest.TestCase):
    def test_wall_switch_turn_on_reset_sequence(self):
        self.assertEqual(
            light_action_helpers.wall_switch_turn_on_reset_sequence(
                ["switch.kitchen_wall"]
            ),
            [
                {
                    "service": "homeassistant.turn_off",
                    "entity_id": ["switch.kitchen_wall"],
                },
                {"delay": {"milliseconds": 200}},
                {
                    "service": "homeassistant.turn_on",
                    "entity_id": ["switch.kitchen_wall"],
                },
            ],
        )

    def test_wall_switch_turn_on_reset_alias(self):
        self.assertEqual(
            light_action_helpers.wall_switch_turn_on_reset_alias(),
            "Everytime to turn on a wall switch, make sure to turn off it first to make sure the smart lights will be back on",
        )

    def test_turn_on_with_brightness_action(self):
        self.assertEqual(
            light_action_helpers.turn_on_with_brightness_action(
                ["light.kitchen_ceiling"],
                50,
            ),
            {
                "service": "light.turn_on",
                "entity_id": ["light.kitchen_ceiling"],
                "data": {"brightness_pct": 50},
            },
        )

    def test_light_on_off_action(self):
        self.assertEqual(
            light_action_helpers.light_on_off_action(
                ["light.kitchen_ceiling"],
                "on",
            ),
            {
                "service": "light.turn_on",
                "entity_id": ["light.kitchen_ceiling"],
            },
        )
        self.assertEqual(
            light_action_helpers.light_on_off_action(
                ["light.kitchen_ceiling"],
                "off",
            ),
            {
                "service": "light.turn_off",
                "entity_id": ["light.kitchen_ceiling"],
            },
        )


if __name__ == "__main__":
    unittest.main()
