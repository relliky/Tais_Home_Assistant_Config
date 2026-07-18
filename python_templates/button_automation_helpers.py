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


def wall_button_double_leave_room_automation(
  automation_room_name,
  room_name,
  configured,
  wall_buttons,
  lights_off_automation_id,
  heating_off_automation_id,
  room_occupancy,
):
  return {
    "alias":"ZLB-" + automation_room_name + "Wall Switch - Double Click - Leave Room and Turn Off Everything" + "-" + room_name,
    "configured": configured,
    "trigger": [
      {
        "platform": "state",
        "entity_id": wall_buttons,
        "to":  ["2", "double", "double_left", "double_right", "double_center", "button_1_double", "button_2_double", "button_3_double"]
      }
    ],
    "action": [
      { "service": "automation.trigger",
        "entity_id": [lights_off_automation_id,
                      heating_off_automation_id]
      },
      { "service": "input_select.select_option",
        "target":  {"entity_id": room_occupancy},
        "data":    {"option": "Outside"}
      }
    ]
  }
