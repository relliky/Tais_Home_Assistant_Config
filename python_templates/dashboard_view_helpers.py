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


def navigation_room_title_card(
    room_icon,
    room_name,
    temperature_sensor,
    motion_group,
    motion_postfix,
    template_card,
):
  return template_card(
    icon=room_icon,
    icon_color="blue",
    primary=room_name,
    secondary=navigation_room_secondary_text(
      temperature_sensor,
      motion_group,
      motion_postfix,
    ),
    tap_action='navigate',
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


def window_status_card(window_group, template_card):
  return template_card(
    icon="{% if is_state(entity, 'on') %}\n"
         "  mdi:window-open-variant\n"
         "{% else %}\n"
         "  mdi:window-closed-variant\n"
         "{% endif %}",
    icon_color="{% if is_state(entity, 'on') %}\n"
               "  lime\n"
               "{% endif %}",
    condition_entity=window_group,
  )


def tv_status_card(tv_entity, template_card):
  return template_card(
    icon="mdi:television-classic",
    icon_color="{% if is_state(entity, 'on') %}\n"
               "  deep-orange\n"
               "{% endif %}",
    tap_entity=tv_entity,
    condition_entity=tv_entity,
    condition_state='on',
  )


def light_status_card(light_group, template_card):
  return template_card(
    icon="{% if is_state(entity, 'on') %}\n"
         "  mdi:floor-lamp\n"
         "{% else %}\n"
         "  mdi:floor-lamp-outline\n"
         "{% endif %}",
    icon_color="{% if is_state(entity, 'on') %}\n"
               "  amber\n"
               "{% endif %}",
    tap_entity=light_group,
  )


def occupancy_override_status_card(occupancy_override_entity, template_card):
  return template_card(
    icon="{% if is_state(entity, 'on') %}\n"
         "  mdi:timer-sand\n"
         "{% else %}\n"
         "  mdi:timer-sand-paused\n"
         "{% endif %}",
    icon_color="{% if is_state(entity, 'on') %}\n"
               "  yellow\n"
               "{% endif %}",
    tap_entity=occupancy_override_entity,
  )


def temperature_control_status_card(thermostat, template_card):
  return template_card(
    icon="{% if is_state(entity, 'heat') %}\n"
         "  mdi:heating-coil\n"
         "    {% else %}   \n"
         "  mdi:snowflake\n"
         "      {% endif %}",
    icon_color="{% if is_state(entity, 'heat') %}\n"
               "  {% if state_attr(entity, 'temperature') > state_attr(entity, 'current_temperature') %}\n"
               "  red\n"
               " {% else %}\n"
               " blue\n"
               "  {% endif %}\n"
               " {% endif %}\n",
    condition_state='heat',
    condition_entity=thermostat,
  )


def occupancy_status_card(room_occupancy, template_card):
  return template_card(
    icon="{% if   is_state(entity, 'Outside') %}\n"
         "  mdi:door-closed\n"
         "{% elif is_state(entity, 'Just Entered') %}\n"
         "  mdi:arrow-right-circle\n"
         "{% elif is_state(entity, 'In Sleep') %}\n"
         "  mdi:sleep\n"
         "{% else %}\n"
         "  mdi:account-multiple\n"
         "{% endif %}",
    icon_color="{% if   is_state(entity, 'Outside') %}                     "
               "{% elif is_state(entity, 'Just Entered') %}\n"
               "  green\n"
               "                 {% elif is_state(entity, 'In Sleep') %}\n"
               "  blue\n"
               "     {% else %}\n"
               "  purple\n"
               "              {% endif %}",
    tap_entity=room_occupancy,
    condition_state_not='Outside',
    condition_entity=room_occupancy,
  )


def curtain_status_card(curtain_group, template_card):
  return template_card(
    icon="{% if is_state(entity, 'open') %}\n"
         "  mdi:curtains\n"
         "{% else %}\n"
         "  mdi:curtains-closed\n"
         "{% endif %}",
    icon_color="{% if is_state(entity, 'open') %}\n"
               "  green       \n"
               "{% endif %}",
    condition_state='open',
    condition_entity=curtain_group,
  )


def navigation_status_cards(
    unavailable_entity,
    room_battery_entity_list,
    room_low_battery_entity,
    room_battery_entity,
    windows,
    window_group,
    tvs,
    lights,
    light_group,
    cfg_occupancy_override,
    occupancy_override_entity,
    cfg_temp_control,
    thermostat,
    cfg_occupancy,
    room_occupancy,
    curtains,
    curtain_group,
    template_card,
):
  cards = [unavailable_status_card(unavailable_entity, template_card)]
  if room_battery_entity_list != []:
    cards += [
      battery_status_card(
        room_low_battery_entity,
        room_battery_entity,
        template_card,
      )
    ]
  if windows != []:
    cards += [window_status_card(window_group, template_card)]
  if tvs != []:
    cards += [tv_status_card(tvs[0], template_card)]
  if lights != []:
    cards += [light_status_card(light_group, template_card)]
  if cfg_occupancy_override != False:
    cards += [
      occupancy_override_status_card(
        occupancy_override_entity,
        template_card,
      )
    ]
  if cfg_temp_control != False:
    cards += [temperature_control_status_card(thermostat, template_card)]
  if cfg_occupancy != False:
    cards += [occupancy_status_card(room_occupancy, template_card)]
  if curtains != []:
    cards += [curtain_status_card(curtain_group, template_card)]
  return cards


def navigation_status_stack_card(card_mod, cards):
  return card_mod | {
    "type": "custom:stack-in-card",
    "mode": "horizontal",
    "cards": cards,
  }


def mushroom_navigation_room_card(title_card, status_stack_card):
  return {
    "type": "custom:stack-in-card",
    "mode": "vertical",
    "cards": [
      title_card,
      status_stack_card,
    ],
  }


def navigation_status_room_card(title_card, card_mod, status_cards):
  return mushroom_navigation_room_card(
    title_card,
    navigation_status_stack_card(card_mod, status_cards),
  )


def prepend_navigation_status_cards(room_card, cards):
  room_card["card"]["cards"][1]["cards"] = (
    cards + room_card["card"]["cards"][1]["cards"]
  )
  return room_card


def append_navigation_title_secondary(room_card, secondary_text):
  room_card["card"]["cards"][0]["secondary"] += secondary_text
  return room_card


def system_navigation_title_card():
  return {
    "type": "custom:mushroom-template-card",
    "icon": "mdi:server",
    "icon_color": "blue",
    "layout": "horizontal",
    "entity": "input_boolean.placeholder",
    "fill_container": True,
    "primary": "System",
    "secondary": "{{states('sensor.processor_use_percent')}}% | {{states('sensor.load_1m')}} | {{(states('sensor.memory_use') | float/1000) | round(1) }}GB ",
    "tap_action": {
      "action": "navigate",
      "navigation_path": "/lovelace-system/system",
    },
    "icon_tap_action": {
      "action": "navigate",
      "navigation_path": "/lovelace-system/system",
    },
  }


def system_gaming_pc_status_card(template_card):
  return template_card(
    icon="mdi:desktop-classic",
    icon_color="{% if   is_state(entity, 'on') %} amber {% endif %}",
    tap_entity='switch.gaming_pc',
    tap_action='more-info',
  )


def system_water_heater_status_card(template_card):
  return template_card(
    icon="mdi:water-boiler",
    icon_color="deep-orange",
    tap_entity='switch.water_heater',
    tap_action='more-info',
  )


def system_navigation_status_cards(template_card):
  return [
    system_gaming_pc_status_card(template_card),
    system_water_heater_status_card(template_card),
  ]
