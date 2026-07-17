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


def battery_sensor_declarations(mac, name, get_entity_from_name, get_name_from_entity):
  raw_sensor = "sensor." + mac + ""
  entity_postfix = get_entity_from_name(name)
  median_sensor = "sensor." + entity_postfix + "_median"

  return {
    "sensor_list_additions": [
      {
        "name": get_name_from_entity(median_sensor),
        "platform": "statistics",
        "entity_id": raw_sensor,
        "precision": 0,
        "state_characteristic": "median",
        "max_age": {"hours": 24},
        "configured": True
      }
    ],
    "template_list_additions": [
      {
        "sensor": [
          {
            "name": name,
            "unit_of_measurement": "%",
            "device_class": "battery",
            "state_class": "measurement",
            "state": "{% set s = states('" + median_sensor + "') %}" +
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
            "{% if   states('"+sensor_1 +"') != 'unavailable' and states('" + sensor_2 + "') == 'unavailable' %}" +
               "{{states('"+sensor_1 +"')}}" +
            "{% elif states('"+sensor_1 +"') == 'unavailable' and states('" + sensor_2 + "') != 'unavailable' %}" +
               "{{states('"+sensor_2 +"')}}" +
            "{% else %}" +
              "{% set sensor_1 = states('"+sensor_1 +"') | float(22) | round(1) %}" +
              "{% set sensor_2 = states('"+sensor_2 +"') | float(22) | round(1) %}" +
              "{% if sensor_1 < 1.0 or sensor_2 < 1.0 or (sensor_1 + sensor_2) < 1.0 %}" +
                 "22.0" +
              "{% else %}" +
                 "{{ ((sensor_1 + sensor_2) / 2) | round(1) }}" +
              "{% endif %}" +
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
