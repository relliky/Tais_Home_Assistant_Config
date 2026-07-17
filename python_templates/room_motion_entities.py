def default_motion_sensor_entities(room_entity, room_type, room_name, automation_room_name, get_id_from_alias):
  automation_occupancy = {
    "alias": "ZOc-" + automation_room_name + "Occupancy Update" + "-" + room_name
  }
  automation_occupancy["id"] = get_id_from_alias(automation_occupancy["alias"])

  motion_group = "group." + room_entity + "_motion_group"

  return {
    "motion_group": motion_group,
    "occupancy_group": "group." + room_entity + "_occupancy_group",
    "bed_motion_sensors": ["binary_sensor." + room_entity + "_bed_motion_sensor_motion"] if room_type == 'bedroom' else [],
    "non_bed_motion_sensors": [],
    "all_motion_sensors": ["uninitialized_all_motion_sensors"],
    "entrance_motion_sensors": ["binary_sensor." + room_entity + "_entrance_motion_sensor_motion"] if room_type == 'bedroom' else [motion_group],
    "room_occupancy": "input_select." + room_entity + "_occupancy",
    "sleep_time": "input_boolean." + room_entity + "_sleep_time" if room_type == 'bedroom' else "input_boolean.always_off_constant",
    "entered_to_inside_timeout": 2*60+30,
    "inside_to_outside_timeout": 1*60 if room_type == 'landing' else 5*60,
    "sleep_to_outside_timeout": 60*60,
    "inside_to_sleep_timeout": 30*60,
    "automation_occupancy": automation_occupancy,
    "occupancy_state_duration": 4,
    "occupancy_on_x_min_ratio_sensor": "unitialized_ratio_sensor",
    "occupancy_on_2x_min_ratio_sensor": "unitialized_ratio_sensor",
    "set_to_outside_when_no_motion": "no",
    "occupancy_override_entity": "input_boolean." + room_entity + "_auto_off_suspended",
    "occupancy_override_timer_entity": "timer." + room_entity + "_auto_off_suspended_timer",
    "occupancy_override_default_timeout": "02:00:00",
  }
