def is_light_entity_list(entity_list):
  is_light_list = True
  if type(entity_list) is list:
    for entity in entity_list:
      is_light_list = is_light_list if entity.startswith('light.') else False
  else:
    is_light_list = is_light_list if entity_list.startswith('light.') else False
  return is_light_list


def service_action_alias(entity_list, state=None, light_brightness=None):
  return ('Turn'  + \
          (' nothing'        if entity_list==[]              else \
          ' ' + entity_list  if isinstance(entity_list, str) else " " + " ".join(entity_list)) + \
          (''                if state==None                  else ' state=' + state) + \
          (''                if light_brightness==None       else ' light_brightness=' + str(light_brightness)))


def homeassistant_on_off_action(entity_list, state):
  return {"service":"homeassistant.turn_on"  if state == 'on'     else \
                    "homeassistant.turn_off" if state == 'off'    else None,
          "entity_id": entity_list}


def toggle_entities_action(entity_list, set_service):
  return {
    "if": [
      {
        'alias': 'toggle everything all together: if any entity is on, turn off all entities, otherwise turn on all entities',
        "condition": "state",
        "entity_id": entity_list,
        "state": "on",
        "match": 'any'
      }
    ],
    "then": set_service(entity_list, 'off'),
    "else": set_service(entity_list, 'on')
  }
