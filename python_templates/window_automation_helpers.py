def window_is_open_condition(window_group):
  return {
    "condition": "state",
    "entity_id": window_group,
    "state": "on"
  }


def notify_windows_open_action(tts_message, **notify_flags):
  return {
    "service": "script.notify_alexa_speakers_and_phones",
    "data": {
      "tts_message": tts_message,
      **notify_flags
    }
  }


def tenant_notify_flags_for_room(room_entity):
  return {
    "notify_guest_room_tenant": "yes",
    "notify_en_suite_room_tenant": "yes"
  } if room_entity == 'kitchen' else {}
