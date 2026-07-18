import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import camera_automation_helpers


class CameraAutomationHelpersTest(unittest.TestCase):
    def test_kitchen_camera_automations(self):
        automations = camera_automation_helpers.kitchen_camera_automations(
            "Kitchen ",
            "Kitchen",
            "input_select.kitchen_occupancy",
            [{"platform": "time_pattern", "minutes": "/30"}],
        )

        self.assertEqual(len(automations), 2)
        self.assertEqual(
            automations[0],
            {
                "alias": "ZM-Kitchen Reset Camera Position After People Left-Kitchen",
                "configured": True,
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": "input_select.kitchen_occupancy",
                        "to": "Outside",
                        "for": "00:10:00",
                    },
                    {"platform": "time_pattern", "minutes": "/30"},
                ],
                "actions": {"action": "script.kitchen_camera_pointing_to_door"},
            },
        )
        self.assertEqual(
            automations[1],
            {
                "alias": "ZM-Kitchen Point Camera To the Table When People Enter-Kitchen",
                "configured": True,
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": "input_select.kitchen_occupancy",
                        "from": "Outside",
                        "to": "Just Entered",
                    }
                ],
                "actions": {"action": "script.kitchen_camera_pointing_to_dining_table"},
            },
        )


if __name__ == "__main__":
    unittest.main()
