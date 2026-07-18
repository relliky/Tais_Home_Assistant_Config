def reset_picture_mode_automation(automation_room_name, room_name, tvs, set_service):
  return {
    "alias": "ZTV-" + automation_room_name + "Reset Picture Mode When Turning on TV" + "-" + room_name,
    "configured": len(tvs) > 0,
    "trigger": [
      {
        "platform": "state",
        "entity_id": tvs,
        "from": "off",
        "to": "on"
      }
    ],
    "action": [
      set_service(tvs, tv_brightness=3)
    ]
  }
