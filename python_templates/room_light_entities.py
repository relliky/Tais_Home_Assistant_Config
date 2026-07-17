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
