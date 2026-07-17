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
