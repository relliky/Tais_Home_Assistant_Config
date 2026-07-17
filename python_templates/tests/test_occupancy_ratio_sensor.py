import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import occupancy_ratio_sensor


def fake_entity_from_name(name):
    return name.lower().replace(" ", "_")


class OccupancyRatioSensorTest(unittest.TestCase):
    def test_build_occupancy_ratio_sensor_config_for_1x(self):
        result = occupancy_ratio_sensor.build_occupancy_ratio_sensor_config(
            "1x",
            4,
            "Master Room",
            "group.master_room_motion_group",
            True,
            fake_entity_from_name,
        )

        self.assertEqual(
            result["sensor_update"],
            {
                "attribute": "occupancy_on_x_min_ratio_sensor",
                "entity": "sensor.master_room_motion_on_ratio_for_last_4_minutes",
            },
        )
        self.assertEqual(
            result["ratio_sensor_config"],
            {
                "platform": "history_stats",
                "name": "Master Room Motion On Ratio For Last 4 Minutes",
                "entity_id": "group.master_room_motion_group",
                "state": "on",
                "type": "ratio",
                "duration": {
                    "minutes": "4",
                },
                "end": "{{ (now() | as_timestamp) | as_datetime | as_local }}",
                "configured": True,
            },
        )

    def test_build_occupancy_ratio_sensor_config_for_2x(self):
        result = occupancy_ratio_sensor.build_occupancy_ratio_sensor_config(
            "2x",
            4,
            "Master Room",
            "group.master_room_motion_group",
            False,
            fake_entity_from_name,
        )

        self.assertEqual(
            result["sensor_update"],
            {
                "attribute": "occupancy_on_2x_min_ratio_sensor",
                "entity": "sensor.master_room_motion_on_ratio_for_last_8_minutes",
            },
        )
        self.assertEqual(result["ratio_sensor_config"]["duration"]["minutes"], "8")
        self.assertEqual(result["ratio_sensor_config"]["configured"], False)

    def test_build_occupancy_ratio_sensor_config_for_unknown_multiple(self):
        result = occupancy_ratio_sensor.build_occupancy_ratio_sensor_config(
            "bad",
            4,
            "Master Room",
            "group.master_room_motion_group",
            True,
            fake_entity_from_name,
        )

        self.assertEqual(result["sensor_update"], {})
        self.assertEqual(
            result["ratio_sensor_config"]["name"],
            "Master Room Motion On Ratio For Last 0 Minutes",
        )
        self.assertEqual(result["ratio_sensor_config"]["duration"]["minutes"], "0")


if __name__ == "__main__":
    unittest.main()
