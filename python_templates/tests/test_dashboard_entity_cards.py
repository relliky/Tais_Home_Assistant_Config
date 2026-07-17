import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import dashboard_entity_cards


class DashboardEntityCardsTest(unittest.TestCase):
    def test_get_entity_domain(self):
        self.assertEqual(
            dashboard_entity_cards.get_entity_domain("light.master_room_ceiling_light"),
            "light",
        )

    def test_infer_mushroom_domain_cards(self):
        self.assertEqual(
            dashboard_entity_cards.infer_entity_card_type("light.master_room_ceiling_light"),
            "custom:mushroom-light-card",
        )
        self.assertEqual(
            dashboard_entity_cards.infer_entity_card_type("cover.master_room_curtain"),
            "custom:mushroom-cover-card",
        )
        self.assertEqual(
            dashboard_entity_cards.infer_entity_card_type("climate.master_room"),
            "custom:mushroom-climate-card",
        )

    def test_infer_other_known_cards(self):
        cases = {
            "media_player.living_room_tv": "custom:mushroom-media-player-card",
            "binary_sensor.master_room_motion": "custom:mushroom-entity-card",
            "switch.master_room_socket": "custom:mushroom-entity-card",
            "input_boolean.master_room_sleep_time": "custom:mushroom-entity-card",
            "group.master_room_light_group": "custom:auto-entities",
            "sensor.master_room_temperature": "sensor",
            "input_select.master_room_scene": "custom:mushroom-select-card",
            "input_number.master_room_default_temperature": "custom:mushroom-number-card",
            "number.master_room_volume": "custom:mushroom-number-card",
        }

        for entity, expected_card_type in cases.items():
            with self.subTest(entity=entity):
                self.assertEqual(
                    dashboard_entity_cards.infer_entity_card_type(entity),
                    expected_card_type,
                )

    def test_unknown_entity_domain_returns_none(self):
        self.assertIsNone(dashboard_entity_cards.infer_entity_card_type("button.master_room"))


if __name__ == "__main__":
    unittest.main()
