import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import service_action_helpers


def set_service(entity_id, state):
    return ["set", entity_id, state]


class ServiceActionHelpersTest(unittest.TestCase):
    def test_is_light_entity_list_for_list(self):
        self.assertTrue(
            service_action_helpers.is_light_entity_list([
                "light.kitchen_ceiling",
                "light.kitchen_led",
            ])
        )
        self.assertFalse(
            service_action_helpers.is_light_entity_list([
                "light.kitchen_ceiling",
                "switch.kitchen_wall",
            ])
        )

    def test_is_light_entity_list_for_string(self):
        self.assertTrue(
            service_action_helpers.is_light_entity_list("light.kitchen_ceiling")
        )
        self.assertFalse(
            service_action_helpers.is_light_entity_list("switch.kitchen_wall")
        )

    def test_service_action_alias_for_string(self):
        self.assertEqual(
            service_action_helpers.service_action_alias(
                "switch.kitchen_wall",
                state="on",
            ),
            "Turn switch.kitchen_wall state=on",
        )

    def test_service_action_alias_for_list(self):
        self.assertEqual(
            service_action_helpers.service_action_alias(
                ["light.kitchen_ceiling", "light.kitchen_led"],
                state="on",
                light_brightness=50,
            ),
            "Turn light.kitchen_ceiling light.kitchen_led state=on light_brightness=50",
        )

    def test_homeassistant_on_off_action(self):
        self.assertEqual(
            service_action_helpers.homeassistant_on_off_action(
                ["switch.kitchen"],
                "on",
            ),
            {
                "service": "homeassistant.turn_on",
                "entity_id": ["switch.kitchen"],
            },
        )
        self.assertEqual(
            service_action_helpers.homeassistant_on_off_action(
                ["switch.kitchen"],
                "off",
            ),
            {
                "service": "homeassistant.turn_off",
                "entity_id": ["switch.kitchen"],
            },
        )

    def test_toggle_entities_action(self):
        self.assertEqual(
            service_action_helpers.toggle_entities_action(
                ["switch.kitchen"],
                set_service,
            ),
            {
                "if": [
                    {
                        "alias": "toggle everything all together: if any entity is on, turn off all entities, otherwise turn on all entities",
                        "condition": "state",
                        "entity_id": ["switch.kitchen"],
                        "state": "on",
                        "match": "any",
                    }
                ],
                "then": ["set", ["switch.kitchen"], "off"],
                "else": ["set", ["switch.kitchen"], "on"],
            },
        )


if __name__ == "__main__":
    unittest.main()
