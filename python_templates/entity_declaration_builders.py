def simple_group(group_name, group_entity_list):
  return [
    {
      "platform": "group",
      "name": group_name,
      "entities": group_entity_list,
      "configured": True
    }
  ]


def wifi_reconnect_automation(entity_id, name, automation_room_name, room_name, unavailable_period, unavailable_device_id):
  return {
    "alias": "ZR-" + automation_room_name + "Reconnect " + name + " When unavailable" + "-" + room_name,
    "configured": True,
    "triggers": [
      {
        "trigger": "state",
        "entity_id": entity_id,
        "to": "unavailable",
        'for': unavailable_period,
      },
    ],
    "actions": [
      {
        "action": "unifi.reconnect_client",
        "data": {"device_id": unavailable_device_id},
      },
      { "delay": '01:00:00'},
    ],
  }
