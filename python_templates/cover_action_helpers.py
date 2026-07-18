def cover_position_step_action(curtains, step_value):
  return {"service": "cover.set_cover_position",
          "target":{"entity_id": curtains},
          "data":  {"position": "{{ [[ (state_attr('" + curtains[0] + "', 'current_position')) + " + str(step_value) + " ,0]|max,100]|min}}"}}


def shutter_blind_position_action(curtains, above, position):
  return {'if': {"condition": "numeric_state",
                 "entity_id": curtains,
                 "attribute": "current_position",
                 "above": above,},
          'then': {"service": "cover.set_cover_position",
                   "data":    {"position": position},
                   "entity_id": curtains}
          }


def cover_open_if_closed_action(curtains, entity_list):
  return {'if': {"condition": "numeric_state",
                 "entity_id": curtains,
                 "attribute": "current_position",
                 "below": 5},
          'then': {"service":  "cover.open_cover",
                  "entity_id": entity_list}
          }


def cover_close_if_open_action(curtains, entity_list):
  return {'if': {"condition": "numeric_state",
                 "entity_id": curtains,
                 "attribute": "current_position",
                 "above": 95},
          'then': {"service":  "cover.close_cover",
                   "entity_id": entity_list}
          }


def cover_toggle_action(entity_list, set_service):
  return {
    "if": [
      {
        'alias': 'toggle all curtains together: if any of curtains is on, turn off all curtains, otherwise turn on all curtains',
        "condition": "state",
        "entity_id": entity_list,
        "state": ['open', 'opening'],
        "match": 'any'
      }
    ],
    "then": set_service(entity_list, 'off'),
    "else": set_service(entity_list, 'on')
  }


def stop_cover_before_action(entity_list, action_service):
  return [{"service":  "cover.stop_cover",
           "entity_id": entity_list},
          action_service]
