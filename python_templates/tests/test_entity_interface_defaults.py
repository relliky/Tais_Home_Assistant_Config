import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import entity_interface_defaults


class EntityInterfaceDefaultsTest(unittest.TestCase):
    def test_default_entity_interface_keys_and_values(self):
        defaults = entity_interface_defaults.default_entity_interface()

        self.assertEqual(
            list(defaults.keys()),
            [
                "automation_list",
                "entity_declarations",
                "input_select_dict",
                "sensor_list",
                "group_dict",
                "timer_dict",
                "button_list",
                "input_boolean_dict",
                "input_datetime_dict",
                "input_number_dict",
                "script_dict",
                "switch_list",
                "cover_list",
                "template_list",
                "climate_list",
                "binary_sensor_list",
                "event_list",
                "lock_list",
                "light_list",
                "room_cards",
                "views",
                "dashboard_type",
                "header_card_list",
                "main_card_list",
                "tail_card_list",
                "al_light_list",
                "gui_ctl_entity_list",
                "customize_dict",
            ],
        )
        self.assertEqual(defaults["automation_list"], [])
        self.assertEqual(defaults["entity_declarations"], {})
        self.assertEqual(defaults["dashboard_type"], None)
        self.assertEqual(defaults["customize_dict"], {})

    def test_default_entity_interface_returns_fresh_containers(self):
        first = entity_interface_defaults.default_entity_interface()
        second = entity_interface_defaults.default_entity_interface()

        self.assertIsNot(first["automation_list"], second["automation_list"])
        self.assertIsNot(first["entity_declarations"], second["entity_declarations"])


if __name__ == "__main__":
    unittest.main()
