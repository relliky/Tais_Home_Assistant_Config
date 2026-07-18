def build_view(view_path='', cards=None, theme="Mushroom Shadow", title=''):
  return {
    "theme": theme,
    "title": title,
    "path":  view_path,
    "subview": True,
    "badges": [],
    "cards": [] if cards is None else cards
  }


def layout_wrapper_cards(dashboard_type, cards=None):
  if dashboard_type in ['mobile', 'default']:
    return [{
        "square": False,
        "columns": 2,
        "type": "grid",
        "cards": cards}]
  elif dashboard_type == 'tablet':
    return cards

  raise TypeError( "\n" +\
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
    "getLayoutWrapperCardList does not support dashboard_type" + str(dashboard_type) + \
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")


def room_view_cards(dashboard_type, header_cards, main_cards, tail_cards):
  return (
    layout_wrapper_cards(dashboard_type, header_cards) +
    layout_wrapper_cards(dashboard_type, main_cards) +
    tail_cards
  )


def home_navigation_card(dashboard_root, navigate_path=None):
  navigation_path = (dashboard_root + "/" + "home") if navigate_path is None else navigate_path
  return {
    "type": "custom:mushroom-template-card",
    "entity": "input_boolean.placeholder",
    "icon": "mdi:keyboard-return",
    "icon_color": "yellow",
    "primary": "HOME",
    "secondary": "",
    "layout": "vertical",
    "hold_action": {
      "action": "toggle"
    },
    "tap_action": {
      "action": "navigate",
      "navigation_path": navigation_path
    },
    "icon_tap_action": {
      "action": "navigate",
      "navigation_path": navigation_path
    },
    "card_mod": {
      "style": {
        "mushroom-state-info$": ".primary {\n  font-size: 16px !important;\n  position: relative;\n  top: 0px;\n  left: 0px;\n  overflow: visible !important;\n  white-space:  \n}\n",
        "mushroom-shape-icon$": ".shape {\n  position: relative;\n  left: 0px;\n  top: 0px;\n}\n",
        ".": ":host {\n  --mush-icon-size: 80px;\n}\n"
      }
    }
  }


def header_cards(dashboard_root, scene_card, navigate_path=None):
  return [
    home_navigation_card(dashboard_root, navigate_path=navigate_path),
    scene_card,
  ]


def button_navigation_room_card(room_name, room_icon, dashboard_view_path):
  return {
    "type": "custom:button-card",
    "aspect_ratio": "1/1",
    "tap_action": {
      "action": "navigate",
      "navigation_path": dashboard_view_path,
    },
    "icon_tap_action": {
      "action": "navigate",
      "navigation_path": dashboard_view_path,
    },
    "entity": "input_boolean.placeholder",
    "show_state": False,
    "name": room_name,
    "icon": room_icon,
    "show_icon": True,
    "show_name": True,
  }


def navigation_room_secondary_text(temperature_sensor, motion_group, motion_postfix):
  temperature_sensor_template_reference = "states." + temperature_sensor + ".state"
  return (
    "{% if " + temperature_sensor_template_reference + " is defined %} {{ " +
    temperature_sensor_template_reference + " }}\u00b0C {% endif %}" +
    "{% set motion_postfix     = '" + motion_postfix + "' %}\n" +
    "{% set motion = '" + motion_group + "' %}\n"
    "{% if is_state(motion, 'on') %}\n"
    "  \U0001f64b\U0001f3fb\n"
    "{% else %}\n"
    "  \U0001f9b6\U0001f3fb\n"
    "{% endif %}{{\n"
    " (as_timestamp(now()) -\n"
    " as_timestamp(states.group[motion_postfix].last_changed)) |\n"
    " timestamp_custom(\"%H:%M\", false) }} "
  )


def unavailable_status_card(unavailable_entity, template_card):
  return template_card(
    icon="mdi:battery-charging-outline",
    icon_color="red",
    condition_state='on',
    condition_entity=unavailable_entity,
  )


def battery_status_card(room_low_battery_entity, room_battery_entity, template_card):
  return template_card(
    icon="{% if is_state('" + room_low_battery_entity + "', 'on') %}\n"
         "  mdi:battery-20-bluetooth \n"
         "{% else %}\n"
         "  mdi:battery-70\n"
         "{% endif %}",
    icon_color="{% if is_state('" + room_low_battery_entity + "', 'on') %}\n"
               "  amber\n"
               "{% endif %}",
    tap_entity=room_battery_entity,
  )
