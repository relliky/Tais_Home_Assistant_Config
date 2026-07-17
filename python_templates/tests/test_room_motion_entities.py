import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import room_motion_entities


def fake_id_from_alias(alias):
    return "id:" + alias


class RoomMotionEntitiesTest(unittest.TestCase):
    def test_default_bedroom_motion_sensor_entities(self):
        entities = room_motion_entities.default_motion_sensor_entities(
            "master_room",
            "bedroom",
            "Master Room",
            "M",
            fake_id_from_alias,
        )

        self.assertEqual(entities["motion_group"], "group.master_room_motion_group")
        self.assertEqual(entities["occupancy_group"], "group.master_room_occupancy_group")
        self.assertEqual(
            entities["bed_motion_sensors"],
            ["binary_sensor.master_room_bed_motion_sensor_motion"],
        )
        self.assertEqual(
            entities["entrance_motion_sensors"],
            ["binary_sensor.master_room_entrance_motion_sensor_motion"],
        )
        self.assertEqual(entities["room_occupancy"], "input_select.master_room_occupancy")
        self.assertEqual(entities["sleep_time"], "input_boolean.master_room_sleep_time")
        self.assertEqual(entities["inside_to_outside_timeout"], 5*60)
        self.assertEqual(
            entities["automation_occupancy"],
            {
                "alias": "ZOc-MOccupancy Update-Master Room",
                "id": "id:ZOc-MOccupancy Update-Master Room",
            },
        )
        self.assertEqual(entities["occupancy_state_duration"], 4)
        self.assertEqual(entities["occupancy_on_x_min_ratio_sensor"], "unitialized_ratio_sensor")
        self.assertEqual(entities["set_to_outside_when_no_motion"], "no")
        self.assertEqual(
            entities["occupancy_override_entity"],
            "input_boolean.master_room_auto_off_suspended",
        )
        self.assertEqual(
            entities["occupancy_override_timer_entity"],
            "timer.master_room_auto_off_suspended_timer",
        )
        self.assertEqual(entities["occupancy_override_default_timeout"], "02:00:00")

    def test_default_non_bedroom_motion_sensor_entities(self):
        entities = room_motion_entities.default_motion_sensor_entities(
            "corridor",
            "landing",
            "Corridor",
            "Co",
            fake_id_from_alias,
        )

        self.assertEqual(entities["bed_motion_sensors"], [])
        self.assertEqual(entities["entrance_motion_sensors"], ["group.corridor_motion_group"])
        self.assertEqual(entities["sleep_time"], "input_boolean.always_off_constant")
        self.assertEqual(entities["inside_to_outside_timeout"], 1*60)


if __name__ == "__main__":
    unittest.main()
