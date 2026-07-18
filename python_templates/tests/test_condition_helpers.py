import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import condition_helpers


class ConditionHelpersTest(unittest.TestCase):
    def test_numeric_state_or_unavailable(self):
        self.assertEqual(
            condition_helpers.numeric_state_or_unavailable(
                "sensor.kitchen_light",
                "above",
                100,
            ),
            {
                "condition": "or",
                "conditions": [
                    {
                        "condition": "numeric_state",
                        "entity_id": "sensor.kitchen_light",
                        "above": 100,
                    },
                    {
                        "condition": "state",
                        "entity_id": "sensor.kitchen_light",
                        "state": [
                            "unavailable",
                            "unknown",
                        ],
                    },
                ],
            },
        )

    def test_sun_state_or_unavailable(self):
        self.assertEqual(
            condition_helpers.sun_state_or_unavailable("above_horizon"),
            {
                "condition": "or",
                "conditions": [
                    {
                        "condition": "state",
                        "entity_id": "sun.sun",
                        "state": "above_horizon",
                    },
                    {
                        "condition": "state",
                        "entity_id": "sun.sun",
                        "state": [
                            "unavailable",
                            "unknown",
                        ],
                    },
                ],
            },
        )

    def test_bright_day_condition_list(self):
        self.assertEqual(
            condition_helpers.bright_day_condition_list(
                "Bright morning",
                "sensor.kitchen_light",
                100,
                "before",
                "12:00:00",
            ),
            [
                {
                    "alias": "Bright morning",
                    "condition": "and",
                    "conditions": [
                        {
                            "condition": "or",
                            "conditions": [
                                {
                                    "condition": "numeric_state",
                                    "entity_id": "sensor.kitchen_light",
                                    "above": 100,
                                },
                                {
                                    "condition": "state",
                                    "entity_id": "sensor.kitchen_light",
                                    "state": [
                                        "unavailable",
                                        "unknown",
                                    ],
                                },
                            ],
                        },
                        {
                            "condition": "or",
                            "conditions": [
                                {
                                    "condition": "state",
                                    "entity_id": "sun.sun",
                                    "state": "above_horizon",
                                },
                                {
                                    "condition": "state",
                                    "entity_id": "sun.sun",
                                    "state": [
                                        "unavailable",
                                        "unknown",
                                    ],
                                },
                            ],
                        },
                        {
                            "condition": "time",
                            "before": "12:00:00",
                        },
                    ],
                }
            ],
        )

    def test_light_intensity_condition_list_for_intense_light_summer(self):
        self.assertEqual(
            condition_helpers.light_intensity_condition_list(
                "intense light summer",
                "sensor.light_intensity",
                {
                    "intense light summer": "input_number.intense_threshold",
                    "moderate light outdoor": "input_number.moderate_threshold",
                },
                "sensor.outside_temperature",
                True,
                "switch.adaptive_sleep_mode",
            ),
            [
                {
                    "condition": "template",
                    "value_template": "{{ states('sensor.light_intensity') | float(0) > states('input_number.intense_threshold') | float(0) }}",
                },
                {
                    "condition": "numeric_state",
                    "entity_id": "sensor.outside_temperature",
                    "above": "12",
                },
                {
                    "condition": "template",
                    "value_template": "{{ now().month > 4 and now().month < 9 }}",
                },
                {
                    "condition": "state",
                    "entity_id": "switch.adaptive_sleep_mode",
                    "state": "off",
                },
            ],
        )

    def test_light_intensity_condition_list_for_moderate_light(self):
        self.assertEqual(
            condition_helpers.light_intensity_condition_list(
                "moderate light outdoor",
                "sensor.light_intensity",
                {"moderate light outdoor": "input_number.moderate_threshold"},
                "sensor.outside_temperature",
                False,
                "switch.adaptive_sleep_mode",
            ),
            [
                {
                    "condition": "template",
                    "value_template": "{{ states('sensor.light_intensity') | float(0) > states('input_number.moderate_threshold') | float(0) }}",
                },
                {
                    "condition": "state",
                    "entity_id": "switch.adaptive_sleep_mode",
                    "state": "off",
                },
            ],
        )

    def test_light_intensity_condition_list_for_low_light(self):
        self.assertEqual(
            condition_helpers.light_intensity_condition_list(
                "low light outdoor",
                "sensor.light_intensity",
                {"moderate light outdoor": "input_number.moderate_threshold"},
                "sensor.outside_temperature",
                False,
                "switch.adaptive_sleep_mode",
            ),
            [
                {
                    "condition": "template",
                    "value_template": "{{ states('sensor.light_intensity') | float(0) <= states('input_number.moderate_threshold') | float(0) }}",
                },
                {
                    "condition": "state",
                    "entity_id": "switch.adaptive_sleep_mode",
                    "state": "off",
                },
            ],
        )

    def test_light_intensity_condition_list_for_sleep_mode(self):
        self.assertEqual(
            condition_helpers.light_intensity_condition_list(
                "sleep mode",
                "sensor.light_intensity",
                {"moderate light outdoor": "input_number.moderate_threshold"},
                "sensor.outside_temperature",
                False,
                "switch.adaptive_sleep_mode",
            ),
            [
                {
                    "condition": "state",
                    "entity_id": "switch.adaptive_sleep_mode",
                    "state": "on",
                }
            ],
        )

    def test_light_intensity_condition_list_returns_none_for_other_conditions(self):
        self.assertIsNone(
            condition_helpers.light_intensity_condition_list(
                "Bright morning",
                "sensor.light_intensity",
                {},
                "sensor.outside_temperature",
                False,
                "switch.adaptive_sleep_mode",
            )
        )


if __name__ == "__main__":
    unittest.main()
