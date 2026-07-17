import os
import sys
import unittest
from unittest.mock import patch


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import message_helpers


class MessageHelpersTest(unittest.TestCase):
    def test_raise_config_error_wraps_message(self):
        with self.assertRaises(TypeError) as ctx:
            message_helpers.raise_config_error("Bad config")

        self.assertIn("Bad config", str(ctx.exception))
        self.assertIn("###", str(ctx.exception))

    def test_warn_config_wraps_message(self):
        with self.assertWarns(Warning) as ctx:
            message_helpers.warn_config("Check this")

        self.assertIn("Check this", str(ctx.warning))

    def test_print_info(self):
        with patch("builtins.print") as mock_print:
            message_helpers.print_info("Generating")

        mock_print.assert_called_once_with("Generating")


if __name__ == "__main__":
    unittest.main()
