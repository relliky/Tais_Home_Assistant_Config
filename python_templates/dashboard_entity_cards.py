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


def light_card(entity, card_name, card_icon, card_type='custom:mushroom-light-card'):
  import dashboard_card_mod

  return {
    "type": card_type,
    "fill_container": True,
    "use_light_color": False,
    "show_brightness_control": True,
    "show_color_control": False,
    "show_color_temp_control": True,
    "collapsible_controls": False,
    "name": card_name,
    "icon": card_icon,
    "entity": entity
  } | dashboard_card_mod.build_card_mod('ios16_toggle', card_type=card_type, color='ios_yellow')


def cover_card(entity, card_name, card_icon, card_type='custom:mushroom-cover-card'):
  return {
    "type": card_type,
    "fill_container": True,
    "tap_action": {
      "action": "toggle"
    },
    "icon_tap_action": {
      "action": "toggle"
    },
    "double_tap_action": {
      "action": "more-info"
    },
    "hold_action": {
      "action": "more-info"
    },
    "show_position_control": True,
    "show_buttons_control": True,
    "name": card_name,
    "icon": card_icon,
    "entity": entity
  }


def climate_card(entity, card_name, card_icon, card_type='custom:mushroom-climate-card'):
  return {
    "type": card_type,
    "show_temperature_control": True,
    "collapsible_controls": False,
    "name": card_name,
    "icon": card_icon,
    "entity": entity
  }


def media_player_card(entity, card_name, card_icon, card_type='custom:mushroom-media-player-card'):
  return {
    "type": card_type,
    "fill_container": True,
    "tap_action": {
      "action": "more-info"
    },
    "icon_tap_action": {
      "action": "more-info"
    },
    "volume_controls": [
      "volume_set",
      "volume_buttons"
    ],
    "show_volume_level": False,
    "name": card_name,
    "icon": card_icon,
    "entity": entity
  }


def group_card(entity, card_name, card_type='custom:auto-entities'):
  return {
    "type": card_type,
    "card": {
      "type": "entities",
      "title": card_name
    },
    "filter": {"include": [{"group": entity}]}
  }


def simple_sensor_card(entity, card_name, card_icon, card_type='sensor'):
  return {
    "type": card_type,
    "graph": "line",
    "name": card_name,
    "icon": card_icon,
    "entity": entity
  }


def entity_card(entity, card_name, card_icon, card_type='custom:mushroom-entity-card'):
  return {
    "type": card_type,
    "fill_container": True,
    "tap_action": {"action": "toggle"},
    "icon_tap_action": {"action": "toggle"},
    "name": card_name,
    "icon": card_icon,
    "entity": entity
  }


def entities_card(entity, card_name, card_type='entities'):
  return {
    "type": card_type,
    "entities": [
      {
        "name": card_name,
        "entity": entity
      }
    ]
  }


def scheduler_card(entity, card_type='custom:scheduler-card'):
  return {
    "type": card_type,
    "include": entity,
    "exclude": [],
    "title": True,
    "discover_existing": True,
    "time_step": 30
  }


def flipdown_timer_card(entity, card_name, card_icon, card_type='custom:flipdown-timer-card'):
  return {
    "type": card_type,
    "show_hour": True,
    "show_title": True,
    "theme": 'dark',
    "styles": {
      "rotor": {
        "width": "50px",
        "height": "80px"
      },
      "button": {
        "width": "100px",
        "location": "bottom"
      }
    },
    "name": card_name,
    "icon": card_icon,
    "entity": entity
  }


def number_card(entity, card_name, card_icon, card_type='custom:mushroom-number-card'):
  return {
    "type": card_type,
    "fill_container": True,
    "tap_action": {"action": "more-info"},
    "icon_tap_action": {"action": "more-info"},
    "display_mode": "buttons",
    "name": card_name,
    "icon": 'mdi:counter' if card_icon is None else card_icon,
    "entity": entity
  }
