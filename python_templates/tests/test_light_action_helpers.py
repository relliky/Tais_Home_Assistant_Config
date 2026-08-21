import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import light_action_helpers


def set_service(entity_id, state=None, light_brightness=None):
    return ["set", entity_id, state, light_brightness]


def continue_if(entity_id, state):
    return ["continueIf", entity_id, state]


def continue_if_with_attribute(entity_id, state, attribute=None):
    return ["continueIf", entity_id, state, attribute]


class LightActionHelpersTest(unittest.TestCase):
    def test_wall_switch_turn_on_reset_sequence(self):
        self.assertEqual(
            light_action_helpers.wall_switch_turn_on_reset_sequence(
                ["switch.kitchen_wall"]
            ),
            [
                {
                    "service": "homeassistant.turn_off",
                    "entity_id": ["switch.kitchen_wall"],
                },
                {"delay": {"milliseconds": 200}},
                {
                    "service": "homeassistant.turn_on",
                    "entity_id": ["switch.kitchen_wall"],
                },
            ],
        )

    def test_wall_switch_turn_on_reset_alias(self):
        self.assertEqual(
            light_action_helpers.wall_switch_turn_on_reset_alias(),
            "Everytime to turn on a wall switch, make sure to turn off it first to make sure the smart lights will be back on",
        )

    def test_turn_on_with_brightness_action(self):
        self.assertEqual(
            light_action_helpers.turn_on_with_brightness_action(
                ["light.kitchen_ceiling"],
                50,
            ),
            {
                "service": "light.turn_on",
                "entity_id": ["light.kitchen_ceiling"],
                "data": {"brightness_pct": 50},
            },
        )

    def test_light_on_off_action(self):
        self.assertEqual(
            light_action_helpers.light_on_off_action(
                ["light.kitchen_ceiling"],
                "on",
            ),
            {
                "service": "light.turn_on",
                "entity_id": ["light.kitchen_ceiling"],
            },
        )

    def test_brightness_step_action_for_led(self):
        self.assertEqual(
            light_action_helpers.brightness_step_action(
                ["light.kitchen_led"],
                34,
                set_service,
            ),
            {
                "if": [
                    {
                        "alias": "increment brightness unless it is off, set the brightness to 1 percent",
                        "condition": "state",
                        "entity_id": ["light.kitchen_led"],
                        "state": "off",
                    }
                ],
                "then": [["set", ["light.kitchen_led"], "on", None]],
                "else": {
                    "service": "light.turn_on",
                    "target": {"entity_id": ["light.kitchen_led"]},
                    "data": {"brightness_step_pct": 34},
                },
            },
        )

    def test_brightness_step_action_for_non_led_light(self):
        action = light_action_helpers.brightness_step_action(
            ["light.kitchen_ceiling"],
            -34,
            set_service,
        )

        self.assertEqual(
            action["then"],
            [["set", ["light.kitchen_ceiling"], "on", 1]],
        )
        self.assertEqual(action["else"]["data"]["brightness_step_pct"], -34)

    def test_light_cycle_entity_id(self):
        self.assertEqual(
            light_action_helpers.light_cycle_entity_id(["light.kitchen_ceiling"]),
            "light.kitchen_ceiling",
        )
        self.assertEqual(
            light_action_helpers.light_cycle_entity_id("light.kitchen_ceiling"),
            "light.kitchen_ceiling",
        )

    def test_light_cycle_action(self):
        self.assertEqual(
            light_action_helpers.light_cycle_action(
                ["light.kitchen_ceiling"],
                continue_if,
            ),
            {
                "if": ["continueIf", ["light.kitchen_ceiling"], "off"],
                "then": [
                    {
                        "service": "light.turn_on",
                        "entity_id": ["light.kitchen_ceiling"],
                        "data": {"brightness": 3},
                    }
                ],
                "else": {
                    "service": "light.turn_on",
                    "entity_id": ["light.kitchen_ceiling"],
                    "data_template": {
                        "brightness": "{% set brightness = state_attr('light.kitchen_ceiling', 'brightness') | int(0) %}"
                        "{% if brightness == 0 or is_state('light.kitchen_ceiling', 'off') %}3"
                        "{% elif brightness <= 83 %}84"
                        "{% elif brightness <= 167 %}168"
                        "{% elif brightness <= 254 %}255"
                        "{% else %}0{% endif %}"
                    },
                },
            },
        )

    def test_led_cycle_action_keeps_one_percent_first_step_with_retry(self):
        self.assertEqual(
            light_action_helpers.led_cycle_action(
                ["light.kitchen_led"],
                continue_if,
            ),
            {
                "if": ["continueIf", ["light.kitchen_led"], "off"],
                "then": [
                    {
                        "service": "light.turn_on",
                        "entity_id": ["light.kitchen_led"],
                        "data": {"brightness": 3},
                    },
                    {"delay": {"milliseconds": 1000}},
                    {
                        "if": ["continueIf", ["light.kitchen_led"], "off"],
                        "then": [
                            {
                                "service": "light.turn_on",
                                "entity_id": ["light.kitchen_led"],
                                "data": {"brightness": 3},
                            }
                        ],
                    },
                ],
                "else": {
                    "service": "light.turn_on",
                    "entity_id": ["light.kitchen_led"],
                    "data_template": {
                        "brightness": "{% set brightness = state_attr('light.kitchen_led', 'brightness') | int(0) %}"
                        "{% if brightness == 0 or is_state('light.kitchen_led', 'off') %}3"
                        "{% elif brightness <= 83 %}84"
                        "{% elif brightness <= 167 %}168"
                        "{% elif brightness <= 254 %}255"
                        "{% else %}0{% endif %}"
                    },
                },
            },
        )

    def test_light_entities_only(self):
        self.assertEqual(
            light_action_helpers.light_entities_only([
                "light.kitchen_ceiling",
                "switch.kitchen_wall",
                "light.kitchen_led",
            ]),
            ["light.kitchen_ceiling", "light.kitchen_led"],
        )

    def test_reset_lights_to_white_sequence(self):
        self.assertEqual(
            light_action_helpers.reset_lights_to_white_sequence(
                ["switch.kitchen_lamp"],
                ["light.kitchen_ceiling"],
                continue_if_with_attribute,
            ),
            [
                {
                    "service": "homeassistant.turn_on",
                    "entity_id": ["switch.kitchen_lamp"],
                },
                {"delay": "00:00:02"},
                {
                    "if": [
                        "continueIf",
                        ["light.kitchen_ceiling"],
                        "color_temp",
                        "color_mode",
                    ],
                    "then": {"service": "script.do_nothing"},
                    "else": [
                        {
                            "service": "light.turn_on",
                            "entity_id": ["light.kitchen_ceiling"],
                            "data": {"color_temp_kelvin": "3000"},
                        },
                        {"delay": "00:00:02"},
                        {
                            "service": "light.turn_off",
                            "entity_id": ["light.kitchen_ceiling"],
                        },
                        {"delay": "00:00:02"},
                        {
                            "service": "light.turn_on",
                            "entity_id": ["light.kitchen_ceiling"],
                        },
                    ],
                },
            ],
        )

    def test_reset_lights_to_white_alias(self):
        self.assertEqual(
            light_action_helpers.reset_lights_to_white_alias(),
            "Turn on lamps first and check if light color is white. Reset color lamps to white and apply adaptive lighting.",
        )
        self.assertEqual(
            light_action_helpers.light_on_off_action(
                ["light.kitchen_ceiling"],
                "off",
            ),
            {
                "service": "light.turn_off",
                "entity_id": ["light.kitchen_ceiling"],
            },
        )


if __name__ == "__main__":
    unittest.main()
