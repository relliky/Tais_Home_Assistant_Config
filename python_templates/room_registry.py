def create_package_rooms(room_classes):
  return [
    room_classes["LivingRoom"](),
    room_classes["Kitchen"](),
    room_classes["GuestRoom"](),
    room_classes["Study"](),
    room_classes["GuestToilet"](),
    room_classes["Garden"](),
    room_classes["Corridor"](),
    room_classes["EnSuiteToilet"](),
    room_classes["EnSuiteRoom"](),
    room_classes["GroundToilet"](),
    room_classes["MasterRoom"](),
    room_classes["MasterToilet"](),
    room_classes["WholeHome"]()
  ]


def get_dashboard_room_classes(room_classes):
  return [
    room_classes["LivingRoom"],
    room_classes["Kitchen"],
    room_classes["MasterRoom"],
    room_classes["MasterToilet"],
    room_classes["Study"],
    room_classes["System"],
    room_classes["GuestRoom"],
    room_classes["Corridor"],
    room_classes["GuestToilet"],
    room_classes["Garden"],
    room_classes["EnSuiteRoom"],
    room_classes["GroundToilet"],
    room_classes["EnSuiteToilet"],
  ]
