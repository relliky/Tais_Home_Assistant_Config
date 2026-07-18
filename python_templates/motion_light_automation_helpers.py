def curtain_scene_choose(condition_list_is, call_scene_service, do_nothing_service):
  return {
    "alias": 'If it is intense light summer',
    "if": condition_list_is('intense light summer'),
    "then": call_scene_service('curtain states when intense light summer'),
    "else": {
      "alias": 'If it is moderate light outdoor',
      "if": condition_list_is('moderate light outdoor'),
      "then": call_scene_service('curtain states when moderate light outdoor'),
      "else": {
        "alias": 'If it is low light outdoor',
        "if": condition_list_is('low light outdoor'),
        "then": call_scene_service('curtain states when low light outdoor'),
        "else": {
          "alias": 'If it is sleep mode',
          "if": condition_list_is('sleep mode'),
          "then": call_scene_service('curtain states when sleep mode'),
          "else": {
            "alias": 'Default',
            **do_nothing_service()
          }
        }
      }
    }
  }


def light_scene_choose(condition_list_is, call_scene_service, do_nothing_service):
  return {
    "alias": 'If it is bright morning',
    "if": condition_list_is('intense light summer'),
    "then": call_scene_service('light states when intense light summer'),
    "else": {
      "alias": 'If it is bright afternoon',
      "if": condition_list_is('moderate light outdoor'),
      "then": call_scene_service('light states when moderate light outdoor'),
      "else": {
        "alias": 'If it is bright afternoon',
        "if": condition_list_is('low light outdoor'),
        "then": call_scene_service('light states when low light outdoor'),
        "else": {
          "alias": 'If it is bright afternoon',
          "if": condition_list_is('sleep mode'),
          "then": call_scene_service('light states when sleep mode'),
          "else": {
            "alias": 'Default',
            **do_nothing_service()
          }
        }
      }
    }
  }


def lights_off_conditions(room_occupancy, motion_group, room_type):
  return [
    {
      "condition": "state",
      "entity_id": room_occupancy,
      "state": "Outside"
    }
  ] + (
    [
      {
        "condition": "state",
        "entity_id": motion_group,
        "state": "off",
        "for": "00:01:00"
      }
    ] if room_type == 'bedroom' else []
  )


def lights_off_parallel_actions(
  automation_lights_on_id,
  tvs,
  extractor,
  set_service,
  set_new_scene_state,
  call_scene_service,
):
  return [
    set_service(automation_lights_on_id, 'on'),
    set_service(tvs, 'off'),
    set_new_scene_state("Idle"),
    call_scene_service("All Off"),
    set_service(extractor, 'off')
  ]


def disable_entering_lights_on_actions(automation_lights_on_id, automation_turn_off):
  return [
    {"delay": "00:00:10"},
    automation_turn_off(automation_lights_on_id, stop_actions="false")
  ]


def walking_in_dark_led_actions(
  room_entity,
  leds,
  ceiling_lights,
  lamps,
  non_bed_motion_sensors,
  set_service,
  call_scene_service,
):
  guarded_lights = leds + ceiling_lights + lamps if room_entity != 'guest_room' else leds + ceiling_lights
  return [
    {
      "condition": "not",
      "conditions": [{
        "condition": "state",
        "entity_id": guarded_lights,
        "state": "on",
        "match": "any"}]
    },
    call_scene_service("Dark Night Mode") if room_entity == 'master_room' else set_service(leds, 'on', light_brightness=40),
    {
      "alias": "Wait for floor sensors to go off for 1 min to turn off LED. Stop waiting if it has wait for 1 hour.",
      "wait_for_trigger":
        { "platform": "state",
          "entity_id": non_bed_motion_sensors,
          "to":  "off",
          "for": "00:01:00"
        },
      "timeout": "01:00:00"
    },
    {
      "alias": " Testing if other lights are manually turned on after the LED was on",
      "condition": "not",
      "conditions": [{
        "condition": "state",
        "entity_id": ceiling_lights + lamps,
        "state": "on",
        "match": "any"}]
    },
    set_service(leds, 'off')
  ]
