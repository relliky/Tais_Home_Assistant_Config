import random


def get_time_pattern_trigger(minutes=30, ha_start_trigger=True):
  time_pattern_trigger =  {
    "minutes": "/" + str(minutes),
    "seconds": str(random.randint(0, 59)),
    "trigger": "time_pattern"
  }

  ha_start_trigger_config = {
   "trigger": "homeassistant",
    "event": "start",
  }

  return [ha_start_trigger_config, time_pattern_trigger] if ha_start_trigger else [time_pattern_trigger]


def select_input_select_option(entity_id, option):
  return {
    "service": "input_select.select_option",
    "target": {"entity_id": entity_id},
    "data": {"option": option}
  }


def state_duration_template_condition(entity_id, state, seconds, op=">="):
  return {
    "condition": "template",
    "value_template": "{{ is_state('" + entity_id + "', '" + state + "') and (as_timestamp(now()) - as_timestamp(states['" + entity_id + "'].last_changed)) " + op + " " + str(int(seconds)) + " }}"
  }


def always_on_condition():
  return ['{{ 1 == 1 }}']


def entity_is_on(entity):
  return  { "condition": "state",
            "entity_id": entity,
            "state": "on"
          }


def continue_if(entity_id, state, attribute=None, lastFor=None):
  cond =  { "condition": "state",
            "entity_id": entity_id,
            "state":     state
          }
  cond |= {"attribute": attribute} if attribute  != None else {}
  cond |= {"for":       lastFor}   if lastFor    != None else {}
  return cond


def wrap_service_sequence(service_list, alias=''):
  return {"alias": alias, "if": always_on_condition(), "then": service_list}


def assign_automation_ids(automation_list, get_id_from_alias):
  for automation in automation_list:
    automation['id'] = get_id_from_alias(automation['alias'])


def automation_turn_off(entity_id, stop_actions=False):
  return {
    "service": "automation.turn_off",
    "entity_id": entity_id,
    "data": {"stop_actions": stop_actions}
  }


def automation_trigger(entity_id):
  return {
    "service": "automation.trigger",
    "entity_id": entity_id,
  }


def do_nothing_service():
  return {"service": "script.do_nothing"}
