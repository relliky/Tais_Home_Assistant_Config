import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import generator_cli


class GeneratorCliTest(unittest.TestCase):
    def test_dashboard_only_command_flags(self):
        args = generator_cli.parse_args(["-C", "-dy", "-R"])

        self.assertFalse(args.render_auto_config)
        self.assertFalse(args.check_auto_system_config)
        self.assertTrue(args.render_dashboard_yaml)
        self.assertEqual(generator_cli.get_dashboard_type(args), "default")
        self.assertEqual(generator_cli.get_dashboard_language(args), "English")

    def test_dashboard_type_and_language_flags(self):
        tablet_chinese = generator_cli.parse_args(["-dy", "-dt", "-lc"])
        mobile = generator_cli.parse_args(["-dy", "-dm"])

        self.assertEqual(generator_cli.get_dashboard_type(tablet_chinese), "tablet")
        self.assertEqual(generator_cli.get_dashboard_language(tablet_chinese), "Chinese")
        self.assertEqual(generator_cli.get_dashboard_type(mobile), "mobile")


if __name__ == "__main__":
    unittest.main()
