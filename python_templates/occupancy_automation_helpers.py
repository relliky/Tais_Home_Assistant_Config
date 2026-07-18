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
