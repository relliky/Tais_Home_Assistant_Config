import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import entity_naming


class EntityNamingTest(unittest.TestCase):
    def test_get_entity_from_name_normalizes(self):
        self.assertEqual(entity_naming.get_entity_from_name("Master Room"), "master_room")
        self.assertEqual(entity_naming.get_entity_from_name("  Living-Room!!  "), "living_room")
        self.assertEqual(entity_naming.get_entity_from_name("Kitchen___Zone"), "kitchen_zone")

    def test_entity_name_helpers(self):
        self.assertEqual(entity_naming.get_postfix("light.master_room_ceiling_light"), "master_room_ceiling_light")
        self.assertEqual(entity_naming.get_name_from_entity("light.master_room_ceiling_light"), "Master Room Ceiling Light")
        self.assertEqual(entity_naming.get_id_from_alias("ZL- Master Room Lights On"), "automation.zl_master_room_lights_on")

    def test_captilize_sentence_keeps_leading_spaces(self):
        self.assertEqual(entity_naming.captilize_sentence("hello world"), "Hello World")
        self.assertEqual(entity_naming.captilize_sentence("  hello world"), "  Hello World")


if __name__ == "__main__":
    unittest.main()
