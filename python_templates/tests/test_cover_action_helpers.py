import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import cover_action_helpers


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


if __name__ == "__main__":
    unittest.main()
