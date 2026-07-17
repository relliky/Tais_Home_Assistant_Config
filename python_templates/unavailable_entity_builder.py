import re


def collect_added_device_entities(
    template_list,
    binary_sensor_list,
    switch_list,
    cover_list,
    lock_list,
    event_list,
    light_list,
):
  added_device_entities = []

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
            formatted_entity_id = f"{entity_type}.{entity_name}"
            added_device_entities.append(formatted_entity_id)

  typed_entity_lists = [
    ("binary_sensor", binary_sensor_list),
    ("switch", switch_list),
    ("cover", cover_list),
    ("lock", lock_list),
    ("event", event_list),
    ("light", light_list),
  ]

  for entity_type, entity_list in typed_entity_lists:
    for entity_dict in entity_list:
      entity_name = entity_dict.get("name")
      configured = entity_dict.get("configured")
      if entity_name and configured:
        formatted_name = entity_name.strip().replace(" ", "_").replace("-", "_").lower()
        formatted_name = re.sub("_$", "", formatted_name)
        added_device_entities.append(f"{entity_type}.{formatted_name}")

  return added_device_entities
