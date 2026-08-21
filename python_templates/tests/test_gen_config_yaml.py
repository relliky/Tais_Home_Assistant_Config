import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import gen_config_yaml
import rooms


class RoomBaseHelpersTest(unittest.TestCase):
    def setUp(self):
        self.room = gen_config_yaml.RoomBase.__new__(gen_config_yaml.RoomBase)

    def test_get_entity_from_name_normalizes(self):
        self.assertEqual(
            self.room.getEntityFromName("Master Room"),
            "master_room",
        )
        self.assertEqual(
            self.room.getEntityFromName("  Living-Room!!  "),
            "living_room",
        )
        self.assertEqual(
            self.room.getEntityFromName("Kitchen___Zone"),
            "kitchen_zone",
        )

    def test_get_id_from_alias(self):
        alias = "ZL- Master Room Lights On"
        self.assertEqual(
            self.room.getIDFromAlias(alias),
            "automation.zl_master_room_lights_on",
        )

    def test_captilize_sentence(self):
        self.assertEqual(
            self.room.captilizeSentence("hello world"),
            "Hello World",
        )
        self.assertEqual(
            self.room.captilizeSentence("  hello world"),
            "  Hello World",
        )

    def test_get_name_from_entity(self):
        entity = "light.master_room_ceiling_light"
        self.assertEqual(
            self.room.getNameFromEntity(entity),
            "Master Room Ceiling Light",
        )

    def test_time_pattern_trigger_structure(self):
        triggers = self.room.get_time_pattern_trigger(minutes=15, ha_start_trigger=True)
        self.assertEqual(len(triggers), 2)
        self.assertEqual(triggers[0]["trigger"], "homeassistant")
        self.assertEqual(triggers[0]["event"], "start")
        self.assertEqual(triggers[1]["trigger"], "time_pattern")
        self.assertEqual(triggers[1]["minutes"], "/15")
        self.assertTrue(triggers[1]["seconds"].isdigit())

        triggers_no_start = self.room.get_time_pattern_trigger(minutes=10, ha_start_trigger=False)
        self.assertEqual(len(triggers_no_start), 1)
        self.assertEqual(triggers_no_start[0]["trigger"], "time_pattern")
        self.assertEqual(triggers_no_start[0]["minutes"], "/10")

    def make_navigation_room(self):
        room = gen_config_yaml.RoomBase.__new__(gen_config_yaml.RoomBase)
        room.room_icon = "mdi:fridge"
        room.room_name = "Kitchen"
        room.temperature_sensor = "sensor.kitchen_temperature"
        room.motion_group = "group.kitchen_motion"
        room.unavailable_entity = "binary_sensor.kitchen_unavailable"
        room.room_battery_entity_list = []
        room.room_low_battery_entity = "binary_sensor.kitchen_low_battery"
        room.room_battery_entity = "group.kitchen_battery"
        room.windows = []
        room.window_group = "group.kitchen_window"
        room.tvs = []
        room.lights = []
        room.light_group = "group.kitchen_light"
        room.cfg_occupancy_override = False
        room.occupancy_override_entity = "input_boolean.kitchen_override"
        room.cfg_temp_control = False
        room.thermostat = "climate.kitchen"
        room.cfg_occupancy = False
        room.room_occupancy = "input_select.kitchen_occupancy"
        room.curtains = []
        room.curtain_group = "cover.kitchen_curtain"
        room.dashboard_view_path = "lovelace/kitchen"
        room.getTemplateCard = lambda **kwargs: kwargs
        room.getPostfix = lambda motion_group: "kitchen_motion"
        room.getCardModColor = lambda color: {"card_mod": {"style": color}}
        return room

    def test_get_mushroom_navigation_room_card(self):
        room = self.make_navigation_room()

        card = room.getMushroomNavigationRoomCard()

        self.assertEqual(card["type"], "custom:stack-in-card")
        self.assertEqual(card["mode"], "vertical")
        self.assertEqual(card["cards"][0]["primary"], "Kitchen")
        self.assertEqual(card["cards"][1]["mode"], "horizontal")
        self.assertEqual(
            card["cards"][1]["cards"][0]["condition_entity"],
            "binary_sensor.kitchen_unavailable",
        )

    def test_get_button_navigation_room_card(self):
        room = self.make_navigation_room()

        card = room.getButtonNavigationRoomCard()

        self.assertEqual(card["type"], "custom:button-card")
        self.assertEqual(card["name"], "Kitchen")
        self.assertEqual(card["icon"], "mdi:fridge")
        self.assertEqual(card["tap_action"]["navigation_path"], "lovelace/kitchen")

    def test_get_navigation_room_card_type_defaults_to_mushroom(self):
        self.assertEqual(
            self.room.getNavigationRoomCardType(),
            gen_config_yaml.NAVIGATION_ROOM_CARD_TYPE_MUSHROOM,
        )

    def test_navigation_room_card_type_constants(self):
        self.assertEqual(
            gen_config_yaml.NAVIGATION_ROOM_CARD_TYPE_MUSHROOM,
            "mushroom",
        )
        self.assertEqual(gen_config_yaml.NAVIGATION_ROOM_CARD_TYPE_BUTTON, "button")

    def test_get_navigation_room_card_rejects_unknown_type(self):
        room = self.make_navigation_room()
        room.getNavigationRoomCardType = lambda: "unknown"

        with self.assertRaises(TypeError):
            room.getNavigationRoomCard()

    def test_restricted_access_method_wraps_card(self):
        inner_card = {"type": "button"}

        card = self.room.getRestrictedAccess("us", inner_card)

        self.assertEqual(card["type"], "custom:restriction-card")
        self.assertIs(card["card"], inner_card)

    def test_misspelled_restriced_access_method_is_compatible(self):
        inner_card = {"type": "button"}

        card = self.room.getRestricedAccess("us", inner_card)

        self.assertEqual(card["type"], "custom:restriction-card")
        self.assertIs(card["card"], inner_card)

    def test_system_navigation_room_card_uses_base_wrapper(self):
        system_class = rooms.define_room_classes(gen_config_yaml.RoomBase)["System"]
        room = system_class.__new__(system_class)
        room.getTemplateCard = lambda **kwargs: kwargs
        room.getCardModColor = lambda color: {"card_mod": {"style": color}}

        card = room.getNavigationRoomCard()

        self.assertEqual(card["type"], "custom:restriction-card")
        inner_card = card["card"]
        self.assertEqual(inner_card["type"], "custom:stack-in-card")
        self.assertEqual(inner_card["mode"], "vertical")
        self.assertEqual(inner_card["cards"][0]["primary"], "System")
        self.assertEqual(inner_card["cards"][1]["mode"], "horizontal")
        self.assertEqual(
            inner_card["cards"][1]["cards"][0]["tap_entity"],
            "switch.gaming_pc",
        )

    def test_master_room_balcony_wall_light_auto_off(self):
        master_room_class = rooms.define_room_classes(gen_config_yaml.RoomBase)["MasterRoom"]
        room = master_room_class()

        automation = next(
            automation
            for automation in room.automation_list
            if automation["alias"]
            == "ZL-MR Balcony Wall Light Off If On For 4 Hours-Master Room"
        )

        self.assertEqual(
            automation["trigger"],
            [
                {
                    "platform": "state",
                    "entity_id": "switch.master_room_balcony_wall_light",
                    "from": "off",
                    "to": "on",
                    "for": "04:00:00",
                }
            ],
        )
        self.assertEqual(
            automation["action"],
            [
                {
                    "service": "homeassistant.turn_off",
                    "target": {"entity_id": "switch.master_room_balcony_wall_light"},
                }
            ],
        )

    def make_device_room(self):
        room = gen_config_yaml.RoomBase.__new__(gen_config_yaml.RoomBase)
        room.initialize_entity_intf()
        room.room_name = "Kitchen"
        room.automation_room_name = "KI-"
        return room

    def test_add_generic_switch(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_fan",
            "Kitchen Fan",
            "",
            "Generic Switch",
        )

        self.assertEqual(
            room.switch_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Fan",
                    "entities": "switch.kitchen_fan",
                    "configured": True,
                }
            ],
        )

    def test_add_mi_power_plug_zigbee_switch(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_plug",
            "Kitchen Plug",
            "",
            "Mi Power Plug ZigBee",
        )

        self.assertEqual(
            room.switch_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Plug",
                    "entities": "switch.kitchen_plug_plug",
                    "configured": True,
                }
            ],
        )

    def test_add_generic_light(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_ceiling",
            "Kitchen Ceiling",
            "",
            "Generic Light",
        )

        self.assertEqual(
            room.light_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Ceiling",
                    "entities": "light.kitchen_ceiling",
                    "configured": True,
                }
            ],
        )

    def test_add_tradfri_z2m_light(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_spot",
            "Kitchen Spot",
            "",
            "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum",
            integration="Z2M",
        )

        self.assertEqual(
            room.light_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Spot",
                    "entities": "light.kitchen_spot",
                    "configured": True,
                }
            ],
        )

    def test_add_mijia_ble_light(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_strip",
            "Kitchen Strip",
            "",
            "Mijia BLE Lights",
        )

        self.assertEqual(
            room.light_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Strip",
                    "entities": "light.kitchen_strip_light",
                    "configured": True,
                }
            ],
        )

    def test_add_generic_curtain(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_blind",
            "Kitchen Blind",
            "",
            "Generic Curtain",
        )

        self.assertEqual(
            room.cover_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Blind",
                    "entities": "cover.kitchen_blind",
                    "configured": True,
                }
            ],
        )

    def test_add_aqara_roller_shade_motor(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_blind_motor",
            "Kitchen Blind",
            "",
            "Aqara roller shade motor",
            mdi_icon="blinds",
        )

        self.assertEqual(
            room.cover_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Blind",
                    "entities": "cover.kitchen_blind_motor_motor",
                    "configured": True,
                }
            ],
        )
        self.assertEqual(
            room.customize_dict,
            {"cover.kitchen_blind": {"icon": "mdi:blinds"}},
        )
        self.assertTrue(room.aqara_shutter_blind)

    def test_add_generic_lock(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_door",
            "Kitchen Door",
            "",
            "Generic Locks",
        )

        self.assertEqual(
            room.lock_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Door",
                    "entities": "lock.kitchen_door",
                    "configured": True,
                }
            ],
        )

    def test_add_generic_event(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_scene",
            "Kitchen Scene",
            "",
            "Generic Event",
        )

        self.assertEqual(
            room.event_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Scene",
                    "entities": "event.kitchen_scene",
                    "configured": True,
                }
            ],
        )

    def test_add_generic_button(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_restart",
            "Kitchen Restart",
            "",
            "Generic Button",
        )

        self.assertEqual(
            room.button_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Restart",
                    "entities": "button.kitchen_restart",
                    "configured": True,
                }
            ],
        )

    def test_add_customized_argument_8_key_remotes(self):
        event_types = {
            "Single Click": [
                285409536,
                285409792,
                285410048,
                285410304,
                285410560,
                285410816,
                285411072,
                285411328,
            ],
            "Double Click": [
                285475072,
                285475328,
                285475584,
                285475840,
                285476096,
                285476352,
                285476608,
                285476864,
            ],
            "Long Press": [
                285540608,
                285540864,
                285541120,
                285541376,
                285541632,
                285541888,
                285542144,
                285542400,
            ],
        }

        for model in ["DEBROGLIE 8-Key Remote", "Jiuhao 8-Key Remote"]:
            with self.subTest(model=model):
                room = self.make_device_room()
                event_entity = "event.customized_event_5"

                room.add_device(
                    event_entity,
                    "Test 8-Key Remote",
                    "",
                    model,
                )

                self.assertEqual(len(room.template_list), 24)
                expected = [
                    (button_index, event_name, attribute_value)
                    for event_name, attribute_values in event_types.items()
                    for button_index, attribute_value in enumerate(attribute_values, start=1)
                ]
                for declaration, (button_index, event_name, attribute_value) in zip(
                    room.template_list, expected
                ):
                    self.assertEqual(declaration["trigger"][0]["entity_id"], event_entity)
                    self.assertEqual(
                        declaration["binary_sensor"][0]["name"],
                        f"Test 8-Key Remote Button {button_index} {event_name}",
                    )
                    self.assertEqual(
                        declaration["binary_sensor"][0]["state"],
                        f"{{{{ trigger.to_state.attributes['Customized Argument 5'] == {attribute_value} }}}}",
                    )

    def test_add_generic_binary_sensor(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_contact",
            "Kitchen Contact",
            "",
            "Generic Binary Sensor",
        )

        self.assertEqual(
            room.binary_sensor_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Contact",
                    "entities": "binary_sensor.kitchen_contact",
                    "configured": True,
                }
            ],
        )

    def test_add_generic_binary_sensor_with_device_class(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_contact",
            "Kitchen Contact",
            "",
            "Generic Binary Sensor",
            device_class="door",
        )

        self.assertEqual(
            room.binary_sensor_list,
            [
                {
                    "platform": "group",
                    "name": "Kitchen Contact",
                    "entities": "binary_sensor.kitchen_contact",
                    "configured": True,
                    "device_class": "door",
                }
            ],
        )

    def test_power_measurement_switch_requires_threshold(self):
        room = self.make_device_room()

        with self.assertRaises(TypeError) as context:
            room.add_device(
                "kitchen_power",
                "Kitchen Power",
                "",
                "Generic Power Measurement Switch",
            )

        self.assertIn(
            "Model Generic Power Measurement Switch needs power_on_threshold",
            str(context.exception),
        )
        self.assertIn("Name = Kitchen Power", str(context.exception))
        self.assertIn("MAC Address:kitchen_power", str(context.exception))

    def test_add_power_measurement_switch_with_smoothing(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_power",
            "Kitchen Power",
            "",
            "Generic Power Measurement Switch",
            power_on_threshold=1.5,
            delay_off_minute=2,
        )

        self.assertEqual(
            room.sensor_list,
            [
                {
                    "name": "Kitchen Power Smoothed",
                    "platform": "filter",
                    "entity_id": "sensor.kitchen_power",
                    "filters": {
                        "filter": "lowpass",
                        "time_constant": 5,
                        "precision": 1,
                    },
                    "configured": True,
                }
            ],
        )
        self.assertEqual(
            room.template_list,
            [
                {
                    "binary_sensor": [
                        {
                            "name": "Kitchen Power",
                            "state": (
                                '{% if states("sensor.kitchen_power_smoothed") '
                                "| float(0) | round(1) > 1.5 %} on {% else %} "
                                "off {% endif %}"
                            ),
                            "delay_off": {"minutes": 2},
                        }
                    ],
                    "configured": True,
                }
            ],
        )

    def test_add_power_measurement_switch_without_smoothing(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_power",
            "Kitchen Power",
            "",
            "Generic Power Measurement Switch",
            power_on_threshold=1.5,
            smooth_power=False,
        )

        self.assertEqual(room.sensor_list, [])
        self.assertEqual(
            room.template_list[0]["binary_sensor"][0]["state"],
            (
                '{% if states("sensor.kitchen_power") | float(0) | round(1) '
                "> 1.5 %} on {% else %} off {% endif %}"
            ),
        )

    def test_unsupported_device_model_error_includes_context(self):
        room = self.make_device_room()

        with self.assertRaises(TypeError) as context:
            room.add_device(
                "kitchen_unknown",
                "Kitchen Unknown",
                "",
                "Unknown Model",
            )

        self.assertIn(
            "Model 'Unknown Model' is not supported",
            str(context.exception),
        )
        self.assertIn("Name = 'Kitchen Unknown'", str(context.exception))
        self.assertIn("MAC Address:'kitchen_unknown'", str(context.exception))

    def test_add_generic_toggle_as_switch(self):
        room = self.make_device_room()

        room.add_device(
            "switch.kitchen_extractor",
            "Kitchen Extractor Toggle",
            "",
            "Generic Toggle As Switch",
        )

        self.assertEqual(
            room.input_boolean_dict,
            {
                "kitchen_extractor_toggle": {
                    "name": "Kitchen Extractor Toggle",
                    "configured": True,
                },
                "kitchen_extractor_toggle_assumed_state": {
                    "name": "Kitchen Extractor Toggle Assumed State",
                    "configured": True,
                },
            },
        )
        self.assertEqual(
            room.template_list,
            [
                {
                    "switch": [
                        {
                            "name": "Kitchen Extractor Toggle",
                            "state": "{{ is_state('input_boolean.kitchen_extractor_toggle', 'on') }}",
                            "turn_on": [
                                {
                                    "service": "input_boolean.turn_on",
                                    "target": {
                                        "entity_id": "input_boolean.kitchen_extractor_toggle",
                                    },
                                }
                            ],
                            "turn_off": [
                                {
                                    "service": "input_boolean.turn_off",
                                    "target": {
                                        "entity_id": "input_boolean.kitchen_extractor_toggle",
                                    },
                                }
                            ],
                        }
                    ],
                    "configured": True,
                }
            ],
        )
        self.assertEqual(
            room.automation_list,
            [
                {
                    "alias": "ZG-KI-Toggle Kitchen Extractor Toggle-Kitchen",
                    "configured": True,
                    "triggers": [
                        {
                            "trigger": "state",
                            "entity_id": "input_boolean.kitchen_extractor_toggle",
                            "from": "off",
                            "to": "on",
                        },
                        {
                            "trigger": "state",
                            "entity_id": "input_boolean.kitchen_extractor_toggle",
                            "from": "on",
                            "to": "off",
                        },
                    ],
                    "actions": [
                        {
                            "delay": {"milliseconds": 500},
                        },
                        {
                            "choose": [
                                {
                                    "conditions": [
                                        {
                                            "condition": "template",
                                            "value_template": (
                                                "{{ states('input_boolean.kitchen_extractor_toggle') != "
                                                "states('input_boolean.kitchen_extractor_toggle_assumed_state') }}"
                                            ),
                                        }
                                    ],
                                    "sequence": [
                                        {
                                            "service": "switch.toggle",
                                            "target": {
                                                "entity_id": "switch.kitchen_extractor",
                                            },
                                        },
                                        {
                                            "service": "input_boolean.toggle",
                                            "target": {
                                                "entity_id": (
                                                    "input_boolean."
                                                    "kitchen_extractor_toggle_assumed_state"
                                                ),
                                            },
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                    "mode": "queued",
                }
            ],
        )

    def test_add_generic_toggle_as_switch_accepts_bare_switch_entity(self):
        room = self.make_device_room()

        room.add_device(
            "kitchen_extractor",
            "Kitchen Extractor Toggle",
            "",
            "Generic Toggle As Switch",
        )

        self.assertEqual(
            room.automation_list[0]["actions"][1]["choose"][0]["sequence"][0][
                "target"
            ]["entity_id"],
            "switch.kitchen_extractor",
        )



def pyscript_occupancy_next_state(cur_state, motion, motion_state_lasts_for,
                                  occupancy_state_lasts_for, sleep_time_on,
                                  turn_to_outside_when_no_motion,
                                  entered_to_inside_timeout,
                                  inside_to_sleep_timeout,
                                  inside_to_outside_timeout,
                                  sleep_to_outside_timeout):
    motion_on_for = motion_state_lasts_for if motion == 'on' else 0
    motion_off_for = motion_state_lasts_for if motion == 'off' else 0
    stay_inside_for = occupancy_state_lasts_for if cur_state == 'Stayed Inside' else 0

    if cur_state == 'Outside':
        if motion == 'on':
            return 'Just Entered'
        return 'Outside'

    if cur_state == 'Just Entered':
        if motion == 'on' and motion_on_for >= entered_to_inside_timeout:
            return 'Stayed Inside'
        if motion_off_for >= inside_to_outside_timeout:
            return 'Outside'
        if turn_to_outside_when_no_motion == 'yes' and motion == 'off':
            return 'Outside'
        return 'Just Entered'

    if cur_state == 'Stayed Inside':
        if stay_inside_for > inside_to_sleep_timeout and sleep_time_on:
            return 'In Sleep'
        if motion_off_for >= inside_to_outside_timeout:
            return 'Outside'
        if turn_to_outside_when_no_motion == 'yes' and motion == 'off':
            return 'Outside'
        return 'Stayed Inside'

    if cur_state == 'In Sleep':
        if not sleep_time_on:
            return 'Stayed Inside'
        if motion_off_for > sleep_to_outside_timeout:
            return 'Outside'
        return 'In Sleep'

    return 'Uninitialized_states'


def generated_occupancy_next_state(room, cur_state, motion, motion_state_lasts_for,
                                   occupancy_state_lasts_for, sleep_time_on):
    actions = room.get_occupancy_state_machine_actions()
    choose = actions[0]['choose']

    def state_matches(entity_id, expected):
        actual = {
            room.room_occupancy: cur_state,
            room.motion_group: motion,
            room.sleep_time: 'on' if sleep_time_on else 'off',
        }[entity_id]
        return actual == expected

    def duration_matches(entity_id, expected_state, seconds, op):
        actual_state = {
            room.room_occupancy: cur_state,
            room.motion_group: motion,
        }[entity_id]
        duration = {
            room.room_occupancy: occupancy_state_lasts_for,
            room.motion_group: motion_state_lasts_for,
        }[entity_id]
        if actual_state != expected_state:
            return False
        return duration > seconds if op == '>' else duration >= seconds

    def template_matches(template):
        if "not is_state('" + room.motion_group + "', 'on')" in template:
            return motion != 'on'
        if "not is_state('" + room.sleep_time + "', 'on')" in template:
            return not sleep_time_on
        for entity_id in (room.room_occupancy, room.motion_group):
            for expected_state in ('on', 'off', 'Stayed Inside'):
                marker = "is_state('" + entity_id + "', '" + expected_state + "')"
                if marker in template:
                    op = '>' if ') > ' in template else '>='
                    seconds = int(template.rsplit(' ', 2)[1])
                    return duration_matches(entity_id, expected_state, seconds, op)
        raise AssertionError('Unsupported template condition: ' + template)

    def condition_matches(condition):
        if condition['condition'] == 'state':
            return state_matches(condition['entity_id'], condition['state'])
        if condition['condition'] == 'template':
            return template_matches(condition['value_template'])
        raise AssertionError('Unsupported condition: ' + str(condition))

    for branch in choose:
        if all(condition_matches(c) for c in branch['conditions']):
            sequence = branch['sequence']
            return sequence[0]['data']['option']

    return None


class OccupancyStateMachineGenerationTest(unittest.TestCase):
    def make_room(self, turn_to_outside_when_no_motion='no'):
        room = gen_config_yaml.RoomBase.__new__(gen_config_yaml.RoomBase)
        room.room_occupancy = 'input_select.test_room_occupancy'
        room.motion_group = 'group.test_room_motion_group'
        room.sleep_time = 'input_boolean.test_room_sleep_time'
        room.set_to_outside_when_no_motion = turn_to_outside_when_no_motion
        room.entered_to_inside_timeout = 150
        room.inside_to_sleep_timeout = 1800
        room.inside_to_outside_timeout = 300
        room.sleep_to_outside_timeout = 3600
        return room

    def assert_generated_matches_pyscript(self, case, turn_to_outside_when_no_motion='no'):
        room = self.make_room(turn_to_outside_when_no_motion)
        expected = pyscript_occupancy_next_state(
            turn_to_outside_when_no_motion=turn_to_outside_when_no_motion,
            entered_to_inside_timeout=room.entered_to_inside_timeout,
            inside_to_sleep_timeout=room.inside_to_sleep_timeout,
            inside_to_outside_timeout=room.inside_to_outside_timeout,
            sleep_to_outside_timeout=room.sleep_to_outside_timeout,
            **case,
        )
        actual = generated_occupancy_next_state(room, **case)
        self.assertEqual(actual, expected, case)

    def test_generated_automation_matches_pyscript_state_machine(self):
        cases = [
            dict(cur_state='Outside', motion='on', motion_state_lasts_for=1, occupancy_state_lasts_for=100, sleep_time_on=False),
            dict(cur_state='Outside', motion='off', motion_state_lasts_for=1000, occupancy_state_lasts_for=100, sleep_time_on=False),
            dict(cur_state='Just Entered', motion='on', motion_state_lasts_for=149, occupancy_state_lasts_for=20, sleep_time_on=False),
            dict(cur_state='Just Entered', motion='on', motion_state_lasts_for=150, occupancy_state_lasts_for=20, sleep_time_on=False),
            dict(cur_state='Just Entered', motion='off', motion_state_lasts_for=299, occupancy_state_lasts_for=20, sleep_time_on=False),
            dict(cur_state='Just Entered', motion='off', motion_state_lasts_for=300, occupancy_state_lasts_for=20, sleep_time_on=False),
            dict(cur_state='Stayed Inside', motion='on', motion_state_lasts_for=10, occupancy_state_lasts_for=1801, sleep_time_on=True),
            dict(cur_state='Stayed Inside', motion='on', motion_state_lasts_for=10, occupancy_state_lasts_for=1800, sleep_time_on=True),
            dict(cur_state='Stayed Inside', motion='off', motion_state_lasts_for=299, occupancy_state_lasts_for=100, sleep_time_on=False),
            dict(cur_state='Stayed Inside', motion='off', motion_state_lasts_for=300, occupancy_state_lasts_for=100, sleep_time_on=False),
            dict(cur_state='In Sleep', motion='off', motion_state_lasts_for=3600, occupancy_state_lasts_for=100, sleep_time_on=True),
            dict(cur_state='In Sleep', motion='off', motion_state_lasts_for=3601, occupancy_state_lasts_for=100, sleep_time_on=True),
            dict(cur_state='In Sleep', motion='on', motion_state_lasts_for=1, occupancy_state_lasts_for=100, sleep_time_on=False),
            dict(cur_state='In Sleep', motion='on', motion_state_lasts_for=1, occupancy_state_lasts_for=100, sleep_time_on=True),
        ]
        for case in cases:
            self.assert_generated_matches_pyscript(case)

    def test_generated_automation_matches_pyscript_authoritative_no_motion_mode(self):
        cases = [
            dict(cur_state='Just Entered', motion='off', motion_state_lasts_for=1, occupancy_state_lasts_for=20, sleep_time_on=False),
            dict(cur_state='Stayed Inside', motion='off', motion_state_lasts_for=1, occupancy_state_lasts_for=100, sleep_time_on=False),
        ]
        for case in cases:
            self.assert_generated_matches_pyscript(case, turn_to_outside_when_no_motion='yes')
if __name__ == "__main__":
    unittest.main()
