import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import room_remote_entities


class RoomRemoteEntitiesTest(unittest.TestCase):
    def test_no_xiaomi_buttons(self):
        entities = room_remote_entities.default_remote_entities("master_room", 0)

        self.assertEqual(entities["xiaomi_buttons"], [])
        self.assertEqual(
            entities["wall_buttons"],
            [
                "sensor.master_room_wall_button",
                "sensor.master_room_wall_button_2",
            ],
        )
        self.assertEqual(entities["buttons"], entities["wall_buttons"])

    def test_single_xiaomi_button_has_no_number_suffix(self):
        entities = room_remote_entities.default_remote_entities("master_room", 1)

        self.assertEqual(entities["xiaomi_buttons"], ["sensor.master_room_button"])
        self.assertEqual(
            entities["buttons"],
            [
                "sensor.master_room_wall_button",
                "sensor.master_room_wall_button_2",
                "sensor.master_room_button",
            ],
        )

    def test_multiple_xiaomi_buttons_are_numbered(self):
        entities = room_remote_entities.default_remote_entities("study", 3)

        self.assertEqual(
            entities["xiaomi_buttons"],
            [
                "sensor.study_button_1",
                "sensor.study_button_2",
                "sensor.study_button_3",
            ],
        )

    def test_default_wall_switches(self):
        self.assertEqual(
            room_remote_entities.default_wall_switches(),
            {
                "wall_switches": [],
                "decouple_wall_switches": [],
                "raw_wall_switches": [],
                "alias_wall_switches": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
