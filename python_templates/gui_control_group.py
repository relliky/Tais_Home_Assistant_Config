SCENE_CONTROL_NAMES = [
  'intense light summer',
  'moderate light outdoor',
  'low light outdoor',
  'sleep mode',
]


def scene_control_entities(
  ceiling_lights,
  lamps,
  leds,
  curtains,
  ceiling_light_control_when,
  lamp_control_when,
  led_control_when,
  curtain_control_when,
):
  entities = []

  for control_name in SCENE_CONTROL_NAMES:
    entities += [ceiling_light_control_when[control_name]] if len(ceiling_lights) > 0 else []
    entities += [lamp_control_when[control_name]] if len(lamps) > 0 else []
    entities += [led_control_when[control_name]] if len(leds) > 0 else []
    entities += [curtain_control_when[control_name]] if len(curtains) > 0 else []

  return entities


def automation_entities(automations):
  return [automation['id'] for automation in automations]


def adaptive_lighting_sleep_mode_entities(cfg_adaptive_lighting, al_light_list, get_entity_from_name):
  if cfg_adaptive_lighting != True:
    return []

  return [
    "switch.adaptive_lighting_sleep_mode_" + get_entity_from_name(al_dict['name'])
    for al_dict in al_light_list
  ]


def extra_control_entities(
  wall_switches,
  decouple_wall_switches,
  cfg_adaptive_lighting,
  al_light_list,
  get_entity_from_name,
  time_controls,
  light_sensor_controls,
  room_battery_entity,
  manual_added_automations,
  windows,
  window_group,
):
  return (
    wall_switches +
    decouple_wall_switches +
    adaptive_lighting_sleep_mode_entities(cfg_adaptive_lighting, al_light_list, get_entity_from_name) +
    time_controls +
    light_sensor_controls +
    [room_battery_entity] +
    manual_added_automations +
    ([window_group] if len(windows) > 0 else [])
  )


def auto_group_declaration(gui_ctl_group, gui_ctl_entity_list, get_postfix, get_name_from_entity):
  return {
    get_postfix(gui_ctl_group): {
      "name": get_name_from_entity(gui_ctl_group),
      "entities": gui_ctl_entity_list,
    }
  }


def merge_auto_group_declaration(
  entity_declarations,
  cfg_group_auto,
  get_gui_ctl_group,
  get_gui_ctl_entity_list,
  get_postfix,
  get_name_from_entity,
):
  if cfg_group_auto:
    gui_ctl_group = get_gui_ctl_group()
    entity_declarations['group'] |= auto_group_declaration(
      gui_ctl_group,
      get_gui_ctl_entity_list(),
      get_postfix,
      get_name_from_entity,
    )
