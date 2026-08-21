import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import entity_declaration_builders


class EntityDeclarationBuildersTest(unittest.TestCase):
    def test_simple_group(self):
        self.assertEqual(
            entity_declaration_builders.simple_group("Kitchen Lights", ["light.kitchen"]),
            [
                {
                    "platform": "group",
                    "name": "Kitchen Lights",
                    "entities": ["light.kitchen"],
                    "configured": True,
                }
            ],
        )

    def test_wifi_reconnect_automation(self):
        automation = entity_declaration_builders.wifi_reconnect_automation(
            entity_id="light.test",
            name="Test Light",
            automation_room_name="TR ",
            room_name="Test Room",
            unavailable_period="00:02:00",
            unavailable_device_id="abc123",
        )

        self.assertEqual(
            automation["alias"],
            "ZR-TR Reconnect Test Light When unavailable-Test Room",
        )
        self.assertEqual(automation["triggers"][0]["entity_id"], "light.test")
        self.assertEqual(automation["triggers"][0]["for"], "00:02:00")
        self.assertEqual(automation["actions"][0]["data"], {"device_id": "abc123"})
        self.assertEqual(automation["actions"][1], {"delay": "01:00:00"})

    def test_power_cycle_switch_when_entities_all_unavailable(self):
        automation = entity_declaration_builders.power_cycle_switch_when_entities_all_unavailable(
            entity_ids=["lock.test", "sensor.test_battery", "binary_sensor.test_mode"],
            name="Test Lock",
            automation_room_name="TR ",
            room_name="Test Room",
            unavailable_period="00:03:00",
            power_switch_entity_id="switch.gateway_power",
        )

        self.assertEqual(
            automation["alias"],
            "ZR-TR Power Cycle Test Lock Gateway When All Entities unavailable-Test Room",
        )
        self.assertEqual(
            automation["triggers"],
            [
                {
                    "trigger": "state",
                    "entity_id": [
                        "lock.test",
                        "sensor.test_battery",
                        "binary_sensor.test_mode",
                    ],
                    "to": "unavailable",
                    "for": "00:03:00",
                    "id": "entities_unavailable",
                },
                {
                    "trigger": "homeassistant",
                    "event": "start",
                    "id": "homeassistant_start",
                },
            ],
        )
        self.assertNotIn("conditions", automation)
        self.assertEqual(
            automation["actions"][:4],
            [
                {
                    "if": [
                        {
                            "condition": "trigger",
                            "id": "homeassistant_start",
                        },
                    ],
                    "then": [
                        {"delay": "00:05:00"},
                    ],
                },
                {
                    "condition": "state",
                    "entity_id": "lock.test",
                    "state": "unavailable",
                    "for": "00:03:00",
                },
                {
                    "condition": "state",
                    "entity_id": "sensor.test_battery",
                    "state": "unavailable",
                    "for": "00:03:00",
                },
                {
                    "condition": "state",
                    "entity_id": "binary_sensor.test_mode",
                    "state": "unavailable",
                    "for": "00:03:00",
                },
            ],
        )
        self.assertEqual(
            automation["actions"][4:7],
            [
                {
                    "action": "switch.turn_off",
                    "target": {"entity_id": "switch.gateway_power"},
                },
                {"delay": "00:00:02"},
                {
                    "action": "switch.turn_on",
                    "target": {"entity_id": "switch.gateway_power"},
                },
            ],
        )
        self.assertEqual(automation["mode"], "single")

        automation = entity_declaration_builders.power_cycle_switch_when_entities_all_unavailable(
            entity_ids=["lock.test", "sensor.test_battery", "binary_sensor.test_mode"],
            name="Test Lock",
            automation_room_name="TR ",
            room_name="Test Room",
            unavailable_period="00:03:00",
            power_switch_entity_id="switch.gateway_power",
            reload_config_entry_id="config-entry-123",
        )
        self.assertEqual(automation["actions"][7], {"delay": "00:00:30"})
        self.assertEqual(
            automation["actions"][8],
            {
                "action": "homeassistant.reload_config_entry",
                "data": {"entry_id": "config-entry-123"},
            },
        )


if __name__ == "__main__":
    unittest.main()
