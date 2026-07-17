import automation_helpers


def get_occupancy_state_machine_actions(room_occupancy,
                                        motion_group,
                                        sleep_time,
                                        set_to_outside_when_no_motion,
                                        entered_to_inside_timeout,
                                        inside_to_sleep_timeout,
                                        inside_to_outside_timeout,
                                        sleep_to_outside_timeout):
  select_outside      = automation_helpers.select_input_select_option(room_occupancy, "Outside")
  select_just_entered = automation_helpers.select_input_select_option(room_occupancy, "Just Entered")
  select_stayed       = automation_helpers.select_input_select_option(room_occupancy, "Stayed Inside")
  select_sleep        = automation_helpers.select_input_select_option(room_occupancy, "In Sleep")

  choose_list = [
    {
      "alias": "Outside -> Just Entered when motion is on",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "Outside"},
        {"condition": "state", "entity_id": motion_group, "state": "on"},
      ],
      "sequence": [select_just_entered]
    },
    {
      "alias": "Outside -> Outside when motion is not on",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "Outside"},
        {"condition": "template", "value_template": "{{ not is_state('" + motion_group + "', 'on') }}"},
      ],
      "sequence": [select_outside]
    },
    {
      "alias": "Just Entered -> Stayed Inside when motion stays on",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "Just Entered"},
        automation_helpers.state_duration_template_condition(motion_group, "on", entered_to_inside_timeout, ">="),
      ],
      "sequence": [select_stayed]
    },
    {
      "alias": "Just Entered -> Outside when motion stays off",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "Just Entered"},
        automation_helpers.state_duration_template_condition(motion_group, "off", inside_to_outside_timeout, ">="),
      ],
      "sequence": [select_outside]
    },
  ]

  if set_to_outside_when_no_motion == 'yes':
    choose_list += [
      {
        "alias": "Just Entered -> Outside when no motion is authoritative",
        "conditions": [
          {"condition": "state", "entity_id": room_occupancy, "state": "Just Entered"},
          {"condition": "state", "entity_id": motion_group, "state": "off"},
        ],
        "sequence": [select_outside]
      }
    ]

  choose_list += [
    {
      "alias": "Just Entered -> Just Entered by default",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "Just Entered"},
      ],
      "sequence": [select_just_entered]
    },
    {
      "alias": "Stayed Inside -> In Sleep when sleep time and stayed long enough",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "Stayed Inside"},
        {"condition": "state", "entity_id": sleep_time, "state": "on"},
        automation_helpers.state_duration_template_condition(room_occupancy, "Stayed Inside", inside_to_sleep_timeout, ">"),
      ],
      "sequence": [select_sleep]
    },
    {
      "alias": "Stayed Inside -> Outside when motion stays off",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "Stayed Inside"},
        automation_helpers.state_duration_template_condition(motion_group, "off", inside_to_outside_timeout, ">="),
      ],
      "sequence": [select_outside]
    },
  ]

  if set_to_outside_when_no_motion == 'yes':
    choose_list += [
      {
        "alias": "Stayed Inside -> Outside when no motion is authoritative",
        "conditions": [
          {"condition": "state", "entity_id": room_occupancy, "state": "Stayed Inside"},
          {"condition": "state", "entity_id": motion_group, "state": "off"},
        ],
        "sequence": [select_outside]
      }
    ]

  choose_list += [
    {
      "alias": "Stayed Inside -> Stayed Inside by default",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "Stayed Inside"},
      ],
      "sequence": [select_stayed]
    },
    {
      "alias": "In Sleep -> Stayed Inside when sleep time ends",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "In Sleep"},
        {"condition": "template", "value_template": "{{ not is_state('" + sleep_time + "', 'on') }}"},
      ],
      "sequence": [select_stayed]
    },
    {
      "alias": "In Sleep -> Outside when motion stays off",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "In Sleep"},
        automation_helpers.state_duration_template_condition(motion_group, "off", sleep_to_outside_timeout, ">"),
      ],
      "sequence": [select_outside]
    },
    {
      "alias": "In Sleep -> In Sleep by default",
      "conditions": [
        {"condition": "state", "entity_id": room_occupancy, "state": "In Sleep"},
      ],
      "sequence": [select_sleep]
    },
  ]

  return [{
    "choose": choose_list,
    "default": [{"service": "script.do_nothing"}]
  }]
