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


def tuya_light_reload_when_state_does_not_update(entity_id, name, automation_room_name, room_name, reload_config_entry_id, expected_state_entity_id, check_delay='00:00:20'):
  entity_id_condition_template = (
    "{% set service_data = trigger.event.data.service_data | default({}) %}"
    "{% set raw_entity_ids = service_data.entity_id | default([]) %}"
    "{% set entity_ids = [raw_entity_ids] if raw_entity_ids is string else raw_entity_ids %}"
    "{{ trigger.event.data.domain in ['light', 'homeassistant'] "
    "and trigger.event.data.service in ['turn_on', 'turn_off', 'toggle'] "
    "and '" + entity_id + "' in entity_ids }}"
  )
  stale_state_template = (
    "{{ states(tuya_light_entity) != states(tuya_expected_state_entity) }}"
  )

  return {
    "alias": "ZR-" + automation_room_name + "Reload Tuya Integration When " + name + " State Does Not Update" + "-" + room_name,
    "configured": True,
    "triggers": [
      {
        "trigger": "event",
        "event_type": "call_service",
      },
    ],
    "conditions": [
      {
        "condition": "template",
        "value_template": entity_id_condition_template,
      },
    ],
    "actions": [
      {
        "variables": {
          "tuya_light_entity": entity_id,
          "tuya_expected_state_entity": expected_state_entity_id,
          "tuya_command": "{{ trigger.event.data.service }}",
        },
      },
      {
        "if": [{"condition": "template", "value_template": "{{ tuya_command == 'turn_on' }}"}],
        "then": [{"action": "input_boolean.turn_on", "target": {"entity_id": expected_state_entity_id}}],
        "else": [
          {
            "if": [{"condition": "template", "value_template": "{{ tuya_command == 'turn_off' }}"}],
            "then": [{"action": "input_boolean.turn_off", "target": {"entity_id": expected_state_entity_id}}],
            "else": [{"action": "input_boolean.toggle", "target": {"entity_id": expected_state_entity_id}}],
          },
        ],
      },
      {"delay": check_delay},
      {
        "if": [
          {
            "condition": "template",
            "value_template": stale_state_template,
          },
        ],
        "then": [
          {
            "action": "homeassistant.reload_config_entry",
            "data": {"entry_id": reload_config_entry_id},
          },
        ],
      },
    ],
    "mode": "restart",
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
