import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import button_automation_helpers


def set_service(entity_id, state):
    return ["set", entity_id, state]


class ButtonAutomationHelpersTest(unittest.TestCase):
    def test_button_toggle_automation(self):
        self.assertEqual(
            button_automation_helpers.button_toggle_automation(
                "Kitchen ",
                "Kitchen",
                True,
                "Wall Switch",
                "Single",
                "Ceiling Light",
                ["sensor.kitchen_wall_switch"],
                ["single", "1"],
                ["light.kitchen_ceiling"],
                set_service,
            ),
            {
                "alias": "ZLB-Kitchen Wall Switch - Single Press - Toggle Ceiling Light-Kitchen",
                "configured": True,
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": ["sensor.kitchen_wall_switch"],
                        "to": ["single", "1"],
                    }
                ],
                "action": [["set", ["light.kitchen_ceiling"], "toggle"]],
            },
        )


if __name__ == "__main__":
    unittest.main()
