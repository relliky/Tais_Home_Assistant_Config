import os
import sys
import tempfile
import unittest

import yaml


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import generator_io
import package_writer


class PackageWriterTest(unittest.TestCase):
    def test_write_room_package_writes_package_and_customize_yaml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            auto_dir = os.path.join(temp_dir, "packages", "_auto_generated_packages")
            packages_dir = os.path.join(temp_dir, "packages")

            result = package_writer.write_room_package(
                room_entity="test_room",
                entity_declarations={"sensor": [{"name": "Test"}]},
                customize_dict={"sensor.test": {"icon": "mdi:test"}},
                script_dir=temp_dir,
                auto_generated_packages_dir=auto_dir,
                packages_dir=packages_dir,
                write_yaml_file=generator_io.write_yaml_file,
            )

            package_path = os.path.join(auto_dir, "auto_gen_test_room.yaml")
            customize_path = os.path.join(packages_dir, "auto_gen_customize_test_room.yaml")

            self.assertEqual(result["package_config_path"], package_path)
            self.assertEqual(result["auto_gen_config_path"], customize_path)
            self.assertEqual(result["customize_declaration"], {"homeassistant": {"customize": {"sensor.test": {"icon": "mdi:test"}}}})

            with open(package_path, encoding="utf-8") as package_file:
                package_content = package_file.read()
            with open(customize_path, encoding="utf-8") as customize_file:
                customize_content = customize_file.read()

            self.assertIn("DO NOT MODIFY", package_content)
            self.assertEqual(yaml.safe_load(package_content), {"sensor": [{"name": "Test"}]})
            self.assertEqual(
                yaml.safe_load(customize_content),
                {"homeassistant": {"customize": {"sensor.test": {"icon": "mdi:test"}}}},
            )


if __name__ == "__main__":
    unittest.main()
