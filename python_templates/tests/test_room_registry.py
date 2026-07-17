import os
import sys
import unittest


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import room_registry


def make_room_class(name):
    return type(name, (), {"__init__": lambda self: None})


ROOM_CLASS_NAMES = [
    "LivingRoom",
    "Kitchen",
    "GuestRoom",
    "Study",
    "GuestToilet",
    "Garden",
    "Corridor",
    "EnSuiteToilet",
    "EnSuiteRoom",
    "GroundToilet",
    "MasterRoom",
    "MasterToilet",
    "WholeHome",
    "System",
]


class RoomRegistryTest(unittest.TestCase):
    def setUp(self):
        self.room_classes = {
            class_name: make_room_class(class_name)
            for class_name in ROOM_CLASS_NAMES
        }

    def test_package_room_order(self):
        rooms = room_registry.create_package_rooms(self.room_classes)

        self.assertEqual(
            [room.__class__.__name__ for room in rooms],
            [
                "LivingRoom",
                "Kitchen",
                "GuestRoom",
                "Study",
                "GuestToilet",
                "Garden",
                "Corridor",
                "EnSuiteToilet",
                "EnSuiteRoom",
                "GroundToilet",
                "MasterRoom",
                "MasterToilet",
                "WholeHome",
            ],
        )

    def test_dashboard_room_class_order(self):
        room_classes = room_registry.get_dashboard_room_classes(self.room_classes)

        self.assertEqual(
            [room_class.__name__ for room_class in room_classes],
            [
                "LivingRoom",
                "Kitchen",
                "MasterRoom",
                "MasterToilet",
                "Study",
                "System",
                "GuestRoom",
                "Corridor",
                "GuestToilet",
                "Garden",
                "EnSuiteRoom",
                "GroundToilet",
                "EnSuiteToilet",
            ],
        )


if __name__ == "__main__":
    unittest.main()
