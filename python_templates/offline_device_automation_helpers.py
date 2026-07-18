def offline_device_notification_automation(
  automation_room_name,
  room_name,
  device_type,
  offline_device,
  tts_message,
  gateway_power_switch,
  set_service,
):
  return {
    "alias": "ZN-" + automation_room_name + "Notify " + device_type + " Offline Devices " + "-" + room_name,
    "configured": True,
    "trigger": [
      {
        "platform": "state",
        "entity_id": offline_device,
        "to": "unavailable",
        "for": "00:03:00"
      }
    ],
    "action": [
      {
        "service": "script.notify_alexa_speakers_and_phones",
        "data": {
          "tts_message": tts_message + " Offline device: " + offline_device,
          "notify_tai": "yes"
        }
      }
      ] + ([
        set_service(gateway_power_switch, "off"),
        {"delay": "00:00:02"},
        set_service(gateway_power_switch, "on")
      ] if gateway_power_switch != 'N/A' else [])
  }
