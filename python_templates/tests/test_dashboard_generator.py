import os
import sys
import contextlib
import io
import tempfile
import unittest

import yaml


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import dashboard_generator


class FakeRoomBase:
    def getLayoutWrapperCardList(self, cards=None):
        return [{"type": "grid", "cards": cards}]

    def addView(self, viewPath="", theme=None, cards=None):
        self.views += [{"path": viewPath, "theme": theme, "cards": cards}]


class FakeRoom:
    def __init__(self, dashboard_type=None, dashboard_language=None):
        self.dashboard_type = dashboard_type
        self.dashboard_language = dashboard_language

    def getNavigationRoomCard(self):
        return {"type": "button", "name": "Fake Room"}

    def getRoomViews(self):
        return [{"path": "fake-room", "cards": []}]


def write_yaml_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as yaml_file:
        yaml.safe_dump(data, yaml_file, sort_keys=False)


def write_json_file(path, data):
    raise AssertionError("JSON writer should not be called for YAML dashboard")


class DashboardGeneratorTest(unittest.TestCase):
    def test_render_dashboard_writes_yaml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with contextlib.redirect_stdout(io.StringIO()):
                dashboard = dashboard_generator.render_dashboard(
                    format="yaml",
                    dashboard_type="mobile",
                    dashboard_language="English",
                    room_base_class=FakeRoomBase,
                    room_classes=[FakeRoom],
                    dashboard_output_dir=temp_dir,
                    storage_dir=temp_dir,
                    write_yaml_file=write_yaml_file,
                    write_json_file=write_json_file,
                )

            output_path = os.path.join(temp_dir, "auto_gen_overall_dashboard.yaml")
            with open(output_path, encoding="utf-8") as yaml_file:
                dashboard_yaml = yaml.safe_load(yaml_file)

            self.assertEqual(dashboard.dashboard_type, "mobile")
            self.assertEqual(dashboard_yaml["views"][0]["path"], "home")
            self.assertEqual(dashboard_yaml["views"][1]["path"], "fake-room")


if __name__ == "__main__":
    unittest.main()
