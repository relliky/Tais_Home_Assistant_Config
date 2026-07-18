import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import condition_helpers


class ConditionHelpersTest(unittest.TestCase):
    def test_numeric_state_or_unavailable(self):
        self.assertEqual(
            condition_helpers.numeric_state_or_unavailable(
                "sensor.kitchen_light",
                "above",
                100,
            ),
            {
                "condition": "or",
                "conditions": [
                    {
                        "condition": "numeric_state",
                        "entity_id": "sensor.kitchen_light",
                        "above": 100,
                    },
                    {
                        "condition": "state",
                        "entity_id": "sensor.kitchen_light",
                        "state": [
                            "unavailable",
                            "unknown",
                        ],
                    },
                ],
            },
        )

    def test_sun_state_or_unavailable(self):
        self.assertEqual(
            condition_helpers.sun_state_or_unavailable("above_horizon"),
            {
                "condition": "or",
                "conditions": [
                    {
                        "condition": "state",
                        "entity_id": "sun.sun",
                        "state": "above_horizon",
                    },
                    {
                        "condition": "state",
                        "entity_id": "sun.sun",
                        "state": [
                            "unavailable",
                            "unknown",
                        ],
                    },
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
