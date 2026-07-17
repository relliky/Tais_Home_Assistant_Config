def default_light_entities(room_entity, room_name, num_of_lamps, cfg_adaptive_lighting):
  ceiling_lights = ["light." + room_entity + "_ceiling_light"]
  lamps = []
  for i in range(num_of_lamps):
    lamp = "light." + room_entity + "_lamp"
    if num_of_lamps != 1:
      lamp += "_" + str(i+1)
    lamps += [lamp]

  leds = []

  return {
    "ceiling_lights": ceiling_lights,
    "lamps": lamps,
    "leds": leds,
    "lights": leds + lamps + ceiling_lights,
    "light_group": "group." + room_entity + "_light_group",
    "screen_leds": [],
    "extractor": [],
    "al_sleep_mode": "switch.adaptive_lighting_sleep_mode_" + room_entity,
    "al_adapt_brightness": "switch.adaptive_lighting_adapt_brightness_" + room_entity,
    "al_light_list_additions": adaptive_lighting_configs(room_name) if cfg_adaptive_lighting == True else [],
  }


def adaptive_lighting_configs(room_name):
  return [
    {
      "configured": True,
      "name": room_name,
      "lights": [],
      "prefer_rgb_color": False,
      "transition": 45,
      "initial_transition": 1,
      "interval": 90,
      "min_brightness": 50,
      "max_brightness": 100,
      "min_color_temp": 2700,
      "max_color_temp": 4000,
      "sleep_brightness": 20,
      "sleep_color_temp": 2200,
      "min_sunset_time": "17:30",
      "take_over_control": True,
      "autoreset_control_seconds": 86400,
      "detect_non_ha_changes": False,
      "only_once": False,
      "adapt_only_on_bare_turn_on": True,
      "separate_turn_on_commands": False,
      "send_split_delay": 500,
      "adapt_delay": 0.5,
      "intercept": True,
      "multi_light_intercept": True,
      "include_config_in_attributes": False,
    }
  ]


def default_lighting_control_entities(room_entity, west_face_windows):
  light_intensity_threshold_when = {
    "intense light summer": "input_number.intensity_threshold_intense_light_summer_" + room_entity,
    "moderate light outdoor": "input_number.intensity_threshold_moderate_light_outdoor_" + room_entity,
  }
  light_intensity_entity = "sensor.master_room_light_intensity" if west_face_windows is True else "sensor.living_room_light_intensity"
  noon_time = "input_datetime.noon_time_" + room_entity
  light_sensor = "sensor.master_room_west_side_light_sensor" if west_face_windows is True else "sensor.living_room_east_side_light_sensor"
  min_value_as_bright = "input_number." + room_entity + "_min_value_as_bright"

  return {
    "ceiling_light_control_when": control_when_entities("ceiling_light", room_entity),
    "lamp_control_when": control_when_entities("lamp", room_entity),
    "led_control_when": control_when_entities("led", room_entity),
    "curtain_control_when": control_when_entities("curtain", room_entity),
    "light_intensity_threshold_when": light_intensity_threshold_when,
    "light_intensity_entity": light_intensity_entity,
    "noon_time": noon_time,
    "time_controls": [],
    "light_sensor": light_sensor,
    "min_value_as_bright": min_value_as_bright,
    "light_sensor_controls": [light_sensor],
    "gui_ctl_entity_list_additions": list(light_intensity_threshold_when.values()) + [light_intensity_entity],
  }


def control_when_entities(control_prefix, room_entity):
  return {
    "intense light summer": "input_boolean." + control_prefix + "_control_intense_light_summer_" + room_entity,
    "moderate light outdoor": "input_boolean." + control_prefix + "_control_moderate_light_outdoor_" + room_entity,
    "low light outdoor": "input_boolean." + control_prefix + "_control_low_light_outdoor_" + room_entity,
    "sleep mode": "input_boolean." + control_prefix + "_control_sleep_mode_" + room_entity,
  }
