def build_xiaomi_buttons(room_entity, num_of_xiaomi_button):
  buttons = []

  for i in range(num_of_xiaomi_button):
    button = "sensor." + room_entity + "_button"
    if num_of_xiaomi_button != 1:
      button += "_" + str(i + 1)
    buttons += [button]

  return buttons


def default_remote_entities(room_entity, num_of_xiaomi_button):
  xiaomi_buttons = build_xiaomi_buttons(room_entity, num_of_xiaomi_button)
  wall_buttons = [
    "sensor." + room_entity + "_wall_button",
    "sensor." + room_entity + "_wall_button_2",
  ]

  return {
    "xiaomi_buttons": xiaomi_buttons,
    "wall_buttons": wall_buttons,
    "buttons": wall_buttons + xiaomi_buttons,
    "curtain_buttons": [],
    "six_key_buttons": [],
    "four_key_buttons": [],
    "eight_key_knob_buttons": [],
  }


def default_wall_switches():
  return {
    "wall_switches": [],
    "decouple_wall_switches": [],
    "raw_wall_switches": [],
    "alias_wall_switches": [],
  }
