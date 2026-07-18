import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import climate_action_helpers


class ClimateActionHelpersTest(unittest.TestCase):
    def test_hvac_mode_for_state(self):
        self.assertEqual(climate_action_helpers.hvac_mode_for_state("off"), "off")
        self.assertEqual(climate_action_helpers.hvac_mode_for_state("on"), "heat")

    def test_set_hvac_mode_action(self):
        self.assertEqual(
            climate_action_helpers.set_hvac_mode_action(
                "climate.kitchen",
                "on",
            ),
            {
                "service": "climate.set_hvac_mode",
                "data": {"hvac_mode": "heat"},
                "entity_id": "climate.kitchen",
            },
        )

    def test_set_temperature_step_action(self):
        self.assertEqual(
            climate_action_helpers.set_temperature_step_action(
                "climate.kitchen",
                1,
            ),
            {
                "service": "climate.set_temperature",
                "target": {"entity_id": "climate.kitchen"},
                "data": {
                    "temperature": "{{ (state_attr('climate.kitchen', 'temperature')) + 1}}"
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
