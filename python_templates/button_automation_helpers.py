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
