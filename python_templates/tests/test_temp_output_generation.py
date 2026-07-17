from pathlib import Path
import copy
import contextlib
import io
import random
import tempfile
import unittest

import yaml


SCRIPT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SCRIPT_DIR.parent
BASELINE_DIR = SCRIPT_DIR / "tests" / "baseline_generated"

import sys

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import gen_config_yaml


GENERATED_GROUPS = {
    "packages_auto": Path("packages") / "_auto_generated_packages",
    "packages_customize": Path("packages"),
}


def load_yaml(path):
    with path.open("r", encoding="utf-8") as yaml_file:
        return yaml.safe_load(yaml_file)


def normalize_generated_yaml(value):
    value = copy.deepcopy(value)

    def normalize(node):
        if isinstance(node, dict):
            if node.get("trigger") == "time_pattern" and "seconds" in node:
                node["seconds"] = "__random_second__"
            for child in node.values():
                normalize(child)
        elif isinstance(node, list):
            for child in node:
                normalize(child)

    normalize(value)
    return value


class TempOutputGenerationTest(unittest.TestCase):
    def test_generator_can_write_all_outputs_to_temp_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                gen_config_yaml.configure_output_root(temp_dir)
                random.seed(0)
                with contextlib.redirect_stdout(io.StringIO()):
                    gen_config_yaml.create_package_rooms()
                    gen_config_yaml.Dashboard(
                        format="yaml",
                        dashboard_type="mobile",
                        dashboard_language="English",
                    )

                for group_name, generated_subdir in GENERATED_GROUPS.items():
                    baseline_dir = BASELINE_DIR / group_name
                    generated_dir = Path(temp_dir) / generated_subdir
                    baseline_files = sorted(path.name for path in baseline_dir.glob("*.yaml"))
                    generated_files = sorted(path.name for path in generated_dir.glob("auto_gen*.yaml"))

                    with self.subTest(group=group_name, check="file_set"):
                        self.assertEqual(generated_files, baseline_files)

                    for file_name in baseline_files:
                        with self.subTest(group=group_name, file=file_name):
                            self.assertEqual(
                                normalize_generated_yaml(load_yaml(generated_dir / file_name)),
                                normalize_generated_yaml(load_yaml(baseline_dir / file_name)),
                            )

                dashboard_path = Path(temp_dir) / "python_templates" / "auto_gen_overall_dashboard.yaml"
                dashboard_yaml = load_yaml(dashboard_path)
                self.assertIn("views", dashboard_yaml)
            finally:
                gen_config_yaml.configure_output_root(None)


if __name__ == "__main__":
    unittest.main()
