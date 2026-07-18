import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import occupancy_automation_helpers


def set_service(entity_id, state):
    return ["set", entity_id, state]


class OccupancyAutomationHelpersTest(unittest.TestCase):
    def test_occupancy_override_to_timer_automation(self):
        automation = occupancy_automation_helpers.occupancy_override_to_timer_automation(
            "Kitchen ",
            "Kitchen",
            True,
            "input_boolean.kitchen_occupancy_override",
            "timer.kitchen_occupancy_override",
            "input_select.kitchen_occupancy",
            "automation.kitchen_occupancy_update",
            set_service,
        )

        self.assertEqual(
            automation["alias"],
            "ZOc-Kitchen Occupancy Override and sync to Timer-Kitchen",
        )
        self.assertEqual(automation["mode"], "single")
        self.assertTrue(automation["configured"])
        self.assertEqual(
            automation["trigger"],
            [
                {
                    "platform": "state",
                    "entity_id": "input_boolean.kitchen_occupancy_override",
                }
            ],
        )
        choose = automation["action"][0]["choose"]
        self.assertEqual(choose[0]["conditions"][0]["state"], "on")
        self.assertEqual(
            choose[0]["sequence"],
            [
                {
                    "service": "timer.start",
                    "target": {"entity_id": "timer.kitchen_occupancy_override"},
                },
                ["set", "automation.kitchen_occupancy_update", "off"],
                {
                    "service": "input_select.select_option",
                    "target": {"entity_id": "input_select.kitchen_occupancy"},
                    "data": {"option": "Stayed Inside"},
                },
            ],
        )
        self.assertEqual(choose[1]["conditions"][0]["state"], "off")
        self.assertEqual(
            choose[1]["sequence"],
            [
                {
                    "service": "timer.cancel",
                    "target": {"entity_id": "timer.kitchen_occupancy_override"},
                },
                ["set", "automation.kitchen_occupancy_update", "on"],
            ],
        )


if __name__ == "__main__":
    unittest.main()
