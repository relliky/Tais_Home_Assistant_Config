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
