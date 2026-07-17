import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import room_config_defaults


class RoomConfigDefaultsTest(unittest.TestCase):
    def test_default_room_config_values(self):
        defaults = room_config_defaults.default_room_config()

        self.assertEqual(defaults["room_entity"], "uninitialized_room_entity")
        self.assertEqual(defaults["num_of_xiaomi_button"], 0)
        self.assertEqual(defaults["num_of_lamps"], 0)
        self.assertEqual(defaults["cfg_scene"], False)
        self.assertEqual(defaults["cfg_occupancy"], False)
        self.assertEqual(defaults["cfg_occupancy_override"], True)
        self.assertEqual(defaults["cfg_tado_calibrate_uses_lan"], True)
        self.assertEqual(defaults["cfg_adaptive_lighting"], False)
        self.assertEqual(defaults["cfg_flex_switch"], False)
        self.assertEqual(defaults["room_name"], "Uninitialized_room_name")
        self.assertEqual(defaults["room_short_name"], "uninitialized_room_short_name")
        self.assertEqual(defaults["xiaomi_home_occupancy"], True)
        self.assertEqual(defaults["gateway_occupancy"], True)
        self.assertEqual(defaults["manual_added_automations"], [])

    def test_default_room_config_returns_fresh_manual_automation_list(self):
        first = room_config_defaults.default_room_config()
        second = room_config_defaults.default_room_config()

        self.assertIsNot(first["manual_added_automations"], second["manual_added_automations"])


if __name__ == "__main__":
    unittest.main()
