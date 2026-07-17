import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import battery_entity_builder


def fake_postfix(entity):
    return entity.split(".", 1)[1]


def fake_name_from_entity(entity):
    return "Name for " + entity


class BatteryEntityBuilderTest(unittest.TestCase):
    def test_battery_entities_from_templates(self):
        template_list = [
            {
                "sensor": [
                    {"name": "Master Button Battery"},
                    {"name": "Master Button Battery Median"},
                ],
                "configured": True,
            },
            {
                "trigger": [{"platform": "state"}],
                "binary_sensor": [{"name": "Ignored Battery"}],
                "configured": False,
            },
        ]

        self.assertEqual(
            battery_entity_builder.battery_entities_from_templates(template_list),
            ["sensor.master_button_battery"],
        )

    def test_build_room_battery_entities(self):
        result = battery_entity_builder.build_room_battery_entities(
            "master_room",
            [
                {
                    "sensor": [{"name": "Master Button Battery"}],
                    "configured": True,
                },
            ],
            fake_postfix,
            fake_name_from_entity,
        )

        self.assertEqual(result["room_battery_entity_list"], ["sensor.master_button_battery"])
        self.assertEqual(result["room_battery_entity"], "group.master_room_battery")
        self.assertEqual(
            result["group_dict_additions"],
            {
                "master_room_battery": {
                    "name": "Name for group.master_room_battery",
                    "entities": ["sensor.master_button_battery"],
                    "configured": True,
                },
            },
        )
        self.assertEqual(result["room_min_battery_value_entity"], "sensor.master_room_min_battery")
        self.assertEqual(result["sensor_list_additions"][0]["platform"], "min_max")
        self.assertEqual(result["sensor_list_additions"][0]["entity_ids"], ["sensor.master_button_battery"])
        self.assertEqual(result["room_low_battery_entity"], "binary_sensor.master_room_low_battery")
        self.assertIn(
            'states("sensor.master_room_min_battery")',
            result["template_list_additions"][0]["binary_sensor"][0]["state"],
        )


if __name__ == "__main__":
    unittest.main()
