import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import offline_device_automation_helpers


def set_service(entity_id, state):
    return {
        "service": "homeassistant.turn_" + state,
        "entity_id": entity_id,
    }


class OfflineDeviceAutomationHelpersTest(unittest.TestCase):
    def test_offline_device_notification_without_gateway_restart(self):
        self.assertEqual(
            offline_device_automation_helpers.offline_device_notification_automation(
                "Kitchen ",
                "Kitchen",
                "Light",
                "light.kitchen_ceiling",
                "Kitchen",
                "N/A",
                set_service,
            ),
            {
                "alias": "ZN-Kitchen Notify Light Offline Devices -Kitchen",
                "configured": True,
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": "light.kitchen_ceiling",
                        "to": "unavailable",
                        "for": "00:03:00",
                    }
                ],
                "action": [
                    {
                        "service": "script.notify_alexa_speakers_and_phones",
                        "data": {
                            "tts_message": "Kitchen Offline device: light.kitchen_ceiling",
                            "notify_tai": "yes",
                        },
                    }
                ],
            },
        )

    def test_offline_device_notification_with_gateway_restart(self):
        automation = offline_device_automation_helpers.offline_device_notification_automation(
            "Kitchen ",
            "Kitchen",
            "Gateway",
            "sensor.kitchen_gateway",
            "Kitchen",
            "switch.kitchen_gateway",
            set_service,
        )

        self.assertEqual(
            automation["action"][1:],
            [
                {
                    "service": "homeassistant.turn_off",
                    "entity_id": "switch.kitchen_gateway",
                },
                {"delay": "00:00:02"},
                {
                    "service": "homeassistant.turn_on",
                    "entity_id": "switch.kitchen_gateway",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
