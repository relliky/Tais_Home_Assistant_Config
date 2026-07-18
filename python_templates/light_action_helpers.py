def wall_switch_turn_on_reset_sequence(entity_list):
  return [{"service":"homeassistant.turn_off", "entity_id": entity_list},
          {"delay": {"milliseconds": 200}},
          {"service":"homeassistant.turn_on",  "entity_id": entity_list}]


def wall_switch_turn_on_reset_alias():
  return 'Everytime to turn on a wall switch, make sure to turn off it first to make sure the smart lights will be back on'
