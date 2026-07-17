import os
import sys
import unittest
from unittest.mock import patch


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import gen_config_yaml


class CliOrchestrationTest(unittest.TestCase):
    def test_dashboard_only_command_skips_packages_and_registry(self):
        parsed_args = gen_config_yaml.parse_args(["-C", "-dy", "-R"])

        self.assertFalse(parsed_args.render_auto_config)
        self.assertFalse(parsed_args.check_auto_system_config)
        self.assertTrue(parsed_args.render_dashboard_yaml)
        self.assertEqual(gen_config_yaml.get_dashboard_type(parsed_args), "default")

        with patch.object(gen_config_yaml, "render_package_configs") as render_packages, \
             patch.object(gen_config_yaml, "check_entity_registry_config") as check_registry, \
             patch.object(gen_config_yaml, "create_clean_entity_registry_config") as create_clean_registry, \
             patch.object(gen_config_yaml, "render_dashboard_config") as render_dashboard:
            gen_config_yaml.run(parsed_args)

        render_packages.assert_not_called()
        check_registry.assert_not_called()
        create_clean_registry.assert_not_called()
        render_dashboard.assert_called_once_with(parsed_args)

    def test_dashboard_type_flags(self):
        self.assertEqual(
            gen_config_yaml.get_dashboard_type(gen_config_yaml.parse_args(["-dy"])),
            "default",
        )
        self.assertEqual(
            gen_config_yaml.get_dashboard_type(gen_config_yaml.parse_args(["-dy", "-dm"])),
            "mobile",
        )
        self.assertEqual(
            gen_config_yaml.get_dashboard_type(gen_config_yaml.parse_args(["-dy", "-dt"])),
            "tablet",
        )


if __name__ == "__main__":
    unittest.main()
