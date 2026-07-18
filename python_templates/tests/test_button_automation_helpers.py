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

    def test_flex_wall_switch_restore_automation(self):
        self.assertEqual(
            button_automation_helpers.flex_wall_switch_restore_automation(
                "Kitchen ",
                "Kitchen",
                2,
                "switch.kitchen_wall_switch_left",
                set_service,
            ),
            {
                "alias": "ZLB-Kitchen Flex Wall Switch On Postion 2- Automatically Turn on the Wall Switch Back When Turned Off -Kitchen",
                "configured": True,
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": "switch.kitchen_wall_switch_left",
                        "to": "off",
                    }
                ],
                "action": [
                    ["set", "switch.kitchen_wall_switch_left", "on"],
                    {"delay": "00:00:01"},
                    ["set", "switch.kitchen_wall_switch_left", "on"],
                    {"delay": "00:00:01"},
                    ["set", "switch.kitchen_wall_switch_left", "on"],
                ],
                "mode": "queued",
            },
        )

    def test_wall_button_double_leave_room_automation(self):
        self.assertEqual(
            button_automation_helpers.wall_button_double_leave_room_automation(
                "Kitchen ",
                "Kitchen",
                True,
                ["sensor.kitchen_wall_switch"],
                "automation.kitchen_lights_off",
                "automation.kitchen_heating_off",
                "input_select.kitchen_occupancy",
            ),
            {
                "alias": "ZLB-Kitchen Wall Switch - Double Click - Leave Room and Turn Off Everything-Kitchen",
                "configured": True,
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": ["sensor.kitchen_wall_switch"],
                        "to": [
                            "2",
                            "double",
                            "double_left",
                            "double_right",
                            "double_center",
                            "button_1_double",
                            "button_2_double",
                            "button_3_double",
                        ],
                    }
                ],
                "action": [
                    {
                        "service": "automation.trigger",
                        "entity_id": [
                            "automation.kitchen_lights_off",
                            "automation.kitchen_heating_off",
                        ],
                    },
                    {
                        "service": "input_select.select_option",
                        "target": {"entity_id": "input_select.kitchen_occupancy"},
                        "data": {"option": "Outside"},
                    },
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
