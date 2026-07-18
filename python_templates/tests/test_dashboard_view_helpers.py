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

    def test_navigation_room_title_card(self):
        def template_card(**kwargs):
            return kwargs

        card = dashboard_view_helpers.navigation_room_title_card(
            "mdi:fridge",
            "Kitchen",
            "sensor.kitchen_temperature",
            "group.kitchen_motion",
            "kitchen_motion",
            template_card,
        )

        self.assertEqual(card["icon"], "mdi:fridge")
        self.assertEqual(card["icon_color"], "blue")
        self.assertEqual(card["primary"], "Kitchen")
        self.assertEqual(card["tap_action"], "navigate")
        self.assertEqual(
            card["secondary"],
            dashboard_view_helpers.navigation_room_secondary_text(
                "sensor.kitchen_temperature",
                "group.kitchen_motion",
                "kitchen_motion",
            ),
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

    def test_battery_status_card(self):
        def template_card(**kwargs):
            return kwargs

        self.assertEqual(
            dashboard_view_helpers.battery_status_card(
                "binary_sensor.kitchen_low_battery",
                "group.kitchen_battery",
                template_card,
            ),
            {
                "icon": "{% if is_state('binary_sensor.kitchen_low_battery', 'on') %}\n"
                "  mdi:battery-20-bluetooth \n"
                "{% else %}\n"
                "  mdi:battery-70\n"
                "{% endif %}",
                "icon_color": "{% if is_state('binary_sensor.kitchen_low_battery', 'on') %}\n"
                "  amber\n"
                "{% endif %}",
                "tap_entity": "group.kitchen_battery",
            },
        )

    def test_window_status_card(self):
        def template_card(**kwargs):
            return kwargs

        self.assertEqual(
            dashboard_view_helpers.window_status_card(
                "group.kitchen_window_group",
                template_card,
            ),
            {
                "icon": "{% if is_state(entity, 'on') %}\n"
                "  mdi:window-open-variant\n"
                "{% else %}\n"
                "  mdi:window-closed-variant\n"
                "{% endif %}",
                "icon_color": "{% if is_state(entity, 'on') %}\n"
                "  lime\n"
                "{% endif %}",
                "condition_entity": "group.kitchen_window_group",
            },
        )

    def test_tv_status_card(self):
        def template_card(**kwargs):
            return kwargs

        self.assertEqual(
            dashboard_view_helpers.tv_status_card(
                "media_player.kitchen_tv",
                template_card,
            ),
            {
                "icon": "mdi:television-classic",
                "icon_color": "{% if is_state(entity, 'on') %}\n"
                "  deep-orange\n"
                "{% endif %}",
                "tap_entity": "media_player.kitchen_tv",
                "condition_entity": "media_player.kitchen_tv",
                "condition_state": "on",
            },
        )

    def test_light_status_card(self):
        def template_card(**kwargs):
            return kwargs

        self.assertEqual(
            dashboard_view_helpers.light_status_card(
                "group.kitchen_light_group",
                template_card,
            ),
            {
                "icon": "{% if is_state(entity, 'on') %}\n"
                "  mdi:floor-lamp\n"
                "{% else %}\n"
                "  mdi:floor-lamp-outline\n"
                "{% endif %}",
                "icon_color": "{% if is_state(entity, 'on') %}\n"
                "  amber\n"
                "{% endif %}",
                "tap_entity": "group.kitchen_light_group",
            },
        )

    def test_occupancy_override_status_card(self):
        def template_card(**kwargs):
            return kwargs

        self.assertEqual(
            dashboard_view_helpers.occupancy_override_status_card(
                "input_boolean.kitchen_auto_off_suspended",
                template_card,
            ),
            {
                "icon": "{% if is_state(entity, 'on') %}\n"
                "  mdi:timer-sand\n"
                "{% else %}\n"
                "  mdi:timer-sand-paused\n"
                "{% endif %}",
                "icon_color": "{% if is_state(entity, 'on') %}\n"
                "  yellow\n"
                "{% endif %}",
                "tap_entity": "input_boolean.kitchen_auto_off_suspended",
            },
        )

    def test_temperature_control_status_card(self):
        def template_card(**kwargs):
            return kwargs

        self.assertEqual(
            dashboard_view_helpers.temperature_control_status_card(
                "climate.kitchen",
                template_card,
            ),
            {
                "icon": "{% if is_state(entity, 'heat') %}\n"
                "  mdi:heating-coil\n"
                "    {% else %}   \n"
                "  mdi:snowflake\n"
                "      {% endif %}",
                "icon_color": "{% if is_state(entity, 'heat') %}\n"
                "  {% if state_attr(entity, 'temperature') > state_attr(entity, 'current_temperature') %}\n"
                "  red\n"
                " {% else %}\n"
                " blue\n"
                "  {% endif %}\n"
                " {% endif %}\n",
                "condition_state": "heat",
                "condition_entity": "climate.kitchen",
            },
        )

    def test_occupancy_status_card(self):
        def template_card(**kwargs):
            return kwargs

        self.assertEqual(
            dashboard_view_helpers.occupancy_status_card(
                "input_select.kitchen_occupancy",
                template_card,
            ),
            {
                "icon": "{% if   is_state(entity, 'Outside') %}\n"
                "  mdi:door-closed\n"
                "{% elif is_state(entity, 'Just Entered') %}\n"
                "  mdi:arrow-right-circle\n"
                "{% elif is_state(entity, 'In Sleep') %}\n"
                "  mdi:sleep\n"
                "{% else %}\n"
                "  mdi:account-multiple\n"
                "{% endif %}",
                "icon_color": "{% if   is_state(entity, 'Outside') %}                     "
                "{% elif is_state(entity, 'Just Entered') %}\n"
                "  green\n"
                "                 {% elif is_state(entity, 'In Sleep') %}\n"
                "  blue\n"
                "     {% else %}\n"
                "  purple\n"
                "              {% endif %}",
                "tap_entity": "input_select.kitchen_occupancy",
                "condition_state_not": "Outside",
                "condition_entity": "input_select.kitchen_occupancy",
            },
        )

    def test_curtain_status_card(self):
        def template_card(**kwargs):
            return kwargs

        self.assertEqual(
            dashboard_view_helpers.curtain_status_card(
                "cover.kitchen_curtain_group",
                template_card,
            ),
            {
                "icon": "{% if is_state(entity, 'open') %}\n"
                "  mdi:curtains\n"
                "{% else %}\n"
                "  mdi:curtains-closed\n"
                "{% endif %}",
                "icon_color": "{% if is_state(entity, 'open') %}\n"
                "  green       \n"
                "{% endif %}",
                "condition_state": "open",
                "condition_entity": "cover.kitchen_curtain_group",
            },
        )

    def test_navigation_status_cards_preserve_card_order(self):
        def template_card(**kwargs):
            return kwargs

        cards = dashboard_view_helpers.navigation_status_cards(
            "binary_sensor.unavailable",
            ["sensor.battery"],
            "binary_sensor.low_battery",
            "group.battery",
            ["binary_sensor.window"],
            "group.window",
            ["media_player.tv"],
            ["light.kitchen"],
            "group.light",
            True,
            "input_boolean.override",
            True,
            "climate.kitchen",
            True,
            "input_select.occupancy",
            ["cover.curtain"],
            "cover.curtain_group",
            template_card,
        )

        self.assertEqual(
            [
                card.get("condition_entity") or card.get("tap_entity")
                for card in cards
            ],
            [
                "binary_sensor.unavailable",
                "group.battery",
                "group.window",
                "media_player.tv",
                "group.light",
                "input_boolean.override",
                "climate.kitchen",
                "input_select.occupancy",
                "cover.curtain_group",
            ],
        )

    def test_navigation_status_cards_skip_disabled_optional_cards(self):
        def template_card(**kwargs):
            return kwargs

        cards = dashboard_view_helpers.navigation_status_cards(
            "binary_sensor.unavailable",
            [],
            "binary_sensor.low_battery",
            "group.battery",
            [],
            "group.window",
            [],
            [],
            "group.light",
            False,
            "input_boolean.override",
            False,
            "climate.kitchen",
            False,
            "input_select.occupancy",
            [],
            "cover.curtain_group",
            template_card,
        )

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["condition_entity"], "binary_sensor.unavailable")

    def test_navigation_status_stack_card(self):
        cards = [{"type": "entity"}]

        self.assertEqual(
            dashboard_view_helpers.navigation_status_stack_card(
                {"card_mod": {"style": "transparent"}},
                cards,
            ),
            {
                "card_mod": {"style": "transparent"},
                "type": "custom:stack-in-card",
                "mode": "horizontal",
                "cards": cards,
            },
        )

    def test_mushroom_navigation_room_card(self):
        title_card = {"type": "title"}
        status_stack_card = {"type": "status"}

        self.assertEqual(
            dashboard_view_helpers.mushroom_navigation_room_card(
                title_card,
                status_stack_card,
            ),
            {
                "type": "custom:stack-in-card",
                "mode": "vertical",
                "cards": [
                    title_card,
                    status_stack_card,
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
