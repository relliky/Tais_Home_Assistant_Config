def numeric_state_or_unavailable(entity_id, numeric_key, numeric_value):
  return {
    "condition": "or",
    "conditions": [
      {
        "condition": "numeric_state",
        "entity_id": entity_id,
        numeric_key: numeric_value,
      },
      {
        "condition": "state",
        "entity_id": entity_id,
        "state": [
          "unavailable",
          "unknown",
        ],
      },
    ],
  }


def sun_state_or_unavailable(state):
  return {
    "condition": "or",
    "conditions": [
      {
        "condition": "state",
        "entity_id": "sun.sun",
        "state": state,
      },
      {
        "condition": "state",
        "entity_id": "sun.sun",
        "state": [
          "unavailable",
          "unknown",
        ],
      },
    ],
  }


LIGHT_INTENSITY_CONDITIONS = [
  'intense light summer',
  'moderate light outdoor',
  'low light outdoor',
  'sleep mode',
]


def light_intensity_template_condition(
    light_intensity_entity,
    threshold_entity,
    comparison,
):
  return {
    "condition": "template",
    "value_template": "{{ states('" + light_intensity_entity + "') | float(0) " +
                      comparison +
                      " states('" + threshold_entity + "') | float(0) }}",
  }


def adaptive_lighting_sleep_mode_condition(al_sleep_mode, state):
  return {
    "condition": "state",
    "entity_id": al_sleep_mode,
    "state": state,
  }


def light_intensity_condition_list(
    condition_name,
    light_intensity_entity,
    light_intensity_threshold_when,
    outside_temperature,
    west_face_windows,
    al_sleep_mode,
):
  if condition_name not in LIGHT_INTENSITY_CONDITIONS:
    return None

  if condition_name == 'sleep mode':
    return [adaptive_lighting_sleep_mode_condition(al_sleep_mode, 'on')]

  if condition_name == 'intense light summer':
    cond = [
      light_intensity_template_condition(
        light_intensity_entity,
        light_intensity_threshold_when['intense light summer'],
        ">",
      ),
      {
        "condition": "numeric_state",
        "entity_id": outside_temperature,
        "above": "12" if west_face_windows else "15",
      },
      {
        "condition": "template",
        "value_template": "{{ now().month > 4 and now().month < 9 }}",
      },
    ]
  elif condition_name == 'moderate light outdoor':
    cond = [
      light_intensity_template_condition(
        light_intensity_entity,
        light_intensity_threshold_when['moderate light outdoor'],
        ">",
      )
    ]
  else:
    cond = [
      light_intensity_template_condition(
        light_intensity_entity,
        light_intensity_threshold_when['moderate light outdoor'],
        "<=",
      )
    ]

  cond += [adaptive_lighting_sleep_mode_condition(al_sleep_mode, 'off')]
  return cond
