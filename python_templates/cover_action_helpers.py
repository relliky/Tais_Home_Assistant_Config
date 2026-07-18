def cover_position_step_action(curtains, step_value):
  return {"service": "cover.set_cover_position",
          "target":{"entity_id": curtains},
          "data":  {"position": "{{ [[ (state_attr('" + curtains[0] + "', 'current_position')) + " + str(step_value) + " ,0]|max,100]|min}}"}}
