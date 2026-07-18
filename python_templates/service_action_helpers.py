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
