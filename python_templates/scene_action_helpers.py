def simple_room_scene_actions(
    scene_name,
    lamps,
    ceiling_lights,
    leds,
    tvs,
    room_entity,
    set_service,
):
  if scene_name == 'All White':
    return [
      set_service(lamps, "on"),
      set_service(ceiling_lights, "on"),
      set_service(leds, "on"),
      set_service(tvs, tv_brightness=3),
    ], True
  if scene_name == 'Ceiling Light White':
    return [
      set_service(lamps, "off"),
      set_service(leds, "off"),
      set_service(ceiling_lights, "on"),
      set_service(tvs, tv_brightness=3),
    ], True
  if scene_name == 'Lamp LED White':
    return [
      set_service(ceiling_lights, "off"),
      set_service(lamps, "on"),
      set_service(leds, "on"),
    ], True
  if scene_name == 'LED White':
    return [set_service(leds, "on")], True
  if scene_name == 'Hue':
    return [
      {
        "service": "pyscript.turn_rgb_light",
        "data": {
          "light_list": lamps + ceiling_lights + leds,
          "state": 'off',
          "rgb": 'non_rgb_only',
        },
      },
      {
        "service": "pyscript.turn_rgb_light",
        "data": {"light_list": lamps + ceiling_lights + leds},
      },
      set_service(tvs, tv_brightness=2),
    ], False
  if scene_name == 'Night Mode':
    return [
      {
        "service": "homeassistant.turn_on",
        "entity_id": "scene." + room_entity + "_night_mode",
      },
      set_service(tvs, tv_brightness=2),
    ], True
  if scene_name == 'Dark Night Mode':
    return [
      {
        "service": "homeassistant.turn_on",
        "entity_id": "scene." + room_entity + "_dark_night_mode",
      },
      set_service(tvs, tv_brightness=1),
    ], True
  if scene_name == "Sleep Mode":
    return [
      {
        "service": "homeassistant.turn_on",
        "entity_id": "scene." + room_entity + "_sleep_mode",
      }
    ], True
  if scene_name == 'All Off':
    return [
      set_service(ceiling_lights, "off"),
      set_service(lamps, "off"),
      set_service(leds, "off"),
      set_service(tvs, tv_brightness=3),
    ], True
  return None


LIGHT_STATE_SCENES = [
  'light states when intense light summer',
  'light states when moderate light outdoor',
  'light states when low light outdoor',
  'light states when sleep mode',
]

CURTAIN_STATE_SCENES = [
  'curtain states when low light outdoor',
  'curtain states when moderate light outdoor',
  'curtain states when intense light summer',
  'curtain states when sleep mode',
]


def dynamic_room_scene_actions(
    scene_name,
    ceiling_light_control_when,
    lamp_control_when,
    led_control_when,
    curtain_control_when,
    ceiling_lights,
    lamps,
    leds,
    curtains,
    set_service,
    continue_if,
):
  if scene_name in LIGHT_STATE_SCENES:
    light_scene_state = scene_name.replace('light states when ', '')
    return [
      {
        "parallel": [
          {
            "if": continue_if(ceiling_light_control_when[light_scene_state], "on"),
            "then": set_service(ceiling_lights, "on"),
            "else": set_service(ceiling_lights, "off"),
          },
          {
            "if": continue_if(lamp_control_when[light_scene_state], "on"),
            "then": set_service(lamps, "on"),
            "else": set_service(lamps, "off"),
          },
          {
            "if": continue_if(led_control_when[light_scene_state], "on"),
            "then": set_service(leds, "on"),
            "else": set_service(leds, "off"),
          },
        ]
      }
    ], True
  if scene_name in CURTAIN_STATE_SCENES:
    curtain_scene_state = scene_name.replace('curtain states when ', '')
    return [
      {
        "parallel": [
          {
            "if": continue_if(curtain_control_when[curtain_scene_state], "on"),
            "then": set_service(curtains, "on"),
            "else": set_service(curtains, "off"),
          }
        ]
      }
    ], True
  return None


def set_new_scene_state_action(room_scene_ctl, new_scene):
  return {
    "service": "script.call_room_scene",
    "data": {
      "room_scene_select": room_scene_ctl,
      "scene": new_scene,
    },
  }


def old_scene_set_new_scene_state_choice(room_scene_ctl, old_scene, new_scene):
  return {
    "conditions": {
      "condition": "state",
      "entity_id": room_scene_ctl,
      "state": old_scene,
    },
    "sequence": set_new_scene_state_action(room_scene_ctl, new_scene),
  }


def call_scene_service_if_selected_choice(room_scene_ctl, scene_name, scene_service):
  return {
    "conditions": [
      {
        "condition": "state",
        "entity_id": room_scene_ctl,
        "state": scene_name,
      }
    ],
    "sequence": scene_service,
  }
