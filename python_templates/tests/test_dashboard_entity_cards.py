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

    def test_light_card(self):
        card = dashboard_entity_cards.light_card(
            "light.master_room_ceiling_light",
            "Ceiling",
            "",
        )

        self.assertEqual(card["type"], "custom:mushroom-light-card")
        self.assertEqual(card["entity"], "light.master_room_ceiling_light")
        self.assertTrue(card["show_brightness_control"])
        self.assertIn("card_mod", card)
        self.assertIn("rgba(253,204,0,1)", card["card_mod"]["style"])

    def test_cover_card(self):
        card = dashboard_entity_cards.cover_card(
            "cover.master_room_curtain",
            "Curtain",
            "",
        )

        self.assertEqual(card["tap_action"], {"action": "toggle"})
        self.assertEqual(card["icon_tap_action"], {"action": "toggle"})
        self.assertTrue(card["show_position_control"])
        self.assertTrue(card["show_buttons_control"])

    def test_media_player_card(self):
        card = dashboard_entity_cards.media_player_card(
            "media_player.living_room_tv",
            "TV",
            "",
        )

        self.assertEqual(card["tap_action"], {"action": "more-info"})
        self.assertEqual(card["volume_controls"], ["volume_set", "volume_buttons"])
        self.assertFalse(card["show_volume_level"])

    def test_group_and_entities_cards(self):
        self.assertEqual(
            dashboard_entity_cards.group_card("group.master_room_light_group", "Lights"),
            {
                "type": "custom:auto-entities",
                "card": {
                    "type": "entities",
                    "title": "Lights",
                },
                "filter": {"include": [{"group": "group.master_room_light_group"}]},
            },
        )
        self.assertEqual(
            dashboard_entity_cards.entities_card("timer.master_room", "Timer"),
            {
                "type": "entities",
                "entities": [
                    {
                        "name": "Timer",
                        "entity": "timer.master_room",
                    }
                ],
            },
        )

    def test_scheduler_timer_and_number_cards(self):
        self.assertEqual(
            dashboard_entity_cards.scheduler_card(["climate.master_room"]),
            {
                "type": "custom:scheduler-card",
                "include": ["climate.master_room"],
                "exclude": [],
                "title": True,
                "discover_existing": True,
                "time_step": 30,
            },
        )

        timer = dashboard_entity_cards.flipdown_timer_card("timer.master_room", "Timer", "")
        self.assertEqual(timer["theme"], "dark")
        self.assertEqual(timer["styles"]["rotor"]["width"], "50px")

        number = dashboard_entity_cards.number_card("input_number.master_room_default_temperature", "Default", "")
        self.assertEqual(number["display_mode"], "buttons")
        self.assertEqual(number["icon"], "")

    def test_complex_sensor_card(self):
        card = dashboard_entity_cards.complex_sensor_card(
            "sensor.master_room_temperature",
            "Temperature",
        )

        self.assertEqual(card["type"], "custom:vertical-stack-in-card")
        self.assertEqual(card["cards"][0]["type"], "custom:mushroom-template-card")
        self.assertEqual(card["cards"][0]["entity"], "sensor.master_room_temperature")
        self.assertIn("rgba(245, 245, 245, 0)", card["cards"][0]["card_mod"]["style"])

        graph_card = card["cards"][1]["cards"][0]
        self.assertEqual(graph_card["type"], "custom:mini-graph-card")
        self.assertEqual(
            graph_card["entities"],
            [
                {
                    "entity": "sensor.master_room_temperature",
                    "name": "Temperature",
                }
            ],
        )
        self.assertEqual(graph_card["color_thresholds"][0], {"value": -10, "color": "#0000ff"})
        self.assertTrue(graph_card["animate"])

    def test_header_chips_card(self):
        card = dashboard_entity_cards.header_chips_card()

        self.assertEqual(card["type"], "custom:mod-card")
        self.assertEqual(card["card"]["type"], "custom:button-card")
        self.assertEqual(
            card["card"]["custom_fields"]["a"]["card"]["chips"],
            [{"type": "menu"}],
        )
        self.assertEqual(
            card["card"]["custom_fields"]["b"]["card"]["chips"][0]["entity"],
            "sensor.time",
        )
        self.assertEqual(
            card["card"]["custom_fields"]["c"]["card"]["chips"][0]["entity"],
            "sensor.shi_chen",
        )
        self.assertIn("position: sticky", card["card_mod"]["style"])


if __name__ == "__main__":
    unittest.main()
