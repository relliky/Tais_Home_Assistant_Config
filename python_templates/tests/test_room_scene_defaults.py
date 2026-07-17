import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import room_scene_defaults


class RoomSceneDefaultsTest(unittest.TestCase):
    def test_default_post_room_config_without_group_auto(self):
        self.assertEqual(
            room_scene_defaults.default_post_room_config("master_room", False),
            {
                "room_scene_ctl": "input_select.master_room_scene",
                "cur_scene": "unintialized_cur_scene",
            },
        )

    def test_default_post_room_config_with_group_auto(self):
        self.assertEqual(
            room_scene_defaults.default_post_room_config("master_room", True),
            {
                "room_scene_ctl": "input_select.master_room_scene",
                "cur_scene": "unintialized_cur_scene",
                "gui_ctl_group": "group.master_room_auto_gen_automations",
            },
        )


if __name__ == "__main__":
    unittest.main()
