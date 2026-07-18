def occupancy_override_to_timer_automation(
  automation_room_name,
  room_name,
  configured,
  occupancy_override_entity,
  occupancy_override_timer_entity,
  room_occupancy,
  occupancy_update_automation_id,
  set_service,
):
  return {
    "alias": "ZOc-"  + automation_room_name + "Occupancy Override and sync to Timer" + "-" + room_name,
    "mode": "single",
    "configured": configured,
    "trigger": [
      {
        "platform": "state",
        "entity_id": occupancy_override_entity
      }
    ],
    "action": [
      {
        "choose": [
          {
            "conditions": [
              {
                "condition": "state",
                "entity_id": occupancy_override_entity,
                "state": "on"
              }
            ],
            "sequence": [
              { "service": "timer.start",
                "target": {"entity_id": occupancy_override_timer_entity}
              },
              set_service(occupancy_update_automation_id, 'off'),
              { "service": "input_select.select_option",
                "target":  {"entity_id": room_occupancy},
                "data":    {"option": "Stayed Inside"},
              },
            ]
          },
          {
            "conditions": [
              {
                "condition": "state",
                "entity_id": occupancy_override_entity,
                "state": "off"
              }
            ],
            "sequence": [
              {"service": "timer.cancel",
                "target": {"entity_id": occupancy_override_timer_entity}
              },
              set_service(occupancy_update_automation_id, 'on'),
            ]
          }
        ]
      }
    ]
  }


def occupancy_update_triggers(
  motion_group,
  entered_to_inside_timeout,
  inside_to_sleep_timeout,
  inside_to_outside_timeout,
  sleep_to_outside_timeout,
  time_pattern_triggers,
):
  return [
    {
      "entity_id": motion_group,
      "platform": "state",
      "to": "on"
    },
    {
      "entity_id": motion_group,
      "platform": "state",
      "to": "on",
      "for": {"seconds":entered_to_inside_timeout},
    },
    {
      "entity_id": motion_group,
      "platform": "state",
      "to": "on",
      "for":  {"seconds":inside_to_sleep_timeout},
    },
    {
      "entity_id": motion_group,
      "platform": "state",
      "to": "off",
    },
    {
      "entity_id": motion_group,
      "platform": "state",
      "to": "off",
      "for": {"seconds":inside_to_outside_timeout},
    },
    {
      "entity_id": motion_group,
      "platform": "state",
      "to": "off",
      "for": {"seconds":sleep_to_outside_timeout },
    }
  ] + time_pattern_triggers


def occupancy_override_from_timer_automation(
  automation_room_name,
  room_name,
  configured,
  occupancy_override_entity,
  occupancy_override_timer_entity,
  time_pattern_triggers,
):
  return {
    "alias": "ZOc-"  + automation_room_name + "Occupancy Override Sync from Timer" + "-" + room_name,
    "mode": "single",
    "configured": configured,
    "trigger": [
      {
        "platform": "state",
        "entity_id": occupancy_override_timer_entity
      }
    ] + time_pattern_triggers,
    "action": [
      {
        "choose": [
          {
            "conditions": [
              {
                "condition": "state",
                "entity_id": occupancy_override_timer_entity,
                "state": "active"
              }
            ],
            "sequence": [
              {
                "service": "input_boolean.turn_on",
                "target": {
                  "entity_id": occupancy_override_entity
                }
              }
            ]
          },
          {
            "conditions": [
              {
                "condition": "or",
                "conditions": [
                  {
                    "condition": "state",
                    "entity_id": occupancy_override_timer_entity,
                    "state": "paused"
                  },
                  {
                    "condition": "state",
                    "entity_id": occupancy_override_timer_entity,
                    "state": "idle"
                  }
                ]
              }
            ],
            "sequence": [
              {
                "service": "input_boolean.turn_off",
                "target": {
                  "entity_id": occupancy_override_entity
                }
              }
            ]
          }
        ]
      }
    ]
  }
