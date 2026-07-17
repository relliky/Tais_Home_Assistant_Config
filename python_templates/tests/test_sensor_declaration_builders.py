import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import sensor_declaration_builders


def fake_name_from_entity(entity):
    return "Name for " + entity


class SensorDeclarationBuildersTest(unittest.TestCase):
    def test_event_binary_sensor_with_numeric_attribute_value(self):
        self.assertEqual(
            sensor_declaration_builders.event_binary_sensor(
                "sensor.button",
                "Button Pressed",
            ),
            {
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": "sensor.button",
                        "not_from": [
                            "unknown",
                            "unavailable",
                        ],
                    },
                ],
                "binary_sensor": [
                    {
                        "name": "Button Pressed",
                        "state": "{{ trigger.to_state.attributes['Button Type'] == 1 }}",
                        "auto_off": 0.2,
                    },
                ],
                "configured": True,
            },
        )

    def test_event_binary_sensor_with_string_attribute_value(self):
        sensor = sensor_declaration_builders.event_binary_sensor(
            "sensor.button",
            "Button Pressed",
            attribute_name="action",
            attribute_value="single",
            auto_off=1.5,
        )

        self.assertEqual(
            sensor["binary_sensor"][0]["state"],
            "{{ trigger.to_state.attributes['action'] == 'single' }}",
        )
        self.assertEqual(sensor["binary_sensor"][0]["auto_off"], 1.5)

    def test_smooth_power_sensor(self):
        self.assertEqual(
            sensor_declaration_builders.smooth_power_sensor(
                "sensor.raw_power",
                "sensor.smooth_power",
                fake_name_from_entity,
            ),
            {
                "name": "Name for sensor.smooth_power",
                "platform": "filter",
                "entity_id": "sensor.raw_power",
                "filters": {
                    "filter": "lowpass",
                    "time_constant": 5,
                    "precision": 1,
                },
                "configured": True,
            },
        )

    def test_smooth_temperature_sensor(self):
        self.assertEqual(
            sensor_declaration_builders.smooth_temperature_sensor(
                "sensor.raw_temperature",
                "sensor.smooth_temperature",
                fake_name_from_entity,
            )["filters"]["time_constant"],
            4,
        )


if __name__ == "__main__":
    unittest.main()
