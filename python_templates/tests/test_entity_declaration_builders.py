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


if __name__ == "__main__":
    unittest.main()
