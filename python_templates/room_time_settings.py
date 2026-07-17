def default_sleep_time_entities():
  return {
    "end_of_sleep_time": "06:30:00",
    "start_of_sleep_time": "23:00:00",
  }


def default_light_time_settings(room_type):
  daytime_lights_off_timeout = "00:15:00"

  return {
    "daytime_lights_off_timeout": daytime_lights_off_timeout,
    "nighttime_lights_off_timeout": "02:00:00" if room_type == "bedroom" else daytime_lights_off_timeout,
    "daytime_start": "06:00:00",
    "afternoon_start": "13:00:00",
    "daytime_end": "21:00:00",
  }
