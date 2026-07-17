import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import room_light_entities


class RoomLightEntitiesTest(unittest.TestCase):
    def test_default_light_entities_without_adaptive_lighting(self):
        entities = room_light_entities.default_light_entities(
            "master_room",
            "Master Room",
            1,
            False,
        )

        self.assertEqual(entities["ceiling_lights"], ["light.master_room_ceiling_light"])
        self.assertEqual(entities["lamps"], ["light.master_room_lamp"])
        self.assertEqual(
            entities["lights"],
            ["light.master_room_lamp", "light.master_room_ceiling_light"],
        )
        self.assertEqual(entities["light_group"], "group.master_room_light_group")
        self.assertEqual(entities["screen_leds"], [])
        self.assertEqual(entities["extractor"], [])
        self.assertEqual(
            entities["al_sleep_mode"],
            "switch.adaptive_lighting_sleep_mode_master_room",
        )
        self.assertEqual(
            entities["al_adapt_brightness"],
            "switch.adaptive_lighting_adapt_brightness_master_room",
        )
        self.assertEqual(entities["al_light_list_additions"], [])

    def test_multiple_lamps_are_numbered(self):
        entities = room_light_entities.default_light_entities(
            "living_room",
            "Living Room",
            3,
            False,
        )

        self.assertEqual(
            entities["lamps"],
            [
                "light.living_room_lamp_1",
                "light.living_room_lamp_2",
                "light.living_room_lamp_3",
            ],
        )

    def test_adaptive_lighting_config(self):
        entities = room_light_entities.default_light_entities(
            "study",
            "Study",
            0,
            True,
        )

        self.assertEqual(len(entities["al_light_list_additions"]), 1)
        config = entities["al_light_list_additions"][0]
        self.assertEqual(config["configured"], True)
        self.assertEqual(config["name"], "Study")
        self.assertEqual(config["min_sunset_time"], "17:30")
        self.assertEqual(config["take_over_control"], True)
        self.assertEqual(config["separate_turn_on_commands"], False)
        self.assertEqual(config["include_config_in_attributes"], False)

    def test_default_lighting_control_entities_for_west_facing_room(self):
        entities = room_light_entities.default_lighting_control_entities(
            "master_room",
            True,
        )

        self.assertEqual(
            entities["ceiling_light_control_when"]["intense light summer"],
            "input_boolean.ceiling_light_control_intense_light_summer_master_room",
        )
        self.assertEqual(
            entities["lamp_control_when"]["sleep mode"],
            "input_boolean.lamp_control_sleep_mode_master_room",
        )
        self.assertEqual(
            entities["light_intensity_threshold_when"],
            {
                "intense light summer": "input_number.intensity_threshold_intense_light_summer_master_room",
                "moderate light outdoor": "input_number.intensity_threshold_moderate_light_outdoor_master_room",
            },
        )
        self.assertEqual(entities["light_intensity_entity"], "sensor.master_room_light_intensity")
        self.assertEqual(entities["noon_time"], "input_datetime.noon_time_master_room")
        self.assertEqual(entities["time_controls"], [])
        self.assertEqual(entities["light_sensor"], "sensor.master_room_west_side_light_sensor")
        self.assertEqual(entities["min_value_as_bright"], "input_number.master_room_min_value_as_bright")
        self.assertEqual(
            entities["light_sensor_controls"],
            ["sensor.master_room_west_side_light_sensor"],
        )
        self.assertEqual(
            entities["gui_ctl_entity_list_additions"],
            [
                "input_number.intensity_threshold_intense_light_summer_master_room",
                "input_number.intensity_threshold_moderate_light_outdoor_master_room",
                "sensor.master_room_light_intensity",
            ],
        )

    def test_default_lighting_control_entities_for_non_west_facing_room(self):
        entities = room_light_entities.default_lighting_control_entities(
            "kitchen",
            False,
        )

        self.assertEqual(entities["light_intensity_entity"], "sensor.living_room_light_intensity")
        self.assertEqual(entities["light_sensor"], "sensor.living_room_east_side_light_sensor")


if __name__ == "__main__":
    unittest.main()
