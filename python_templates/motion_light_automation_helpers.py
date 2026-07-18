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
