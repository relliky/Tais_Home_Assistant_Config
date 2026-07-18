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
