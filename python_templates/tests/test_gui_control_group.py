import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import gui_control_group


def control_dict(prefix):
    return {name: prefix + "_" + name.replace(" ", "_") for name in gui_control_group.SCENE_CONTROL_NAMES}


class GuiControlGroupTest(unittest.TestCase):
    def test_scene_control_entities_for_lights_only(self):
        entities = gui_control_group.scene_control_entities(
            ceiling_lights=["light.ceiling"],
            lamps=[],
            leds=["light.led"],
            curtains=[],
            ceiling_light_control_when=control_dict("ceiling"),
            lamp_control_when=control_dict("lamp"),
            led_control_when=control_dict("led"),
            curtain_control_when=control_dict("curtain"),
        )

        self.assertEqual(
            entities,
            [
                "ceiling_intense_light_summer",
                "led_intense_light_summer",
                "ceiling_moderate_light_outdoor",
                "led_moderate_light_outdoor",
                "ceiling_low_light_outdoor",
                "led_low_light_outdoor",
                "ceiling_sleep_mode",
                "led_sleep_mode",
            ],
        )

    def test_scene_control_entities_for_curtains_and_lamps(self):
        entities = gui_control_group.scene_control_entities(
            ceiling_lights=[],
            lamps=["light.lamp"],
            leds=[],
            curtains=["cover.curtain"],
            ceiling_light_control_when=control_dict("ceiling"),
            lamp_control_when=control_dict("lamp"),
            led_control_when=control_dict("led"),
            curtain_control_when=control_dict("curtain"),
        )

        self.assertEqual(
            entities,
            [
                "lamp_intense_light_summer",
                "curtain_intense_light_summer",
                "lamp_moderate_light_outdoor",
                "curtain_moderate_light_outdoor",
                "lamp_low_light_outdoor",
                "curtain_low_light_outdoor",
                "lamp_sleep_mode",
                "curtain_sleep_mode",
            ],
        )

    def test_scene_control_entities_without_devices(self):
        self.assertEqual(
            gui_control_group.scene_control_entities(
                ceiling_lights=[],
                lamps=[],
                leds=[],
                curtains=[],
                ceiling_light_control_when=control_dict("ceiling"),
                lamp_control_when=control_dict("lamp"),
                led_control_when=control_dict("led"),
                curtain_control_when=control_dict("curtain"),
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
