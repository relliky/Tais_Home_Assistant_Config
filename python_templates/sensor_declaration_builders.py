def event_binary_sensor(entity_id, name, attribute_name='Button Type', attribute_value=1, auto_off=0.2):
  value_literal = "'" + attribute_value + "'" if isinstance(attribute_value, str) else str(attribute_value)
  return {
    "trigger": [
      {
        "platform": "state",
        "entity_id": entity_id,
        "not_from": [
          "unknown",
          "unavailable"
        ]
      }
    ],
    "binary_sensor": [
      {
        "name": name,
        "state": "{{ trigger.to_state.attributes['" + attribute_name + "'] == " + value_literal + " }}",
        "auto_off": auto_off
      }
    ],
    "configured": True
  }


def smooth_power_sensor(sensor_in, sensor_out, get_name_from_entity):
  return smooth_filter_sensor(
    sensor_in,
    sensor_out,
    time_constant=5,
    precision=1,
    get_name_from_entity=get_name_from_entity,
  )


def smooth_temperature_sensor(sensor_in, sensor_out, get_name_from_entity):
  return smooth_filter_sensor(
    sensor_in,
    sensor_out,
    time_constant=4,
    precision=1,
    get_name_from_entity=get_name_from_entity,
  )


def smooth_filter_sensor(sensor_in, sensor_out, time_constant, precision, get_name_from_entity):
  return {
    "name": get_name_from_entity(sensor_out),
    "platform": "filter",
    "entity_id": sensor_in,
    "filters": {
      "filter": "lowpass",
      "time_constant": time_constant,
      "precision": precision,
    },
    "configured": True
  }
