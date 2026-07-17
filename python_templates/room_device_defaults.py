def default_mirror_entities():
  return {
    "mirror_sensors": [],
    "demisters": [],
    "shower_sensors": [],
  }


def default_tv_entities():
  return {
    "tv_room_entity": None,
    "tvs": [],
    "tv_picture_mode": [],
    "tv_soundbars": [],
    "fire_tvs": [],
    "media_players": [],
  }


def default_cover_entities(room_entity):
  return {
    "curtains": [],
    "aqara_shutter_blind": False,
    "curtain_group": 'group.' + room_entity + '_curtain_group',
  }


def default_window_entities(room_entity):
  return {
    "windows": [],
    "timeout_windows": [],
    "window_group": 'group.' + room_entity + '_window_group',
    "timeout_window_group": 'group.' + room_entity + '_timeout_window_group',
  }


def default_temperature_control_entities(room_entity):
  thermostat = "climate." + room_entity

  return {
    "outside_temperature": "sensor.met_office_cambridge_city_airport_temperature_3_hourly",
    "room_default_temperature": "input_number." + room_entity + "_default_temperature",
    "thermostat": thermostat,
    "thermostat_cloud_tado": thermostat + '_tado',
    "thermostat_schedule": "switch.schedule_" + room_entity + "_temperature",
    "temperature_sensor": "sensor." + room_entity + "_temperature_sensor",
    "room_heating_override": "input_boolean." + room_entity + "_heating_override",
  }
