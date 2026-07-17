import json
import os
import sys
import tempfile
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import ha_entity_registry


class HaEntityRegistryTest(unittest.TestCase):
    def write_registry(self, storage_dir, entity_ids):
        os.makedirs(storage_dir, exist_ok=True)
        registry = {
            "data": {
                "entities": [
                    {"entity_id": entity_id, "platform": "test"}
                    for entity_id in entity_ids
                ]
            }
        }
        with open(os.path.join(storage_dir, "core.entity_registry"), "w", encoding="utf-8") as registry_file:
            json.dump(registry, registry_file)

    def test_finds_unexpected_duplicate_entities(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.write_registry(
                temp_dir,
                [
                    "automation.zl_living_room_light",
                    "automation.zl_living_room_light_2",
                    "sensor.temperature_2",
                    "light.kitchen",
                ],
            )

            ha_entity_registry.read_core_entity_entries_json(temp_dir)

            self.assertEqual(
                ha_entity_registry.find_unexpected_entities(check_all_suffix_duplicates=True),
                ["automation.zl_living_room_light_2", "sensor.temperature_2"],
            )
            self.assertEqual(
                ha_entity_registry.find_unexpected_entities(check_all_suffix_duplicates=False),
                ["automation.zl_living_room_light_2"],
            )

    def test_removes_auto_generated_automation_entities(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.write_registry(
                temp_dir,
                [
                    "automation.zl_living_room_light",
                    "automation.manual_scene",
                    "sensor.temperature",
                ],
            )

            ha_entity_registry.read_core_entity_entries_json(temp_dir)
            cleaned_registry = ha_entity_registry.remove_auto_generated_automation_entities()

            self.assertEqual(
                [entity["entity_id"] for entity in cleaned_registry["data"]["entities"]],
                ["automation.manual_scene", "sensor.temperature"],
            )

    def test_writes_cleaned_registry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = os.path.join(temp_dir, "storage")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            self.write_registry(storage_dir, ["automation.z_auto", "sensor.keep"])

            ha_entity_registry.read_core_entity_entries_json(storage_dir)
            ha_entity_registry.remove_auto_generated_automation_entities()
            output_path = ha_entity_registry.write_core_entity_entries_json(output_dir)

            with open(output_path, encoding="utf-8") as registry_file:
                written_registry = json.load(registry_file)

            self.assertEqual(
                [entity["entity_id"] for entity in written_registry["data"]["entities"]],
                ["sensor.keep"],
            )


if __name__ == "__main__":
    unittest.main()
