import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import mirror_automation_helpers


class MirrorAutomationHelpersTest(unittest.TestCase):
    def test_mirror_sensor_on_automation(self):
        self.assertEqual(
            mirror_automation_helpers.mirror_sensor_on_automation(
                "Kitchen ",
                "Kitchen",
                ["binary_sensor.kitchen_mirror"],
                ["light.kitchen_ceiling"],
            ),
            {
                "alias": "ZLM-Kitchen Mirror Sensor On Turns On Ceiling Light With Cool Temperature-Kitchen",
                "configured": True,
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": ["binary_sensor.kitchen_mirror"],
                        "from": "off",
                        "to": "on",
                    }
                ],
                "action": [
                    {
                        "condition": "state",
                        "entity_id": ["binary_sensor.kitchen_mirror"],
                        "state": "on",
                    },
                    {"delay": "00:00:01"},
                    {
                        "service": "light.turn_on",
                        "target": {"entity_id": ["light.kitchen_ceiling"]},
                        "data": {"brightness_pct": 100, "kelvin": 6500},
                    },
                ],
            },
        )

    def test_mirror_sensor_off_automation(self):
        self.assertEqual(
            mirror_automation_helpers.mirror_sensor_off_automation(
                "Kitchen ",
                "Kitchen",
                ["binary_sensor.kitchen_mirror"],
                "input_select.kitchen_occupancy",
                "switch.adaptive_lighting_kitchen",
            ),
            {
                "alias": "ZLM-Kitchen Mirror Sensor Off Turns Ceiling Light With Adaptive Lighting Unless it's off-Kitchen",
                "configured": True,
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": ["binary_sensor.kitchen_mirror"],
                        "from": "on",
                        "to": "off",
                    }
                ],
                "action": [
                    {"delay": "00:00:01"},
                    {
                        "condition": "state",
                        "entity_id": "input_select.kitchen_occupancy",
                        "state": ["Just Entered", "Stayed Inside"],
                    },
                    {
                        "service": "adaptive_lighting.apply",
                        "data": {"entity_id": "switch.adaptive_lighting_kitchen"},
                    },
                ],
            },
        )

    def test_mirror_sensor_automations_are_unconfigured_without_sensor(self):
        self.assertFalse(
            mirror_automation_helpers.mirror_sensor_on_automation(
                "Kitchen ",
                "Kitchen",
                [],
                ["light.kitchen_ceiling"],
            )["configured"]
        )


if __name__ == "__main__":
    unittest.main()
