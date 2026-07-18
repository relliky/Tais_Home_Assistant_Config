def hvac_mode_for_state(state):
  return "off" if state == 'off' else "heat"


def set_hvac_mode_action(entity_list, state):
  return { "service": "climate.set_hvac_mode",
           "data": {"hvac_mode": hvac_mode_for_state(state)},
           "entity_id": entity_list
        }


def set_temperature_step_action(thermostat, step_value):
  return {"service": "climate.set_temperature",
          "target":{"entity_id": thermostat},
          "data":  {"temperature": "{{ (state_attr('" + thermostat + "', 'temperature')) + " + str(step_value) + "}}"}}
