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
