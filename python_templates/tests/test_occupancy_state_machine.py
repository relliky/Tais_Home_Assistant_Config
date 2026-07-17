import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import occupancy_state_machine


class OccupancyStateMachineModuleTest(unittest.TestCase):
    def make_actions(self, no_motion_mode="no"):
        return occupancy_state_machine.get_occupancy_state_machine_actions(
            room_occupancy="input_select.room_occupancy",
            motion_group="group.room_motion",
            sleep_time="input_boolean.room_sleep_time",
            set_to_outside_when_no_motion=no_motion_mode,
            entered_to_inside_timeout=150,
            inside_to_sleep_timeout=1800,
            inside_to_outside_timeout=300,
            sleep_to_outside_timeout=3600,
        )

    def test_generates_choose_action_wrapper(self):
        actions = self.make_actions()

        self.assertEqual(len(actions), 1)
        self.assertIn("choose", actions[0])
        self.assertEqual(actions[0]["default"], [{"service": "script.do_nothing"}])

    def test_no_motion_authoritative_mode_adds_extra_branches(self):
        normal_choose = self.make_actions(no_motion_mode="no")[0]["choose"]
        authoritative_choose = self.make_actions(no_motion_mode="yes")[0]["choose"]

        self.assertEqual(len(authoritative_choose), len(normal_choose) + 2)
        self.assertIn(
            "Just Entered -> Outside when no motion is authoritative",
            [branch["alias"] for branch in authoritative_choose],
        )
        self.assertIn(
            "Stayed Inside -> Outside when no motion is authoritative",
            [branch["alias"] for branch in authoritative_choose],
        )

    def test_select_actions_target_room_occupancy(self):
        first_sequence = self.make_actions()[0]["choose"][0]["sequence"]

        self.assertEqual(
            first_sequence,
            [
                {
                    "service": "input_select.select_option",
                    "target": {"entity_id": "input_select.room_occupancy"},
                    "data": {"option": "Just Entered"},
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
