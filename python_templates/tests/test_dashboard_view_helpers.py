import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import dashboard_view_helpers


class DashboardViewHelpersTest(unittest.TestCase):
    def test_build_view(self):
        self.assertEqual(
            dashboard_view_helpers.build_view(
                view_path="kitchen",
                cards=[{"type": "entities"}],
                theme="Mushroom Shadow",
                title="Kitchen",
            ),
            {
                "theme": "Mushroom Shadow",
                "title": "Kitchen",
                "path": "kitchen",
                "subview": True,
                "badges": [],
                "cards": [{"type": "entities"}],
            },
        )

    def test_mobile_layout_wraps_cards_in_grid(self):
        cards = [{"type": "button"}]

        self.assertEqual(
            dashboard_view_helpers.layout_wrapper_cards("mobile", cards=cards),
            [{"square": False, "columns": 2, "type": "grid", "cards": cards}],
        )

    def test_tablet_layout_returns_cards_directly(self):
        cards = [{"type": "button"}]

        self.assertIs(dashboard_view_helpers.layout_wrapper_cards("tablet", cards=cards), cards)

    def test_unknown_layout_raises(self):
        with self.assertRaises(TypeError):
            dashboard_view_helpers.layout_wrapper_cards("bad")

    def test_room_view_cards_for_mobile(self):
        header_cards = [{"type": "header"}]
        main_cards = [{"type": "main"}]
        tail_cards = [{"type": "tail"}]

        self.assertEqual(
            dashboard_view_helpers.room_view_cards(
                "mobile",
                header_cards,
                main_cards,
                tail_cards,
            ),
            [
                {"square": False, "columns": 2, "type": "grid", "cards": header_cards},
                {"square": False, "columns": 2, "type": "grid", "cards": main_cards},
                {"type": "tail"},
            ],
        )

    def test_room_view_cards_for_tablet(self):
        header_cards = [{"type": "header"}]
        main_cards = [{"type": "main"}]
        tail_cards = [{"type": "tail"}]

        self.assertEqual(
            dashboard_view_helpers.room_view_cards(
                "tablet",
                header_cards,
                main_cards,
                tail_cards,
            ),
            [
                {"type": "header"},
                {"type": "main"},
                {"type": "tail"},
            ],
        )

    def test_home_navigation_card_uses_default_home_path(self):
        self.assertEqual(
            dashboard_view_helpers.home_navigation_card("lovelace"),
            {
                "type": "custom:mushroom-template-card",
                "entity": "input_boolean.placeholder",
                "icon": "mdi:keyboard-return",
                "icon_color": "yellow",
                "primary": "HOME",
                "secondary": "",
                "layout": "vertical",
                "hold_action": {
                    "action": "toggle"
                },
                "tap_action": {
                    "action": "navigate",
                    "navigation_path": "lovelace/home",
                },
                "icon_tap_action": {
                    "action": "navigate",
                    "navigation_path": "lovelace/home",
                },
                "card_mod": {
                    "style": {
                        "mushroom-state-info$": ".primary {\n  font-size: 16px !important;\n  position: relative;\n  top: 0px;\n  left: 0px;\n  overflow: visible !important;\n  white-space:  \n}\n",
                        "mushroom-shape-icon$": ".shape {\n  position: relative;\n  left: 0px;\n  top: 0px;\n}\n",
                        ".": ":host {\n  --mush-icon-size: 80px;\n}\n",
                    }
                },
            },
        )

    def test_home_navigation_card_uses_override_path(self):
        card = dashboard_view_helpers.home_navigation_card(
            "lovelace",
            navigate_path="custom/path",
        )

        self.assertEqual(card["tap_action"]["navigation_path"], "custom/path")
        self.assertEqual(card["icon_tap_action"]["navigation_path"], "custom/path")

    def test_header_cards(self):
        scene_card = {"type": "entity", "entity": "input_select.kitchen_scene"}

        cards = dashboard_view_helpers.header_cards(
            "lovelace",
            scene_card,
            navigate_path="custom/path",
        )

        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["tap_action"]["navigation_path"], "custom/path")
        self.assertIs(cards[1], scene_card)

    def test_button_navigation_room_card(self):
        self.assertEqual(
            dashboard_view_helpers.button_navigation_room_card(
                "Kitchen",
                "mdi:fridge",
                "/lovelace/kitchen",
            ),
            {
                "type": "custom:button-card",
                "aspect_ratio": "1/1",
                "tap_action": {
                    "action": "navigate",
                    "navigation_path": "/lovelace/kitchen",
                },
                "icon_tap_action": {
                    "action": "navigate",
                    "navigation_path": "/lovelace/kitchen",
                },
                "entity": "input_boolean.placeholder",
                "show_state": False,
                "name": "Kitchen",
                "icon": "mdi:fridge",
                "show_icon": True,
                "show_name": True,
            },
        )

    def test_navigation_room_secondary_text(self):
        self.assertEqual(
            dashboard_view_helpers.navigation_room_secondary_text(
                "sensor.kitchen_temperature",
                "group.kitchen_motion",
                "kitchen_motion",
            ),
            "{% if states.sensor.kitchen_temperature.state is defined %} {{ states.sensor.kitchen_temperature.state }}\u00b0C {% endif %}"
            "{% set motion_postfix     = 'kitchen_motion' %}\n"
            "{% set motion = 'group.kitchen_motion' %}\n"
            "{% if is_state(motion, 'on') %}\n"
            "  \U0001f64b\U0001f3fb\n"
            "{% else %}\n"
            "  \U0001f9b6\U0001f3fb\n"
            "{% endif %}{{\n"
            " (as_timestamp(now()) -\n"
            " as_timestamp(states.group[motion_postfix].last_changed)) |\n"
            ' timestamp_custom("%H:%M", false) }} ',
        )

    def test_unavailable_status_card(self):
        def template_card(**kwargs):
            return kwargs

        self.assertEqual(
            dashboard_view_helpers.unavailable_status_card(
                "binary_sensor.kitchen_unavailable",
                template_card,
            ),
            {
                "icon": "mdi:battery-charging-outline",
                "icon_color": "red",
                "condition_state": "on",
                "condition_entity": "binary_sensor.kitchen_unavailable",
            },
        )


if __name__ == "__main__":
    unittest.main()
