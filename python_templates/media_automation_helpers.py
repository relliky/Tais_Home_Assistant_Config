def left_room_media_pause_delay(room_entity):
  return "00:10:00" if room_entity == 'corridor' else "00:00:01"


def sonos_pause_after_people_left_automation(
  automation_room_name,
  room_name,
  room_entity,
  room_occupancy,
  media_players,
  time_pattern_triggers,
  set_service,
):
  delay = left_room_media_pause_delay(room_entity)
  return {
    "alias" : "ZM-" + automation_room_name + "Sonos Pause Playing After People Left" + "-" + room_name,
    "configured": (len(media_players) > 0),
    "trigger": [
      { "platform": "state",
        "entity_id": room_occupancy,
        "to": "Outside",
        "for": delay,
      }
    ] + time_pattern_triggers,
    "action":
      [
        { "condition": "state",
          "entity_id": room_occupancy,
          "state": "Outside",
          "for": delay,
        },
        set_service(media_players, 'off')
      ]
  }
