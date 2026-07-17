def build_room_battery_entities(room_entity, template_list, get_postfix, get_name_from_entity):
  room_battery_entity_list = battery_entities_from_templates(template_list)
  room_battery_entity = "group." + room_entity + "_battery"
  room_min_battery_value_entity = "sensor." + room_entity + "_min_battery"
  room_low_battery_entity = "binary_sensor." + room_entity + "_low_battery"

  return {
    "room_battery_entity_list": room_battery_entity_list,
    "room_battery_entity": room_battery_entity,
    "group_dict_additions": {
      get_postfix(room_battery_entity): {
        "name": get_name_from_entity(room_battery_entity),
        "entities": room_battery_entity_list,
        "configured": True,
      }
    },
    "room_min_battery_value_entity": room_min_battery_value_entity,
    "sensor_list_additions": [
      {
        "name": get_name_from_entity(room_min_battery_value_entity),
        "platform": "min_max",
        "type": "min",
        "entity_ids": room_battery_entity_list,
        "configured": True,
      }
    ],
    "room_low_battery_entity": room_low_battery_entity,
    "template_list_additions": [
      {
        "binary_sensor": [
          {
            "name": get_name_from_entity(room_low_battery_entity),
            "state": '{% set state = states("' + room_min_battery_value_entity + '") %} {% if state == "unavailable" or state == "unknown" or int(state) > 20 %} off {% else%} on {% endif %}'
          }
        ],
        "configured": True
      }
    ],
  }


def battery_entities_from_templates(template_list):
  room_battery_entity_list = []
  for entity_dict in template_list:
    configured = False
    for key, value in entity_dict.items():
      if key == "configured":
        configured = value

    for key, value in entity_dict.items():
      entity_type = key
      entity_data_list = value
      if key != "trigger":
        if isinstance(entity_data_list, list) and configured:
          for entity_data in entity_data_list:
            entity_name = entity_data["name"].strip().replace(" ", "_").replace("-", "_").lower()
            if "_battery" in entity_name and not "_battery_" in entity_name:
              formatted_entity_id = f"{entity_type}.{entity_name}"
              room_battery_entity_list += [formatted_entity_id]

  return room_battery_entity_list
