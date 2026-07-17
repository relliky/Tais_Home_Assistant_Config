import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import dashboard_restrictions


class DashboardRestrictionsTest(unittest.TestCase):
    def test_restricted_access_card_wraps_inner_card(self):
        inner_card = {"type": "button", "name": "Room"}

        card = dashboard_restrictions.restricted_access_card("us", inner_card)

        self.assertEqual(card["type"], "custom:restriction-card")
        self.assertIs(card["card"], inner_card)
        self.assertEqual(
            card["restrictions"]["hide"]["exemptions"],
            dashboard_restrictions.EXEMPTION_USERS,
        )

    def test_unsupported_user_raises(self):
        with self.assertRaises(TypeError):
            dashboard_restrictions.restricted_access_card("unknown", {})


if __name__ == "__main__":
    unittest.main()
