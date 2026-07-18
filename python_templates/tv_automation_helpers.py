def reset_picture_mode_automation(automation_room_name, room_name, tvs, set_service):
  return {
    "alias": "ZTV-" + automation_room_name + "Reset Picture Mode When Turning on TV" + "-" + room_name,
    "configured": len(tvs) > 0,
    "trigger": [
      {
        "platform": "state",
        "entity_id": tvs,
        "from": "off",
        "to": "on"
      }
    ],
    "action": [
      set_service(tvs, tv_brightness=3)
    ]
  }


def picture_mode_for_brightness(tv_brightness):
  return "Movie"    if tv_brightness in [1, '1'] else \
         "Natural"  if tv_brightness in [2, '2'] else \
         "Standard" if tv_brightness in [3, '3'] else \
         "Dynamic"


def set_picture_mode_action(entity_list, tv_picture_mode, tv_brightness):
  return {
    "if": [
      {
        'alias': 'Set TV brightness when it is on',
        "condition": "state",
        "entity_id": entity_list,
        "state": "on"
      }
    ],
    "then":  { "service" : "input_select.select_option",
                "data": { "entity_id" : tv_picture_mode,
                          "option": picture_mode_for_brightness(tv_brightness)}}
  }


def picture_mode_step_action(tv_brightness, tv_picture_mode, tvs, continue_if, set_service):
  transitions = {
    'cycle': [
      ("Movie", 4),
      ("Natural", 1),
      ("Standard", 2),
      ("Dynamic", 3),
    ],
    'increment': [
      ("Movie", 2),
      ("Natural", 3),
      ("Standard", 4),
      ("Dynamic", 4),
    ],
    'decrement': [
      ("Movie", 1),
      ("Natural", 1),
      ("Standard", 2),
      ("Dynamic", 3),
    ],
  }

  return {"choose": [
    {
      "conditions": continue_if(tv_picture_mode, picture_mode),
      "sequence": set_service(tvs, tv_brightness=next_brightness),
    }
    for picture_mode, next_brightness in transitions[tv_brightness]
  ]}
