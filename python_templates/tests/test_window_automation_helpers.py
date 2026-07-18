import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import window_automation_helpers


class WindowAutomationHelpersTest(unittest.TestCase):
    def test_window_is_open_condition(self):
        self.assertEqual(
            window_automation_helpers.window_is_open_condition("group.kitchen_window_group"),
            {
                "condition": "state",
                "entity_id": "group.kitchen_window_group",
                "state": "on",
            },
        )

    def test_notify_windows_open_action(self):
        self.assertEqual(
            window_automation_helpers.notify_windows_open_action(
                "Kitchen windows are open",
                notify_tai="yes",
                notify_ke="yes",
            ),
            {
                "service": "script.notify_alexa_speakers_and_phones",
                "data": {
                    "tts_message": "Kitchen windows are open",
                    "notify_tai": "yes",
                    "notify_ke": "yes",
                },
            },
        )

    def test_tenant_notify_flags_for_kitchen(self):
        self.assertEqual(
            window_automation_helpers.tenant_notify_flags_for_room("kitchen"),
            {
                "notify_guest_room_tenant": "yes",
                "notify_en_suite_room_tenant": "yes",
            },
        )

    def test_tenant_notify_flags_for_other_room(self):
        self.assertEqual(
            window_automation_helpers.tenant_notify_flags_for_room("master_room"),
            {},
        )


if __name__ == "__main__":
    unittest.main()
