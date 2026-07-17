def remove_disabled_entities(entity_declarations):
  filtered_entities = {}

  for category_name in entity_declarations:
    category_entities = entity_declarations[category_name]

    if type(category_entities) == list:
      filtered_entities[category_name] = []
      for entity in category_entities:
        if entity["configured"] == True:
          entity.pop('configured')
          filtered_entities[category_name] += [entity]

    elif type(category_entities) == dict:
      filtered_entities[category_name] = {}
      for entity_name in category_entities:
        entity = category_entities[entity_name]
        if entity["configured"] == True:
          entity.pop('configured')
          filtered_entities[category_name] |= {entity_name : entity}

    else:
      raise TypeError('entity_declarations[' + category_name + '] is not either a dictionary or a list')

  return filtered_entities
