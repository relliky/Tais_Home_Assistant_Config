import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import room_properties


class RoomPropertiesTest(unittest.TestCase):
    def test_bedroom_properties(self):
        properties = room_properties.derive_room_properties("Master Room", "Master")

        self.assertEqual(properties["room_entity"], "master_room")
        self.assertEqual(properties["room_navi_path"], "master-room")
        self.assertEqual(properties["automation_room_name"], "Master ")
        self.assertEqual(properties["room_type"], "bedroom")
        self.assertTrue(properties["west_face_windows"])

    def test_living_room_is_common_area(self):
        properties = room_properties.derive_room_properties("Living Room", "Living")

        self.assertEqual(properties["room_entity"], "living_room")
        self.assertEqual(properties["room_type"], "common_area")
        self.assertFalse(properties["west_face_windows"])

    def test_toilet_properties(self):
        properties = room_properties.derive_room_properties("En Suite Toilet", "En Suite Toilet")

        self.assertEqual(properties["room_entity"], "en_suite_toilet")
        self.assertEqual(properties["room_type"], "toilet")
        self.assertTrue(properties["west_face_windows"])

    def test_kitchen_common_area_has_west_face_windows(self):
        properties = room_properties.derive_room_properties("Kitchen", "Kitchen")

        self.assertEqual(properties["room_type"], "common_area")
        self.assertTrue(properties["west_face_windows"])


if __name__ == "__main__":
    unittest.main()
