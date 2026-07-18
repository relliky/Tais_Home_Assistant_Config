import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import media_automation_helpers


def set_service(entity_id, state):
    return ["set", entity_id, state]


def continue_if(entity_id, state):
    return ["continueIf", entity_id, state]


class MediaAutomationHelpersTest(unittest.TestCase):
    def test_single_device_volume_action(self):
        self.assertEqual(
            media_automation_helpers.single_device_volume_action(
                ["media_player.kitchen_sonos"],
                3,
            ),
            {
                "service": "media_player.volume_set",
                "entity_id": ["media_player.kitchen_sonos"],
                "data_template": {
                    "volume_level": "{{ (state_attr('media_player.kitchen_sonos', 'volume_level')) + 0.03 }}"
                },
            },
        )

    def test_media_play_pause_action_on(self):
        self.assertEqual(
            media_automation_helpers.media_play_pause_action(
                ["media_player.kitchen_sonos"],
                "on",
                continue_if,
                set_service,
            ),
            {
                "if": ["continueIf", ["media_player.kitchen_sonos"], "paused"],
                "then": ["set", ["media_player.kitchen_sonos"], "toggle"],
            },
        )

    def test_media_play_pause_action_off(self):
        self.assertEqual(
            media_automation_helpers.media_play_pause_action(
                ["media_player.kitchen_sonos"],
                "off",
                continue_if,
                set_service,
            ),
            {
                "if": ["continueIf", ["media_player.kitchen_sonos"], "playing"],
                "then": ["set", ["media_player.kitchen_sonos"], "toggle"],
            },
        )

    def test_media_play_pause_action_toggle(self):
        self.assertEqual(
            media_automation_helpers.media_play_pause_action(
                ["media_player.kitchen_sonos"],
                "toggle",
                continue_if,
                set_service,
            ),
            {
                "service": "media_player.media_play_pause",
                "entity_id": ["media_player.kitchen_sonos"],
            },
        )

    def test_media_play_pause_action_unsupported_state(self):
        self.assertEqual(
            media_automation_helpers.media_play_pause_action(
                ["media_player.kitchen_sonos"],
                "unsupported",
                continue_if,
                set_service,
            ),
            {"service": "script.do_nothing"},
        )

    def test_left_room_media_pause_delay(self):
        self.assertEqual(
            media_automation_helpers.left_room_media_pause_delay("corridor"),
            "00:10:00",
        )
        self.assertEqual(
            media_automation_helpers.left_room_media_pause_delay("kitchen"),
            "00:00:01",
        )

    def test_sonos_pause_after_people_left_automation(self):
        automation = media_automation_helpers.sonos_pause_after_people_left_automation(
            "Kitchen ",
            "Kitchen",
            "kitchen",
            "input_select.kitchen_occupancy",
            ["media_player.kitchen_sonos"],
            [{"platform": "time_pattern", "minutes": "/30"}],
            set_service,
        )

        self.assertEqual(
            automation["alias"],
            "ZM-Kitchen Sonos Pause Playing After People Left-Kitchen",
        )
        self.assertTrue(automation["configured"])
        self.assertEqual(
            automation["trigger"],
            [
                {
                    "platform": "state",
                    "entity_id": "input_select.kitchen_occupancy",
                    "to": "Outside",
                    "for": "00:00:01",
                },
                {"platform": "time_pattern", "minutes": "/30"},
            ],
        )
        self.assertEqual(
            automation["action"],
            [
                {
                    "condition": "state",
                    "entity_id": "input_select.kitchen_occupancy",
                    "state": "Outside",
                    "for": "00:00:01",
                },
                ["set", ["media_player.kitchen_sonos"], "off"],
            ],
        )

    def test_sonos_pause_after_people_left_automation_for_corridor(self):
        automation = media_automation_helpers.sonos_pause_after_people_left_automation(
            "Ground Corridor ",
            "Ground Corridor",
            "corridor",
            "input_select.ground_corridor_occupancy",
            [],
            [],
            set_service,
        )

        self.assertFalse(automation["configured"])
        self.assertEqual(automation["trigger"][0]["for"], "00:10:00")
        self.assertEqual(automation["action"][0]["for"], "00:10:00")


if __name__ == "__main__":
    unittest.main()
