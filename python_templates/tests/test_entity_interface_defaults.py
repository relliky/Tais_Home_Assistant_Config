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

    def test_build_entity_declarations(self):
        values = {
            "al_light_list": [{"name": "Adaptive"}],
            "automation_list": [{"alias": "Automation"}],
            "input_select_dict": {"scene": {}},
            "input_boolean_dict": {"flag": {}},
            "input_datetime_dict": {"time": {}},
            "input_number_dict": {"number": {}},
            "sensor_list": [{"name": "Sensor"}],
            "timer_dict": {"timer": {}},
            "button_list": [{"name": "Button"}],
            "switch_list": [{"name": "Switch"}],
            "cover_list": [{"name": "Cover"}],
            "climate_list": [{"name": "Climate"}],
            "template_list": [{"sensor": []}],
            "binary_sensor_list": [{"name": "Binary"}],
            "event_list": [{"name": "Event"}],
            "lock_list": [{"name": "Lock"}],
            "light_list": [{"name": "Light"}],
            "group_dict": {"group": {}},
        }

        declarations = entity_interface_defaults.build_entity_declarations(**values)

        self.assertEqual(
            list(declarations.keys()),
            [
                "adaptive_lighting",
                "automation",
                "input_select",
                "input_boolean",
                "input_datetime",
                "input_number",
                "sensor",
                "timer",
                "button",
                "switch",
                "cover",
                "climate",
                "template",
                "binary_sensor",
                "event",
                "lock",
                "light",
                "group",
            ],
        )
        self.assertIs(declarations["automation"], values["automation_list"])
        self.assertIs(declarations["group"], values["group_dict"])


if __name__ == "__main__":
    unittest.main()
