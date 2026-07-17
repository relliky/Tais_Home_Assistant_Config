import os
import sys
import tempfile
import unittest

import yaml


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import generator_io


class GeneratorIoTest(unittest.TestCase):
    def tearDown(self):
        generator_io.configure_output_root(None)

    def test_configure_output_root_updates_generated_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            generator_io.configure_output_root(temp_dir)

            self.assertEqual(generator_io.PACKAGES_DIR, os.path.join(temp_dir, "packages"))
            self.assertEqual(
                generator_io.AUTO_GENERATED_PACKAGES_DIR,
                os.path.join(temp_dir, "packages", "_auto_generated_packages"),
            )
            self.assertEqual(generator_io.STORAGE_DIR, os.path.join(temp_dir, ".storage"))
            self.assertEqual(
                generator_io.DASHBOARD_OUTPUT_DIR,
                os.path.join(temp_dir, "python_templates"),
            )

    def test_write_yaml_file_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "nested", "auto_gen_test.yaml")

            generator_io.write_yaml_file(output_path, {"sensor": [{"name": "Test"}]}, include_header=True)

            with open(output_path, encoding="utf-8") as yaml_file:
                content = yaml_file.read()

            self.assertIn("DO NOT MODIFY", content)
            self.assertEqual(yaml.safe_load(content), {"sensor": [{"name": "Test"}]})

    def test_write_json_file_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "nested", "config.json")

            generator_io.write_json_file(output_path, {"ok": True})

            self.assertTrue(os.path.exists(output_path))


if __name__ == "__main__":
    unittest.main()
