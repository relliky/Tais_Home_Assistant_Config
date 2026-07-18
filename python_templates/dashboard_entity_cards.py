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


def complex_sensor_card(entity, card_name):
  import dashboard_card_mod

  return {
    "type": "custom:vertical-stack-in-card",
    "cards": [
      {
        "type": "custom:mushroom-template-card",
        "entity": entity,
        "primary": card_name,
        "secondary": "{{ states('" + entity + "') | round(0) }}\u00b0C\n",
        "icon": "mdi:thermometer",
        "icon_color": "{% set value = states('" + entity + "') | int %}\n{% if value < 18 %}\n  blue\n{% elif value < 28 %}\n  light-green\n{% elif value < 40 %}\n  red\n{% else %}\n  green\n{% endif %}",
        "tap_action": {"action": "more-info"},
        "icon_tap_action": {"action": "more-info"},
      } | dashboard_card_mod.build_card_mod('background_color_select', color='transparent'),
      {
        "type": "custom:layout-card",
        "layout_type": "masonry",
        "layout": {
          "width": 150,
          "max_cols": 1,
          "height": "auto",
          "padding": "0px",
          "card_margin": "var(--masonry-view-card-margin, -10px 8px 15px)"
        },
        "cards": [
          {
            "type": "custom:mini-graph-card",
            "tap_action": {"action": "more-info"},
            "icon_tap_action": {"action": "more-info"},
            "entities": [
              {
                "entity": entity,
                "name": "Temperature"
              }
            ],
            "color_thresholds": [
              {
                "value": -10,
                "color": "#0000ff"
              },
              {
                "value": 18,
                "color": "#0000ff"
              },
              {
                "value": 18.1,
                "color": "#00FF00"
              },
              {
                "value": 27,
                "color": "#00FF00"
              },
              {
                "value": 27.1,
                "color": "#FF0000"
              },
              {
                "value": 40,
                "color": "#FF0000"
              }
            ],
            "hours_to_show": 24,
            "line_width": 3,
            "animate": True,
            "show": {
              "name": False,
              "icon": False,
              "state": False,
              "legend": False,
              "fill": "fade"
            },
            "card_mod": {
              "style": "ha-card {\n  background: none;\n  box-shadow: none;\n  --ha-card-border-width: 0;\n}"
            }
          }
        ]
      }
    ]
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


def header_chips_card():
  return {
    "type": "custom:mod-card",
    "card": {
      "type": "custom:button-card",
      "show_icon": False,
      "show_state": False,
      "show_name": False,
      "styles": {
        "grid": [
          {"grid-template-areas": '"a a b c"'},
          {"grid-template-columns": "1fr 3fr 1fr 1fr"},
          {"grid-template-rows": "1fr"}
        ],
        "card": [{"padding": "8px"}]
      },
      "custom_fields": {
        "a": {
          "card": {
            "type": "custom:mushroom-chips-card",
            "chips": [
              {"type": "menu"}
            ]
          }
        },
        "b": {
          "card": {
            "type": "custom:mushroom-chips-card",
            "chips": [
              {
                "type": "template",
                "entity": "sensor.time",
                "content": "{{ states(entity) }}",
                "tap_action": {"action": "more-info"},
                "icon_tap_action": {"action": "more-info"},
              }
            ]
          }
        },
        "c": {
          "card": {
            "type": "custom:mushroom-chips-card",
            "chips": [
              {
                "type": "template",
                "entity": "sensor.shi_chen",
                "content": "{{ states(entity) }}",
                "tap_action": {"action": "more-info"},
                "icon_tap_action": {"action": "more-info"},
              }
            ]
          }
        }
      }
    },
    "card_mod": {
      "style": """
                :host {
                    z-index: 5;
                    position: sticky;
                    position: -webkit-sticky;
                    top: 0;
                }
            """
    }
  }


def template_card_tap_action(tap_action, dashboard_view_path):
  if tap_action == 'navigate':
    return {
      "action": "navigate",
      "navigation_path": dashboard_view_path
    }
  elif tap_action == 'more-info':
    return {"action": "more-info"}

  return {}


def template_card(
  icon='mdi:head-alert-outline',
  icon_color='blue',
  primary=None,
  secondary=None,
  entity='input_boolean.placeholder',
  tap_action_dict=None,
  theme='default',
):
  tap_action_dict = {} if tap_action_dict is None else tap_action_dict

  return {
    "type": "custom:mushroom-template-card",
    "icon": "{% set entity = '" + entity + "' %}\n" + icon,
    "tap_action": tap_action_dict,
    "icon_tap_action": tap_action_dict,
    "entity": entity,
    "layout": "horizontal",
    "fill_container": True,
  } | ({"primary": primary} if primary != None else {}) \
    | ({"secondary": secondary} if secondary != None else {}) \
    | ({"icon_color": "{% set entity = '" + entity + "' %}\n" + icon_color} if theme == 'default' else {})
