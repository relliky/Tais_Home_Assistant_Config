import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import scene_action_helpers


LAMPS = ["switch.kitchen_lamp"]
CEILING_LIGHTS = ["light.kitchen_ceiling"]
LEDS = ["light.kitchen_led"]
TVS = ["media_player.kitchen_tv"]


def set_service(entity_id, state=None, tv_brightness=None):
    return ["set", entity_id, state, tv_brightness]


class SceneActionHelpersTest(unittest.TestCase):
    def test_all_white_scene_actions(self):
        self.assertEqual(
            scene_action_helpers.simple_room_scene_actions(
                "All White",
                LAMPS,
                CEILING_LIGHTS,
                LEDS,
                TVS,
                "kitchen",
                set_service,
            ),
            (
                [
                    ["set", LAMPS, "on", None],
                    ["set", CEILING_LIGHTS, "on", None],
                    ["set", LEDS, "on", None],
                    ["set", TVS, None, 3],
                ],
                True,
            ),
        )

    def test_hue_scene_actions_disable_parallel_wrapper(self):
        actions, parallel_enable = scene_action_helpers.simple_room_scene_actions(
            "Hue",
            LAMPS,
            CEILING_LIGHTS,
            LEDS,
            TVS,
            "kitchen",
            set_service,
        )

        self.assertFalse(parallel_enable)
        self.assertEqual(actions[0]["service"], "pyscript.turn_rgb_light")
        self.assertEqual(actions[0]["data"]["state"], "off")
        self.assertEqual(actions[0]["data"]["rgb"], "non_rgb_only")
        self.assertEqual(actions[1]["data"]["light_list"], LAMPS + CEILING_LIGHTS + LEDS)
        self.assertEqual(actions[2], ["set", TVS, None, 2])

    def test_scene_entity_actions(self):
        self.assertEqual(
            scene_action_helpers.simple_room_scene_actions(
                "Dark Night Mode",
                LAMPS,
                CEILING_LIGHTS,
                LEDS,
                TVS,
                "kitchen",
                set_service,
            ),
            (
                [
                    {
                        "service": "homeassistant.turn_on",
                        "entity_id": "scene.kitchen_dark_night_mode",
                    },
                    ["set", TVS, None, 1],
                ],
                True,
            ),
        )

    def test_unsupported_scene_returns_none(self):
        self.assertIsNone(
            scene_action_helpers.simple_room_scene_actions(
                "light states when low light outdoor",
                LAMPS,
                CEILING_LIGHTS,
                LEDS,
                TVS,
                "kitchen",
                set_service,
            )
        )


if __name__ == "__main__":
    unittest.main()
