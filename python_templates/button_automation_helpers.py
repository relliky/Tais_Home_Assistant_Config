def button_toggle_automation(
  automation_room_name,
  room_name,
  configured,
  switch_type,
  button_state_name,
  device_name,
  button_list,
  button_state_list,
  device_list,
  set_service,
):
  return {
    "alias":"ZLB-" + automation_room_name + switch_type + " - " + button_state_name + " Press - Toggle " + device_name + "-" + room_name,
    "configured": configured,
    "trigger": [
      {
        "platform": "state",
        "entity_id": button_list,
        "to": button_state_list
      }
    ],
    "action": [set_service(device_list, "toggle")]
  }


def flex_wall_switch_restore_automation(
  automation_room_name,
  room_name,
  flex_wall_switch_index,
  flex_wall_switch_entity,
  set_service,
):
  return {
    "alias":"ZLB-" + automation_room_name + "Flex Wall Switch On Postion " + str(flex_wall_switch_index)  + "- Automatically Turn on the Wall Switch Back When Turned Off -" + room_name,
    "configured": True,
    "trigger": [
      {
        "platform": "state",
        "entity_id": flex_wall_switch_entity,
        "to": "off"
      }
    ],
    "action": [
      set_service(flex_wall_switch_entity, "on"),
      {"delay": "00:00:01"},
      set_service(flex_wall_switch_entity, "on"),
      {"delay": "00:00:01"},
      set_service(flex_wall_switch_entity, "on"),
    ],
    "mode": "queued",
  }
