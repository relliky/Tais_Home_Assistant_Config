import entity_naming


WEST_FACE_WINDOW_ROOMS = [
  'en_suite_room',
  'en_suite_toilet',
  'master_room',
  'kitchen',
]


def get_room_type(room_entity):
  return 'bedroom'       if (('_room' in room_entity) and ('living_room' != room_entity)) else \
         'toilet'        if '_toilet' in room_entity else \
         'common_area'


def derive_room_properties(room_name, room_short_name):
  room_entity = entity_naming.get_entity_from_name(room_name)

  return {
    "room_entity": room_entity,
    "room_navi_path": room_entity.replace("_", "-"),
    "automation_room_name": room_short_name + " ",
    "room_type": get_room_type(room_entity),
    "west_face_windows": True if room_entity in WEST_FACE_WINDOW_ROOMS else False,
  }
