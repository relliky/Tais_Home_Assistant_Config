import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import room_device_defaults


class RoomDeviceDefaultsTest(unittest.TestCase):
    def test_default_mirror_entities(self):
        self.assertEqual(
            room_device_defaults.default_mirror_entities(),
            {
                "mirror_sensors": [],
                "demisters": [],
                "shower_sensors": [],
            },
        )

    def test_default_tv_entities(self):
        self.assertEqual(
            room_device_defaults.default_tv_entities(),
            {
                "tv_room_entity": None,
                "tvs": [],
                "tv_picture_mode": [],
                "tv_soundbars": [],
                "fire_tvs": [],
                "media_players": [],
            },
        )

    def test_default_cover_entities(self):
        self.assertEqual(
            room_device_defaults.default_cover_entities("master_room"),
            {
                "curtains": [],
                "aqara_shutter_blind": False,
                "curtain_group": "group.master_room_curtain_group",
            },
        )

    def test_default_window_entities(self):
        self.assertEqual(
            room_device_defaults.default_window_entities("master_room"),
            {
                "windows": [],
                "timeout_windows": [],
                "window_group": "group.master_room_window_group",
                "timeout_window_group": "group.master_room_timeout_window_group",
            },
        )


if __name__ == "__main__":
    unittest.main()
