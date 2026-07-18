def wall_switch_turn_on_reset_sequence(entity_list):
  return [{"service":"homeassistant.turn_off", "entity_id": entity_list},
          {"delay": {"milliseconds": 200}},
          {"service":"homeassistant.turn_on",  "entity_id": entity_list}]


def wall_switch_turn_on_reset_alias():
  return 'Everytime to turn on a wall switch, make sure to turn off it first to make sure the smart lights will be back on'


def turn_on_with_brightness_action(entity_list, light_brightness):
  return {"service" : "light.turn_on",
          "entity_id" : entity_list,
          "data": {"brightness_pct": light_brightness}}


def light_on_off_action(entity_list, state):
  return {"service":"light.turn_on"  if state == 'on'     else \
                    "light.turn_off" if state == 'off'    else None,
          "entity_id": entity_list}


def brightness_step_action(entity_list, step_value, set_service):
  return {
    "if": [
      {
        'alias': 'increment brightness unless it is off, set the brightness to 1 percent',
        "condition": "state",
        "entity_id": entity_list,
        "state": "off",
      }
    ],
    "then":[set_service(entity_list, 'on')] if 'led' in entity_list[0] else [] + \
           [set_service(entity_list, 'on', light_brightness=1),],
    "else": {"service":"light.turn_on",
            "target":{"entity_id":entity_list},
            "data":{"brightness_step_pct":step_value}},
  }
