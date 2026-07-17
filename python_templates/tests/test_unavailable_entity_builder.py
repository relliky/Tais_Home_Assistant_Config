import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import unavailable_entity_builder


class UnavailableEntityBuilderTest(unittest.TestCase):
    def test_collect_added_device_entities(self):
        entities = unavailable_entity_builder.collect_added_device_entities(
            template_list=[
                {
                    "sensor": [
                        {"name": "Master Temperature"},
                    ],
                    "binary_sensor": [
                        {"name": "Master Motion"},
                    ],
                    "trigger": [{"platform": "state"}],
                    "configured": True,
                },
                {
                    "sensor": [
                        {"name": "Ignored Sensor"},
                    ],
                    "configured": False,
                },
            ],
            binary_sensor_list=[
                {"name": "Room Occupancy-", "configured": True},
                {"name": "Ignored Binary", "configured": False},
            ],
            switch_list=[{"name": "Fan Switch", "configured": True}],
            cover_list=[{"name": "Main Cover", "configured": True}],
            lock_list=[{"name": "Door Lock", "configured": True}],
            event_list=[{"name": "Button Event", "configured": True}],
            light_list=[{"name": "Ceiling Light", "configured": True}],
        )

        self.assertEqual(
            entities,
            [
                "sensor.master_temperature",
                "binary_sensor.master_motion",
                "binary_sensor.room_occupancy",
                "switch.fan_switch",
                "cover.main_cover",
                "lock.door_lock",
                "event.button_event",
                "light.ceiling_light",
            ],
        )


if __name__ == "__main__":
    unittest.main()
