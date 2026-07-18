import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import cover_action_helpers


def set_service(entity_id, state):
    return ["set", entity_id, state]


class CoverActionHelpersTest(unittest.TestCase):
    def test_cover_position_step_action(self):
        self.assertEqual(
            cover_action_helpers.cover_position_step_action(
                ["cover.kitchen_curtain"],
                34,
            ),
            {
                "service": "cover.set_cover_position",
                "target": {"entity_id": ["cover.kitchen_curtain"]},
                "data": {
                    "position": "{{ [[ (state_attr('cover.kitchen_curtain', 'current_position')) + 34 ,0]|max,100]|min}}"
                },
            },
        )

    def test_shutter_blind_position_action(self):
        self.assertEqual(
            cover_action_helpers.shutter_blind_position_action(
                ["cover.study_blind"],
                95,
                100,
            ),
            {
                "if": {
                    "condition": "numeric_state",
                    "entity_id": ["cover.study_blind"],
                    "attribute": "current_position",
                    "above": 95,
                },
                "then": {
                    "service": "cover.set_cover_position",
                    "data": {"position": 100},
                    "entity_id": ["cover.study_blind"],
                },
            },
        )

    def test_cover_open_if_closed_action(self):
        self.assertEqual(
            cover_action_helpers.cover_open_if_closed_action(
                ["cover.kitchen_curtain"],
                ["cover.kitchen_curtain"],
            ),
            {
                "if": {
                    "condition": "numeric_state",
                    "entity_id": ["cover.kitchen_curtain"],
                    "attribute": "current_position",
                    "below": 5,
                },
                "then": {
                    "service": "cover.open_cover",
                    "entity_id": ["cover.kitchen_curtain"],
                },
            },
        )

    def test_cover_close_if_open_action(self):
        self.assertEqual(
            cover_action_helpers.cover_close_if_open_action(
                ["cover.kitchen_curtain"],
                ["cover.kitchen_curtain"],
            ),
            {
                "if": {
                    "condition": "numeric_state",
                    "entity_id": ["cover.kitchen_curtain"],
                    "attribute": "current_position",
                    "above": 95,
                },
                "then": {
                    "service": "cover.close_cover",
                    "entity_id": ["cover.kitchen_curtain"],
                },
            },
        )

    def test_cover_toggle_action(self):
        self.assertEqual(
            cover_action_helpers.cover_toggle_action(
                ["cover.kitchen_curtain"],
                set_service,
            ),
            {
                "if": [
                    {
                        "alias": "toggle all curtains together: if any of curtains is on, turn off all curtains, otherwise turn on all curtains",
                        "condition": "state",
                        "entity_id": ["cover.kitchen_curtain"],
                        "state": ["open", "opening"],
                        "match": "any",
                    }
                ],
                "then": ["set", ["cover.kitchen_curtain"], "off"],
                "else": ["set", ["cover.kitchen_curtain"], "on"],
            },
        )

    def test_stop_cover_before_action(self):
        self.assertEqual(
            cover_action_helpers.stop_cover_before_action(
                ["cover.kitchen_curtain"],
                {"service": "cover.open_cover"},
            ),
            [
                {
                    "service": "cover.stop_cover",
                    "entity_id": ["cover.kitchen_curtain"],
                },
                {"service": "cover.open_cover"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
