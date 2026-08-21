def mirror_sensor_on_automation(
  automation_room_name,
  room_name,
  mirror_sensors,
  ceiling_lights,
):
  return {
    "alias":"ZLM-" + automation_room_name + "Mirror Sensor On Turns On Ceiling Light With Cool Temperature" + "-" + room_name,
    "configured": len(mirror_sensors) > 0,
    "trigger": [
      {
        "platform": "state",
        "entity_id": mirror_sensors,
        "from": "off",
        "to":  "on"
      }
    ],
    'mode': 'restart',
    "action": [
      {
        "condition": "state",
        "entity_id": mirror_sensors,
        "state":  "on"
      },
      { "delay": "00:00:01" },
      { "service": "light.turn_on",
        "target":  {"entity_id": ceiling_lights},
        "data":    {"brightness_pct": 100,
                    "color_temp_kelvin": 6500}
      }
    ]
  }


def mirror_sensor_off_automation(
  automation_room_name,
  room_name,
  mirror_sensors,
  room_occupancy,
  al_adapt_brightness,
):
  return {
    "alias":"ZLM-" + automation_room_name + "Mirror Sensor Off Turns Ceiling Light With Adaptive Lighting Unless it's off" + "-" + room_name,
    "configured": len(mirror_sensors) > 0,
    "trigger": [
      {
        "platform": "state",
        "entity_id": mirror_sensors,
        "from": "on",
        "to":  "off"
      }
    ],
    'mode': 'restart',
    "action": [
      { "delay": "00:00:01" },
      {
        "condition": "state",
        "entity_id": room_occupancy,
        "state":  ['Just Entered', 'Stayed Inside'],
      },
      { "service": "adaptive_lighting.apply",
        "data":    {"entity_id": al_adapt_brightness}
      }
    ]
  }
