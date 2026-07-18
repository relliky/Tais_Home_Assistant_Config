import os
import sys
import unittest
from unittest.mock import patch


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import automation_helpers


class AutomationHelpersTest(unittest.TestCase):
    def test_get_time_pattern_trigger_with_start(self):
        with patch("automation_helpers.random.randint", return_value=17):
            triggers = automation_helpers.get_time_pattern_trigger(minutes=15, ha_start_trigger=True)

        self.assertEqual(
            triggers,
            [
                {"trigger": "homeassistant", "event": "start"},
                {"minutes": "/15", "seconds": "17", "trigger": "time_pattern"},
            ],
        )

    def test_get_time_pattern_trigger_without_start(self):
        with patch("automation_helpers.random.randint", return_value=3):
            triggers = automation_helpers.get_time_pattern_trigger(minutes=10, ha_start_trigger=False)

        self.assertEqual(triggers, [{"minutes": "/10", "seconds": "3", "trigger": "time_pattern"}])

    def test_condition_helpers(self):
        self.assertEqual(automation_helpers.always_on_condition(), ['{{ 1 == 1 }}'])
        self.assertEqual(
            automation_helpers.entity_is_on("switch.test"),
            {"condition": "state", "entity_id": "switch.test", "state": "on"},
        )
        self.assertEqual(
            automation_helpers.continue_if("sensor.mode", "Movie", attribute="source", lastFor="00:01:00"),
            {
                "condition": "state",
                "entity_id": "sensor.mode",
                "state": "Movie",
                "attribute": "source",
                "for": "00:01:00",
            },
        )

    def test_state_duration_template_condition(self):
        condition = automation_helpers.state_duration_template_condition("binary_sensor.motion", "on", 150)

        self.assertEqual(condition["condition"], "template")
        self.assertIn("binary_sensor.motion", condition["value_template"])
        self.assertIn(">= 150", condition["value_template"])

    def test_wrap_service_sequence(self):
        service_list = [{"service": "light.turn_on", "entity_id": "light.test"}]

        self.assertEqual(
            automation_helpers.wrap_service_sequence(service_list, alias="Turn on test"),
            {"alias": "Turn on test", "if": ['{{ 1 == 1 }}'], "then": service_list},
        )

    def test_assign_automation_ids(self):
        automations = [
            {"alias": "Kitchen Lights On"},
            {"alias": "Kitchen Lights Off"},
        ]

        automation_helpers.assign_automation_ids(
            automations,
            lambda alias: "automation." + alias.lower().replace(" ", "_"),
        )

        self.assertEqual(
            automations,
            [
                {"alias": "Kitchen Lights On", "id": "automation.kitchen_lights_on"},
                {"alias": "Kitchen Lights Off", "id": "automation.kitchen_lights_off"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
