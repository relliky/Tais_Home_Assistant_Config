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


def power_cycle_switch_when_entities_all_unavailable(entity_ids, name, automation_room_name, room_name, unavailable_period, power_switch_entity_id, reload_config_entry_id=None):
  actions = [
    {
      "if": [
        {
          "condition": "trigger",
          "id": "homeassistant_start",
        },
      ],
      "then": [
        {"delay": "00:05:00"},
      ],
    },
  ]
  actions += [
    {
      "condition": "state",
      "entity_id": entity_id,
      "state": "unavailable",
      "for": unavailable_period,
    } for entity_id in entity_ids
  ]
  actions += [
    {
      "action": "switch.turn_off",
      "target": {"entity_id": power_switch_entity_id},
    },
    {"delay": "00:00:02"},
    {
      "action": "switch.turn_on",
      "target": {"entity_id": power_switch_entity_id},
    },
  ]
  if reload_config_entry_id:
    actions += [
      {"delay": "00:00:30"},
      {
        "action": "homeassistant.reload_config_entry",
        "data": {"entry_id": reload_config_entry_id},
      },
    ]

  return {
    "alias": "ZR-" + automation_room_name + "Power Cycle " + name + " Gateway When All Entities unavailable" + "-" + room_name,
    "configured": True,
    "triggers": [
      {
        "trigger": "state",
        "entity_id": entity_ids,
        "to": "unavailable",
        "for": unavailable_period,
        "id": "entities_unavailable",
      },
      {
        "trigger": "homeassistant",
        "event": "start",
        "id": "homeassistant_start",
      },
    ],
    "actions": actions,
    "mode": "single",
  }
