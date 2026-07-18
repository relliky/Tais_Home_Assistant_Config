def kitchen_camera_automations(automation_room_name, room_name, room_occupancy, time_pattern_triggers):
  return [
    {
      "alias" : "ZM-" + automation_room_name + "Reset Camera Position After People Left" + "-" + room_name,
      "configured": True,
      "trigger": [
        { "platform": "state",
          "entity_id": room_occupancy,
          "to": "Outside",
          "for": "00:10:00",
        },
      ] + time_pattern_triggers,
      "actions": {"action": "script.kitchen_camera_pointing_to_door"}
    },
    {
      "alias" : "ZM-" + automation_room_name + "Point Camera To the Table When People Enter" + "-" + room_name,
      "configured": True,
      "trigger": [
        { "platform": "state",
          "entity_id": room_occupancy,
          "from": "Outside",
          "to": "Just Entered",
        },
      ],
      "actions": {"action": "script.kitchen_camera_pointing_to_dining_table"}
    }
  ]
