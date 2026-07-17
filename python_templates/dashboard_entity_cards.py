def get_entity_domain(entity):
  return entity.split(".", 1)[0]


def infer_entity_card_type(entity):
  entity_type = get_entity_domain(entity)

  if entity_type in ['light', 'cover', 'climate']:
    return 'custom:mushroom-' + entity_type + '-card'
  elif entity_type in ['media_player']:
    return 'custom:mushroom-media-player-card'
  if entity_type in ['binary_sensor', 'switch', 'input_boolean']:
    return 'custom:mushroom-entity-card'
  elif entity_type in ['group']:
    return 'custom:auto-entities'
  elif entity_type in ['sensor']:
    return 'sensor'
  elif entity_type in ['input_select']:
    return 'custom:mushroom-select-card'
  elif entity_type in ['input_number', 'number']:
    return 'custom:mushroom-number-card'

  return None
