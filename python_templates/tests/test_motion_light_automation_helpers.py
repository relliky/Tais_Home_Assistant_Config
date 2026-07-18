import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import motion_light_automation_helpers


def condition_list_is(name):
    return ["condition", name]


def call_scene_service(name):
    return ["scene", name]


def set_service(entity, state):
    return ["set", entity, state]


def set_new_scene_state(state):
    return ["scene_state", state]


def do_nothing_service():
    return {"service": "script.do_nothing"}


def automation_turn_off(entity_id, stop_actions=False):
    return {
        "service": "automation.turn_off",
        "entity_id": entity_id,
        "data": {"stop_actions": stop_actions},
    }


class MotionLightAutomationHelpersTest(unittest.TestCase):
    def test_curtain_scene_choose(self):
        choose = motion_light_automation_helpers.curtain_scene_choose(
            condition_list_is,
            call_scene_service,
            do_nothing_service,
        )

        self.assertEqual(choose["alias"], "If it is intense light summer")
        self.assertEqual(choose["if"], ["condition", "intense light summer"])
        self.assertEqual(choose["then"], ["scene", "curtain states when intense light summer"])
        self.assertEqual(choose["else"]["alias"], "If it is moderate light outdoor")
        self.assertEqual(choose["else"]["else"]["alias"], "If it is low light outdoor")
        self.assertEqual(choose["else"]["else"]["else"]["alias"], "If it is sleep mode")
        self.assertEqual(
            choose["else"]["else"]["else"]["else"],
            {"alias": "Default", "service": "script.do_nothing"},
        )

    def test_light_scene_choose(self):
        choose = motion_light_automation_helpers.light_scene_choose(
            condition_list_is,
            call_scene_service,
            do_nothing_service,
        )

        self.assertEqual(choose["alias"], "If it is bright morning")
        self.assertEqual(choose["if"], ["condition", "intense light summer"])
        self.assertEqual(choose["then"], ["scene", "light states when intense light summer"])
        self.assertEqual(choose["else"]["alias"], "If it is bright afternoon")
        self.assertEqual(choose["else"]["else"]["alias"], "If it is bright afternoon")
        self.assertEqual(choose["else"]["else"]["else"]["alias"], "If it is bright afternoon")
        self.assertEqual(
            choose["else"]["else"]["else"]["else"],
            {"alias": "Default", "service": "script.do_nothing"},
        )

    def test_lights_off_conditions_for_bedroom(self):
        self.assertEqual(
            motion_light_automation_helpers.lights_off_conditions(
                "input_select.master_room_occupancy",
                "group.master_room_motion_group",
                "bedroom",
            ),
            [
                {
                    "condition": "state",
                    "entity_id": "input_select.master_room_occupancy",
                    "state": "Outside",
                },
                {
                    "condition": "state",
                    "entity_id": "group.master_room_motion_group",
                    "state": "off",
                    "for": "00:01:00",
                },
            ],
        )

    def test_lights_off_conditions_for_common_area(self):
        self.assertEqual(
            motion_light_automation_helpers.lights_off_conditions(
                "input_select.kitchen_occupancy",
                "group.kitchen_motion_group",
                "common_area",
            ),
            [
                {
                    "condition": "state",
                    "entity_id": "input_select.kitchen_occupancy",
                    "state": "Outside",
                },
            ],
        )

    def test_lights_off_parallel_actions(self):
        self.assertEqual(
            motion_light_automation_helpers.lights_off_parallel_actions(
                "automation.lights_on",
                ["media_player.tv"],
                ["switch.extractor"],
                set_service,
                set_new_scene_state,
                call_scene_service,
            ),
            [
                ["set", "automation.lights_on", "on"],
                ["set", ["media_player.tv"], "off"],
                ["scene_state", "Idle"],
                ["scene", "All Off"],
                ["set", ["switch.extractor"], "off"],
            ],
        )

    def test_disable_entering_lights_on_actions(self):
        self.assertEqual(
            motion_light_automation_helpers.disable_entering_lights_on_actions(
                "automation.lights_on",
                automation_turn_off,
            ),
            [
                {"delay": "00:00:10"},
                {
                    "service": "automation.turn_off",
                    "entity_id": "automation.lights_on",
                    "data": {"stop_actions": "false"},
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
