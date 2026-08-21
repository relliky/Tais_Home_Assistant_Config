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


def light_cycle_entity_id(entity_list):
  return entity_list[0] if type(entity_list) is list else entity_list


def light_cycle_brightness_action(entity_list):
  entity_id = light_cycle_entity_id(entity_list)
  return {"service" : "light.turn_on",
          "entity_id" : entity_list,
          "data_template": {
            "brightness": "{% set brightness = state_attr('" + entity_id + "', 'brightness') | int(0) %}"
                          "{% if brightness == 0 or is_state('" + entity_id + "', 'off') %}3"
                          "{% elif brightness <= 83 %}84"
                          "{% elif brightness <= 167 %}168"
                          "{% elif brightness <= 254 %}255"
                          "{% else %}0{% endif %}"
          }}


def light_cycle_first_step_action(entity_list):
  return {"service" : "light.turn_on",
          "entity_id" : entity_list,
          "data": {"brightness": 3}}


def light_cycle_action(entity_list, continue_if):
  return {
    "if":     continue_if(entity_list, "off"),
    "then": [light_cycle_first_step_action(entity_list)],
    "else":  light_cycle_brightness_action(entity_list),
  }


def led_cycle_action(entity_list, continue_if):
  return {
    "if":     continue_if(entity_list, "off"),
    "then": [
      light_cycle_first_step_action(entity_list),
      {"delay": {"milliseconds": 1000}},
      {"if":   continue_if(entity_list, "off"),
       "then": [light_cycle_first_step_action(entity_list)]},
    ],
    "else":  light_cycle_brightness_action(entity_list),
  }


def light_entities_only(entity_list):
  lights_only_entity_list = []
  for entity in entity_list:
    lights_only_entity_list += [entity] if entity.startswith('light') else []
  return lights_only_entity_list


def reset_lights_to_white_alias():
  return 'Turn on lamps first and check if light color is white. ' + \
         'Reset color lamps to white and apply adaptive lighting.'


def reset_lights_to_white_sequence(lamps, lights_only_entity_list, continue_if):
  return [
     {"service": "homeassistant.turn_on", "entity_id": lamps},
     {"delay" : "00:00:02"},
     {"if": continue_if(lights_only_entity_list, 'color_temp', attribute='color_mode'),
       "then": {"service": "script.do_nothing"},
       "else":[
           {"service": "light.turn_on",  "entity_id": lights_only_entity_list, "data": {"color_temp_kelvin": "3000"}},
           {"delay"  : "00:00:02"},
           {"service": "light.turn_off", "entity_id": lights_only_entity_list},
           {"delay"  : "00:00:02"},
           {"service": "light.turn_on",  "entity_id": lights_only_entity_list}
       ]
     }
  ]
