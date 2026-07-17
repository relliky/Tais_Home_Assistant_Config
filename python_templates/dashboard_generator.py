import os


def create_dashboard_rooms(room_classes, dashboard_type=None, dashboard_language=None):
  return [
    room_class(dashboard_type=dashboard_type, dashboard_language=dashboard_language)
    for room_class in room_classes
  ]


def render_dashboard(format=None,
                     dashboard_type=None,
                     dashboard_language=None,
                     room_base_class=None,
                     room_classes=None,
                     dashboard_output_dir=None,
                     storage_dir=None,
                     write_yaml_file=None,
                     write_json_file=None):
  class Dashboard(room_base_class):
    def __init__ (self, format=None, dashboard_type=None, dashboard_language=None):
      print ("-------------------------------------")
      print ("** Generating Overall Lovelace Configs. **")
      self.format             = 'yaml'   if format         == None else format
      self.dashboard_type     = 'mobile' if dashboard_type == None else dashboard_type
      self.room_nav_cards = []
      self.dashboard = {}
      self.views = []
      self.rooms = create_dashboard_rooms(room_classes, dashboard_type=dashboard_type, dashboard_language=dashboard_language)
      self.addNavigationView()
      self.addAllRoomView()
      self.getDashbaord()
      self.writeConfig()
      print ("-------------------------------------")

    def addNavigationView(self):
      for room in self.rooms:
        self.room_nav_cards += [room.getNavigationRoomCard()]

      room_nav_grid_cards = self.getLayoutWrapperCardList(self.room_nav_cards)

      self.addView(viewPath='home', theme='Mushroom Shadow', cards=room_nav_grid_cards)

    def addAllRoomView(self):
        for room in self.rooms:
          self.views += room.getRoomViews()

    def getDashbaord(self):
      if self.format == 'json':
        self.dashboard = {
                            "version": 1,
                            "minor_version": 1,
                            "key": "lovelace.dashboard_mobile",
                            "data": {
                              "config": {
                                "background": "var(--background-image)",
                                "views": self.views
                              }
                            }
                          }
      else: # yaml
        self.dashboard = {"background": "var(--background-image)",
                          "views": self.views
                          }

    def writeConfig(self):
      if self.format == 'yaml':
        self.auto_gen_config_path = os.path.join(dashboard_output_dir, "auto_gen_overall_dashboard.yaml")
      else: # json
        # this does not work. have to use GUI to copy the yaml dashboard
        self.auto_gen_config_path = os.path.join(storage_dir, "lovelace.dashboard_mobile")

      if self.format == 'yaml':
        write_yaml_file(self.auto_gen_config_path, self.dashboard)
      else: # json
        write_json_file(self.auto_gen_config_path, self.dashboard)

  return Dashboard(format=format, dashboard_type=dashboard_type, dashboard_language=dashboard_language)
