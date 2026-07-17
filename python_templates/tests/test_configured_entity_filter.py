import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import configured_entity_filter


class ConfiguredEntityFilterTest(unittest.TestCase):
    def test_filters_list_and_removes_configured_key(self):
        declarations = {
            "sensor": [
                {"name": "Keep", "configured": True},
                {"name": "Drop", "configured": False},
            ]
        }

        filtered = configured_entity_filter.remove_disabled_entities(declarations)

        self.assertEqual(filtered, {"sensor": [{"name": "Keep"}]})
        self.assertNotIn("configured", filtered["sensor"][0])

    def test_filters_dict_and_removes_configured_key(self):
        declarations = {
            "input_boolean": {
                "keep": {"name": "Keep", "configured": True},
                "drop": {"name": "Drop", "configured": False},
            }
        }

        filtered = configured_entity_filter.remove_disabled_entities(declarations)

        self.assertEqual(filtered, {"input_boolean": {"keep": {"name": "Keep"}}})
        self.assertNotIn("configured", filtered["input_boolean"]["keep"])

    def test_unsupported_category_type_raises(self):
        with self.assertRaises(TypeError):
            configured_entity_filter.remove_disabled_entities({"bad": "not-list-or-dict"})


if __name__ == "__main__":
    unittest.main()
