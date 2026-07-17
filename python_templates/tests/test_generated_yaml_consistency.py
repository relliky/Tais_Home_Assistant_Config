from pathlib import Path
import unittest

import yaml


SCRIPT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SCRIPT_DIR.parent
BASELINE_DIR = SCRIPT_DIR / "tests" / "baseline_generated"


GENERATED_GROUPS = {
    "packages_auto": REPO_ROOT / "packages" / "_auto_generated_packages",
    "packages_customize": REPO_ROOT / "packages",
    "dashboard": SCRIPT_DIR,
}


def load_yaml(path):
    with path.open("r", encoding="utf-8") as yaml_file:
        return yaml.safe_load(yaml_file)


class GeneratedYamlConsistencyTest(unittest.TestCase):
    def test_generated_yaml_matches_baseline_structure(self):
        for group_name, generated_dir in GENERATED_GROUPS.items():
            baseline_dir = BASELINE_DIR / group_name
            baseline_files = sorted(path.name for path in baseline_dir.glob("*.yaml"))
            generated_files = sorted(path.name for path in generated_dir.glob("auto_gen*.yaml"))

            with self.subTest(group=group_name, check="file_set"):
                self.assertEqual(generated_files, baseline_files)

            for file_name in baseline_files:
                with self.subTest(group=group_name, file=file_name):
                    self.assertEqual(
                        load_yaml(generated_dir / file_name),
                        load_yaml(baseline_dir / file_name),
                    )


if __name__ == "__main__":
    unittest.main()
