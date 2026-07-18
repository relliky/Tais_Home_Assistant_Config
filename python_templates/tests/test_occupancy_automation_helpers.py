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
    def test_occupancy_update_triggers(self):
        self.assertEqual(
            occupancy_automation_helpers.occupancy_update_triggers(
                "group.kitchen_motion",
                10,
                20,
                30,
                40,
                [{"platform": "time_pattern", "minutes": "/3"}],
            ),
            [
                {
                    "entity_id": "group.kitchen_motion",
                    "platform": "state",
                    "to": "on",
                },
                {
                    "entity_id": "group.kitchen_motion",
                    "platform": "state",
                    "to": "on",
                    "for": {"seconds": 10},
                },
                {
                    "entity_id": "group.kitchen_motion",
                    "platform": "state",
                    "to": "on",
                    "for": {"seconds": 20},
                },
                {
                    "entity_id": "group.kitchen_motion",
                    "platform": "state",
                    "to": "off",
                },
                {
                    "entity_id": "group.kitchen_motion",
                    "platform": "state",
                    "to": "off",
                    "for": {"seconds": 30},
                },
                {
                    "entity_id": "group.kitchen_motion",
                    "platform": "state",
                    "to": "off",
                    "for": {"seconds": 40},
                },
                {"platform": "time_pattern", "minutes": "/3"},
            ],
        )

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

    def test_occupancy_override_from_timer_automation(self):
        automation = occupancy_automation_helpers.occupancy_override_from_timer_automation(
            "Kitchen ",
            "Kitchen",
            True,
            "input_boolean.kitchen_occupancy_override",
            "timer.kitchen_occupancy_override",
            [{"platform": "time_pattern", "minutes": "/10"}],
        )

        self.assertEqual(
            automation["alias"],
            "ZOc-Kitchen Occupancy Override Sync from Timer-Kitchen",
        )
        self.assertEqual(automation["mode"], "single")
        self.assertTrue(automation["configured"])
        self.assertEqual(
            automation["trigger"],
            [
                {
                    "platform": "state",
                    "entity_id": "timer.kitchen_occupancy_override",
                },
                {"platform": "time_pattern", "minutes": "/10"},
            ],
        )
        choose = automation["action"][0]["choose"]
        self.assertEqual(
            choose[0],
            {
                "conditions": [
                    {
                        "condition": "state",
                        "entity_id": "timer.kitchen_occupancy_override",
                        "state": "active",
                    }
                ],
                "sequence": [
                    {
                        "service": "input_boolean.turn_on",
                        "target": {
                            "entity_id": "input_boolean.kitchen_occupancy_override"
                        },
                    }
                ],
            },
        )
        self.assertEqual(
            choose[1],
            {
                "conditions": [
                    {
                        "condition": "or",
                        "conditions": [
                            {
                                "condition": "state",
                                "entity_id": "timer.kitchen_occupancy_override",
                                "state": "paused",
                            },
                            {
                                "condition": "state",
                                "entity_id": "timer.kitchen_occupancy_override",
                                "state": "idle",
                            },
                        ],
                    }
                ],
                "sequence": [
                    {
                        "service": "input_boolean.turn_off",
                        "target": {
                            "entity_id": "input_boolean.kitchen_occupancy_override"
                        },
                    }
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
