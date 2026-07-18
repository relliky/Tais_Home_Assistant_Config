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

    def test_automation_entities(self):
        self.assertEqual(
            gui_control_group.automation_entities(
                [
                    {"id": "automation.one"},
                    {"id": "automation.two"},
                ]
            ),
            ["automation.one", "automation.two"],
        )

    def test_adaptive_lighting_sleep_mode_entities(self):
        self.assertEqual(
            gui_control_group.adaptive_lighting_sleep_mode_entities(
                True,
                [{"name": "Master Room"}, {"name": "Living Room"}],
                lambda name: name.lower().replace(" ", "_"),
            ),
            [
                "switch.adaptive_lighting_sleep_mode_master_room",
                "switch.adaptive_lighting_sleep_mode_living_room",
            ],
        )
        self.assertEqual(
            gui_control_group.adaptive_lighting_sleep_mode_entities(
                False,
                [{"name": "Master Room"}],
                lambda name: name.lower().replace(" ", "_"),
            ),
            [],
        )

    def test_extra_control_entities_preserves_order(self):
        self.assertEqual(
            gui_control_group.extra_control_entities(
                wall_switches=["switch.wall"],
                decouple_wall_switches=["switch.decouple"],
                cfg_adaptive_lighting=True,
                al_light_list=[{"name": "Master Room"}],
                get_entity_from_name=lambda name: name.lower().replace(" ", "_"),
                time_controls=["input_datetime.noon"],
                light_sensor_controls=["sensor.light"],
                room_battery_entity="sensor.room_battery",
                manual_added_automations=["automation.manual"],
                windows=["binary_sensor.window"],
                window_group="group.window",
            ),
            [
                "switch.wall",
                "switch.decouple",
                "switch.adaptive_lighting_sleep_mode_master_room",
                "input_datetime.noon",
                "sensor.light",
                "sensor.room_battery",
                "automation.manual",
                "group.window",
            ],
        )

    def test_auto_group_declaration(self):
        self.assertEqual(
            gui_control_group.auto_group_declaration(
                "group.master_room_auto_gen_automations",
                ["automation.one"],
                lambda entity: entity.split(".", 1)[1],
                lambda entity: "Master Room Auto Gen Automations",
            ),
            {
                "master_room_auto_gen_automations": {
                    "name": "Master Room Auto Gen Automations",
                    "entities": ["automation.one"],
                }
            },
        )

    def test_merge_auto_group_declaration_when_enabled(self):
        entity_declarations = {"group": {"existing": {"name": "Existing", "entities": []}}}

        gui_control_group.merge_auto_group_declaration(
            entity_declarations,
            True,
            lambda: "group.master_room_auto_gen_automations",
            lambda: ["automation.one"],
            lambda entity: entity.split(".", 1)[1],
            lambda entity: "Master Room Auto Gen Automations",
        )

        self.assertEqual(
            entity_declarations["group"]["master_room_auto_gen_automations"],
            {
                "name": "Master Room Auto Gen Automations",
                "entities": ["automation.one"],
            },
        )
        self.assertIn("existing", entity_declarations["group"])

    def test_merge_auto_group_declaration_when_disabled(self):
        entity_declarations = {"group": {}}

        gui_control_group.merge_auto_group_declaration(
            entity_declarations,
            False,
            lambda: "group.master_room_auto_gen_automations",
            lambda: ["automation.one"],
            lambda entity: entity.split(".", 1)[1],
            lambda entity: "Master Room Auto Gen Automations",
        )

        self.assertEqual(entity_declarations, {"group": {}})

    def test_merge_auto_group_declaration_when_disabled_is_lazy(self):
        entity_declarations = {"group": {}}

        def fail_if_called():
            raise AssertionError("disabled merge should not read group fields")

        gui_control_group.merge_auto_group_declaration(
            entity_declarations,
            False,
            fail_if_called,
            fail_if_called,
            fail_if_called,
            fail_if_called,
        )

        self.assertEqual(entity_declarations, {"group": {}})


if __name__ == "__main__":
    unittest.main()
