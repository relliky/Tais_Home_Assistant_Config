import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import tv_automation_helpers


def set_service(entity_list, state=None, tv_brightness=None):
    return {
        "set": entity_list,
        "state": state,
        "tv_brightness": tv_brightness,
    }


class TvAutomationHelpersTest(unittest.TestCase):
    def test_picture_mode_for_brightness(self):
        self.assertEqual(tv_automation_helpers.picture_mode_for_brightness(1), "Movie")
        self.assertEqual(tv_automation_helpers.picture_mode_for_brightness("1"), "Movie")
        self.assertEqual(tv_automation_helpers.picture_mode_for_brightness(2), "Natural")
        self.assertEqual(tv_automation_helpers.picture_mode_for_brightness(3), "Standard")
        self.assertEqual(tv_automation_helpers.picture_mode_for_brightness(4), "Dynamic")
        self.assertEqual(tv_automation_helpers.picture_mode_for_brightness(9), "Dynamic")

    def test_set_picture_mode_action(self):
        self.assertEqual(
            tv_automation_helpers.set_picture_mode_action(
                ["media_player.master_room_tv"],
                "input_select.master_room_tv_picture_mode",
                3,
            ),
            {
                "if": [
                    {
                        "alias": "Set TV brightness when it is on",
                        "condition": "state",
                        "entity_id": ["media_player.master_room_tv"],
                        "state": "on",
                    }
                ],
                "then": {
                    "service": "input_select.select_option",
                    "data": {
                        "entity_id": "input_select.master_room_tv_picture_mode",
                        "option": "Standard",
                    },
                },
            },
        )

    def test_reset_picture_mode_automation_with_tvs(self):
        automation = tv_automation_helpers.reset_picture_mode_automation(
            "MR ",
            "Master Room",
            ["media_player.master_room_tv"],
            set_service,
        )

        self.assertEqual(
            automation["alias"],
            "ZTV-MR Reset Picture Mode When Turning on TV-Master Room",
        )
        self.assertTrue(automation["configured"])
        self.assertEqual(
            automation["trigger"],
            [
                {
                    "platform": "state",
                    "entity_id": ["media_player.master_room_tv"],
                    "from": "off",
                    "to": "on",
                }
            ],
        )
        self.assertEqual(
            automation["action"],
            [
                {
                    "set": ["media_player.master_room_tv"],
                    "state": None,
                    "tv_brightness": 3,
                }
            ],
        )

    def test_reset_picture_mode_automation_without_tvs(self):
        automation = tv_automation_helpers.reset_picture_mode_automation(
            "Kitchen ",
            "Kitchen",
            [],
            set_service,
        )

        self.assertFalse(automation["configured"])


if __name__ == "__main__":
    unittest.main()
