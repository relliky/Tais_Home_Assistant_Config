def build_occupancy_ratio_sensor_config(
    x_minutes_multiple_str,
    occupancy_state_duration,
    room_name,
    motion_group,
    cfg_occupancy,
    get_entity_from_name,
):
  x_minutes_multiple = 1 if x_minutes_multiple_str == "1x" else 2 if x_minutes_multiple_str == "2x" else 0
  x_minutes_total = x_minutes_multiple * occupancy_state_duration
  sensor_name = room_name + " Motion On Ratio For Last " + str(x_minutes_total) + " Minutes"

  sensor_update = {}
  if x_minutes_multiple == 1:
    sensor_update = {
      "attribute": "occupancy_on_x_min_ratio_sensor",
      "entity": "sensor." + get_entity_from_name(sensor_name),
    }
  elif x_minutes_multiple == 2:
    sensor_update = {
      "attribute": "occupancy_on_2x_min_ratio_sensor",
      "entity": "sensor." + get_entity_from_name(sensor_name),
    }

  return {
    "sensor_update": sensor_update,
    "ratio_sensor_config": {
      "platform": "history_stats",
      "name": sensor_name,
      "entity_id": motion_group,
      "state": "on",
      "type": "ratio",
      "duration": {
        "minutes": str(x_minutes_total)
      },
      "end": "{{ (now() | as_timestamp) | as_datetime | as_local }}",
      "configured": cfg_occupancy,
    },
  }
