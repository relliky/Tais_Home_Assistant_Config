import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import room_time_settings


class RoomTimeSettingsTest(unittest.TestCase):
    def test_default_sleep_time_entities(self):
        self.assertEqual(
            room_time_settings.default_sleep_time_entities(),
            {
                "end_of_sleep_time": "06:30:00",
                "start_of_sleep_time": "23:00:00",
            },
        )

    def test_bedroom_light_time_settings(self):
        settings = room_time_settings.default_light_time_settings("bedroom")

        self.assertEqual(settings["daytime_lights_off_timeout"], "00:15:00")
        self.assertEqual(settings["nighttime_lights_off_timeout"], "02:00:00")
        self.assertEqual(settings["daytime_start"], "06:00:00")
        self.assertEqual(settings["afternoon_start"], "13:00:00")
        self.assertEqual(settings["daytime_end"], "21:00:00")

    def test_common_area_night_timeout_matches_daytime(self):
        settings = room_time_settings.default_light_time_settings("common_area")

        self.assertEqual(settings["daytime_lights_off_timeout"], "00:15:00")
        self.assertEqual(settings["nighttime_lights_off_timeout"], "00:15:00")


if __name__ == "__main__":
    unittest.main()
