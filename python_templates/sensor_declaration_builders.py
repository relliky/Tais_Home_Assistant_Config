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


def battery_sensor_declarations(mac, name, get_entity_from_name, get_name_from_entity, smooth_battery=True):
  raw_sensor = "sensor." + mac + ""
  entity_postfix = get_entity_from_name(name)
  median_sensor = "sensor." + entity_postfix + "_median"
  source_sensor = median_sensor if smooth_battery else raw_sensor

  sensor_list_additions = []
  if smooth_battery:
    sensor_list_additions.append({
      "name": get_name_from_entity(median_sensor),
      "platform": "statistics",
      "entity_id": raw_sensor,
      "precision": 0,
      "state_characteristic": "median",
      "max_age": {"hours": 24},
      "configured": True
    })

  return {
    "sensor_list_additions": sensor_list_additions,
    "template_list_additions": [
      {
        "sensor": [
          {
            "name": name,
            "unit_of_measurement": "%",
            "device_class": "battery",
            "state_class": "measurement",
            "state": "{% set s = states('" + source_sensor + "') %}" +
                     "{{ s | int if s not in ['unknown', 'unavailable', ''] else 'unknown' }}"
          }
        ],
        "configured": True
      }
    ],
  }


def average_temperature_sensor(sensor_1, sensor_2, sensor_out, get_name_from_entity):
  return {
    "sensor": [
      {
        "name": get_name_from_entity(sensor_out),
        "unit_of_measurement": "°C",
        "state": "" +
            "{% set unavailable_states = ['unknown', 'unavailable', 'none', ''] %}" +
            "{% set sensor_1_state = states('" + sensor_1 + "') %}" +
            "{% set sensor_2_state = states('" + sensor_2 + "') %}" +
            "{% if sensor_1_state in unavailable_states and sensor_2_state in unavailable_states %}" +
              "unavailable" +
            "{% elif sensor_1_state in unavailable_states %}" +
              "{{ sensor_2_state | float | round(1) }}" +
            "{% elif sensor_2_state in unavailable_states %}" +
              "{{ sensor_1_state | float | round(1) }}" +
            "{% else %}" +
              "{% set sensor_1 = sensor_1_state | float %}" +
              "{% set sensor_2 = sensor_2_state | float %}" +
              "{{ ((sensor_1 + sensor_2) / 2) | round(1) }}" +
            "{% endif %}"
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
