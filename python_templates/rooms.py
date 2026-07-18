from copy import deepcopy
import dashboard_view_helpers


def define_room_classes(RoomBase):
  class MasterRoom(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'Master Room'
      self.room_short_name       = 'MR'
      self.num_of_xiaomi_button  = 3
      self.num_of_lamps          = 2
      # Enables
      self.cfg_scene              = True
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      self.cfg_scene_color_led    = True
      self.cfg_scene_color_lamp   = True
      self.cfg_custom_scene       = True
      self.cfg_motion_bed_led     = True
      self.cfg_auto_curtain_ctl   = True
      self.cfg_adaptive_lighting  = True
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
      self.add_device("582d34376b04",                      self.room_name,                          'Temperature Sensor', "Qingping Temperature Sensor", postfix='new_1')
      self.add_device("582d343b6a27",                      self.room_name,                          'Temperature Sensor', "Qingping Temperature Sensor", postfix='new_2')
      # self.add_device("a4c1381d6ddb",                     self.room_name,                     'Temperature Sensor', "Mijia2 Temperature Sensor")
  
      self.add_average_temperature_sensor(    sensor_1=  'sensor.master_room_temperature_sensor_new_1',
                                              sensor_2=  'sensor.master_room_temperature_sensor_new_2',
                                              sensor_out='sensor.master_room_average_temperature_sensor')
      self.add_smooth_temperature_sensor(     sensor_in= 'sensor.master_room_average_temperature_sensor',
                                              sensor_out='sensor.master_room_temperature_sensor', )
  
      self.add_device("a4c1383dc01d",                      self.room_name + ' Corridor',             'Motion Sensor',      "Linptech Occupancy Sensor ES3")
      self.add_device("linp_cn_blt_3_1k8ac64fskc00_es2",   self.room_name + ' Corridor Xiaomi Home', 'Motion Sensor',      "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      self.add_device("linp_cn_blt_3_1onitceoh0000_es5b",  self.room_name + ' Bed Xiaomi Home',  'Motion Sensor',      "Linptech Occupancy Sensor ES5", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
  
  
      self.add_device("0x00158d0005228ba8",                self.room_name + " TV",                  'Motion Sensor',      "Aqara Motion and Illuminance Sensor")
      self.add_device("0x00158d000122393b",                self.room_name + " Entrance",            'Motion Sensor',      "Aqara Motion and Illuminance Sensor")
      self.add_device("0x00158d00054deda4",                self.room_name + " Stair",               'Motion Sensor',      "Aqara Motion and Illuminance Sensor")
      self.add_device("0x00158d00054a6f3a",                self.room_name + " Drawer",              'Motion Sensor',      "Aqara Motion and Illuminance Sensor")
      #self.add_device('50ec50df3056',                      self.room_name + " Bed Ceiling Light",   'Light',              'Mijia BLE Lights')
      self.add_device("yeelight_ceiling13_0x1c649afe", self.room_name + " Bed Ceiling Light",'Light',        "Generic Light") # Yeelight
      #self.add_device("yeelink_ceiling13_40f4_light", self.room_name + " Bed Ceiling Light",'Light',        "Generic Light") # MiIOT Auto
  
      #self.add_device("master_room_drawer_ceiling_light_xiaomi",self.room_name + " Drawer Ceiling Light",'Light',        "Generic Light") # MiIOT Auto
      self.add_device("yeelink_cn_442976373_ceiling13_s_2_light",self.room_name + " Drawer Ceiling Light",'Light',        "Generic Light") # Xiaomi Home
  
      self.add_device("hue_color_lamp_5",                  self.room_name + " Lamp 1",              'Light',              "Generic Light")
      self.add_device("hue_color_lamp_6",                  self.room_name + " Lamp 2",              'Light',              "Generic Light")
      #self.add_device("master_room_bed_led_magic_home",    self.room_name + " Bed LED",             'Light',              "Generic Light")
      self.add_device("master_room_tv_led_magic_home",     self.room_name + " TV LED",              'Light',              "Generic Light")
      #self.add_device("master_room_drawer_led_magic_home", self.room_name + " Drawer LED",          'Light',              "Generic Light")
      self.add_device("0x04cf8cdf3c73a19b",                self.room_name + " Curtain",             'Curtain',            "Aqara B1 curtain motor", mdi_icon='curtains-closed')
      self.add_device("0x04cf8cdf3c7ad638",                self.room_name,                          'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Triple Rocker)", flex_switch=[2,3])
      self.add_device("0x04cf8cdf3c7ad638_channel_1",      self.room_name + ' Balcony Wall Light',  'Wall Switch',        "Generic Switch")
      self.add_device("0x00158d00052e2124",                self.room_name + ' Entrance',            'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Single Rocker)")
      self.add_device("hue_ambiance_lamp_2",               self.room_name + " Entrance Light",      'Light',              "Generic Light")
  
      #self.add_device('sonoff_1001e49ec4_1',               self.room_name + ' Dressing Table Light','Switch',             'Generic Switch')
      #self.add_device("sonoff_1001e4a0a0_1",               self.room_name + ' Gateway Power',       'Switch',             "Generic Switch")
      self.add_device('0x04cf8cdf3c7b36b1',                 self.room_name + ' West Side',           'Light Sensor',       'Xiaomi Light Detection Sensor')
      self.add_device('0x04cf8cdf3c7b36b1_illuminance',     self.room_name ,                         'Light Sensor',       'Generic Light Intensity')
  
      self.add_device('va0932385792',                      self.room_name,                          'Raditor',            'Tado Homekit')
  
      self.add_device('remote_control_4bc8',               self.room_name +' 6 Key',                'Button', 'Yeelight 6 Key Remote')
  
      # Smart Bed
      self.add_device("giot_cn_2079716287_v84ksm_on_p_2_1",       'Alpha Zero G Mode',       'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079716287_v84ksm_on_p_3_1",       'Alpha TV Mode',           'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079716287_v84ksm_on_p_4_1",       'Alpha Reading Mode',      'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079716287_v84ksm_on_p_10_1",      'Alpha Sleep Mode',        'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079460410_v84ksm_on_p_2_1",       'Alpha Head Up',           'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079460410_v84ksm_on_p_3_1",       'Alpha Foot Up',           'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079460410_v84ksm_on_p_4_1",       'Alpha Head Down',         'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079460410_v84ksm_on_p_10_1",      'Alpha Foot Down',         'Switch',             "Generic Switch")
  
      self.add_device("giot_cn_2079504293_v84ksm_on_p_2_1",       'Beta Zero G Mode',        'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079504293_v84ksm_on_p_3_1",       'Beta TV Mode',            'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079504293_v84ksm_on_p_4_1",       'Beta Reading Mode',       'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079504293_v84ksm_on_p_10_1",      'Beta Sleep Mode',         'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079484894_v84ksm_on_p_2_1",       'Beta Head Up',            'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079484894_v84ksm_on_p_3_1",       'Beta Foot Up',            'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079484894_v84ksm_on_p_4_1",       'Beta Head Down',          'Switch',             "Generic Switch")
      self.add_device("giot_cn_2079484894_v84ksm_on_p_10_1",      'Beta Foot Down',          'Switch',             "Generic Switch")
  
      # New unused
      #self.add_device('18c23c24681a',                      self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='1')
      #self.add_device('18c23c25a26c',                      self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='1')
      #self.add_device('18c23c25960b',                      self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='2')
      #self.add_device('0x54ef441000792d09',                self.room_name + ' Bed',                 'Pressure Sensor',    'Aqara Pressure Sensor')
      #self.add_device('e4aaec755efa',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='1')
      #self.add_device('e4aaec755cbc',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='2')
      #self.add_device('e4aaec755ef9',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='3')
      #self.add_device("dced830908fb",                      self.room_name,                          'Motion Sensor',      "Ziqing Occupancy Sensor")
      #self.add_device('e0798dba988e',                      self.room_name + ' Bed',                 'Motion Sensor',      'Mijia Motion Sensor 2')
      #self.add_device('18c23c25a26c',              self.room_name,                                  'Button',             'MiJia Wireless Switch 2', postfix='3')
      #self.add_device('50ec50df0a79',             'Master Room Ceiling Light Bulb 2',               'Light',              'Mijia BLE Lights')
      #self.add_device("54ef44e58958",             self.room_name + " Bed",                          'Motion Sensor',      "Mijia Motion Sensor 2")
      #self.add_device("lumi_hagl04_a19b_curtain", self.room_name + " Curtain",                      'Curtain',            "Generic Curtain")
      #self.add_device('mss210_d3bd_outlet',       self.room_name + ' Dressing Table Light',         'Switch',             'Generic Switch')
  
      # Z2M
      #('0x00158d00054a6f3a', 'Master Room Drawer',         'Aqara Motion and Illuminance Sensor')
      #('0x00158d00054deda4', 'Master Room Stair',          'Aqara Motion and Illuminance Sensor')
      #('0x00158d000122393b', 'Master Room Entrance',       'Motion Sensor')
      #('0x00158d000171bd29', 'Master Room Dressing Table', 'Motion Sensor')
      #('0x00158d00052e2124', 'Master Room Entrance',       'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
      #('0x04cf8cdf3c7b36b1', 'Master Room',                'Light Meter')
      #('0x00158d00053e95f6', 'Master Room Balcony',        'Aqara Door & Window Sensor')
      #('0x00158d00012262a5', 'Master Room 1'               'MiJia Wireless Switch')
      #('0x00158d000424f98c', 'Master Room 2'               'MiJia Wireless Switch')
  
    def get_window_entities(self):
      super().get_window_entities()
      self.windows                 = ["binary_sensor.master_room_balcony_door"]
      self.timeout_windows         = []
  
    # Remove wall switch single automation
    def gen_wall_button_single_automations(self):
      pass
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.non_bed_motion_sensors = [
        "binary_sensor.master_room_entrance_motion_sensor_motion",
        "binary_sensor.master_room_stair_motion_sensor_motion",
        "binary_sensor.master_room_dressing_table_motion_sensor_motion",
        "binary_sensor.master_room_tv_motion_sensor_motion",
        "binary_sensor.master_room_drawer_motion_sensor_motion",
        "binary_sensor.master_toilet_dressing_room_motion_sensor_motion"
      ]
  
      self.bed_motion_sensors = [
        #"binary_sensor.master_room_bed_pressure_sensor_1",
        #"binary_sensor.master_room_bed_pressure_sensor_2",
        #"binary_sensor.master_room_bed_pressure_sensor_3",
        #"binary_sensor.master_room_bed_pressure_sensor",
        #"binary_sensor.master_room_occupancy_sensor_occupancy",
        #"binary_sensor.master_room_drawer_occupancy_sensor_occupancy"
      ] + ([f"binary_sensor.{self.room_entity }_bed_xiaomi_home_occupancy_sensor_occupancy"]          if self.xiaomi_home_occupancy else []) \
        + ([f"binary_sensor.{self.room_entity }_bed_occupancy_sensor_occupancy"]                      if self.gateway_occupancy     else []) \
        + ([f"binary_sensor.{self.room_entity }_corridor_occupancy_sensor_occupancy"]                 if self.gateway_occupancy     else []) \
        + ([f"binary_sensor.{self.room_entity }_corridor_xiaomi_home_occupancy_sensor_occupancy"]     if self.xiaomi_home_occupancy else []) \
  
  
      self.toilet_motion_sensors = [
        "group.master_toilet_motion_group"
      ]
  
      self.all_motion_sensors = self.non_bed_motion_sensors + self.bed_motion_sensors + self.toilet_motion_sensors
  
      self.inside_to_outside_timeout = 2*60
      self.sleep_to_outside_timeout  = 5*60
      self.inside_to_sleep_timeout   = 5*60
  
    def get_light_entities(self):
      super().get_light_entities()
      # Light/Switch entities
      self.lamps                   = ["light.master_room_lamp_1",
                                      "light.master_room_lamp_2",
                                     ]
      self.add_group('light', self.room_name + ' Lamp', self.lamps)
  
      self.leds                    = ["light.master_room_tv_led",
                                      #"light.master_room_drawer_led",
                                      #"light.master_room_bed_led",
                                    ]
  
      self.other_lights            = ["light.master_room_entrance_light",
                                      'switch.master_room_balcony_wall_light',
                                      #"switch.master_room_dressing_table_light",
                                     ]
  
      self.ceiling_lights          = ["light.master_room_bed_ceiling_light",
                                      "light.master_room_drawer_ceiling_light"]
      self.add_group('light', self.room_name + ' Ceiling Light', self.ceiling_lights)
  
      self.lights                  = self.ceiling_lights + self.lamps + self.leds + self.other_lights
  
      # Adaptive lighting
      if self.cfg_adaptive_lighting:
        self.al_light_list = [deepcopy(self.al_light_list[0]), deepcopy(self.al_light_list[0])]
        self.al_light_list[0]["lights"]           = self.ceiling_lights + self.lamps
        self.al_light_list[1]["name"]             = 'Master Room Entrance'
        self.al_light_list[1]["lights"]           = ["light.master_room_entrance_light"]
        self.al_light_list[1]["sleep_brightness"] = 15
  
    def get_cover_entities(self):
      super().get_cover_entities()
      # Cover entities
      #"cover.master_room_blind" - too noisy
      self.curtains               = [ "cover.master_room_curtain"]
  
    def get_tv_entities(self):
      super().get_tv_entities()
      self.tvs                     = [f"media_player.{self.room_entity}_tv"]
      self.tv_picture_mode         = [f"input_select.{self.room_entity}_tv_picture_mode"]
      self.tv_soundbars            = [f"media_player.{self.room_entity}_sonos"]
      self.fire_tvs                = [f"media_player.{self.room_entity}_fire_tv"]
      self.media_players           = [f"media_player.{self.room_entity}_sonos"]
  
    # Overwrite scene 'All off' to include turning off blinds
    def callSceneService(self, scene_name):
      scene_service = super().callSceneService(scene_name)
  
      if scene_name == 'All Off':
        scene_service = [scene_service, self.set('cover.master_room_blind', "off")]
        return self.convertToSingleService(scene_service, alias=scene_name)
      else:
        return scene_service
  
    def get_remote_entities(self):
      super().get_remote_entities()
      self.wall_buttons            = [f"sensor.{self.room_entity}_entrance_wall_button"]
      self.buttons                 = self.wall_buttons + self.xiaomi_buttons
  
      # button states do not work well (not responsive) with template sensor renaming
      # and directly using button sensor is much responsive
      #self.four_key_buttons        = ['sensor.0x842e14fffe60b64a_action']
      self.eight_key_knob_buttons  = ['sensor.f0a3033b201b_action',
                                      'sensor.cf0c1f9b4dbc_action']
  
    def gen_room_specific_automations(self):
      self.add_offline_device_automations(
        device_type          = 'Zigbee',
        offline_device       = 'switch.master_toilet_wall_switch',
        gateway_power_switch = 'switch.master_room_gateway_power',
        tts_message          = self.automation_room_name + "2F gateway zigbee devices are offline - Restarting gateway"
        )
  
      self.add_offline_device_automations(
        device_type          = 'Wifi',
        offline_device       = 'cover.master_room_blind_1',
        tts_message          = self.automation_room_name + "2F wifi devices are offline. You may want to manual restart 2.4Ghz Wifi."
        )
  
      self.gen_a_button_toggle_automation( button_state_list=[ "1", "single", "button_1_single"],
                                           button_state_name='Single',
                                           button_list = [f"sensor.{self.room_entity}_entrance_wall_button"],
                                           device_list = [f'light.{self.room_entity}_entrance_light'],
                                           device_name ='Entrace Light',
                                           switch_type ="Entrance Wall Switch")
  
    def gen_window_automations(self):
      if len(self.windows) > 0:
        self.add_window_open_notification_when_leaving_zone_automations()
        #self.add_window_open_notification_when_going_to_sleep_automations()
        #self.add_window_open_notification_when_timeout_automations()
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'master-room'
      self.dashboard_view_name    = 'master-room'
      self.room_icon              = 'mdi:bed-king-outline'
      #self.room_theme             = 'ios-dark-mode-dark-green'
  
  
  class MasterToilet(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name              = 'Master Toilet'
      self.room_short_name        = 'MT'
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      self.cfg_scene              = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_auto_curtain_ctl   = True
      self.cfg_adaptive_lighting  = True
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
      self.add_device('0x00158d00047d69be',                 self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
      self.add_device("xiaomi_cn_blt_3_1nu46jugl0o00_mini", self.room_name,                    'Temperature Sensor', "Mijia3 Temperature Sensor 3 Mini", integration='Xiaomi Home', enable_shower_sensor=True)
  
      # self.add_device("a4c1381d6ddb",                     self.room_name,                     'Temperature Sensor', "Mijia2 Temperature Sensor", enable_humidity_sensor=True)
      #self.add_device('e4aaec80bc19',                     self.room_name + ' Door',           'Door Sensor',        'Mijia2 Contact')
      #self.add_device("a4c13846b902",                     self.room_name + ' Basin',          'Motion Sensor',      "Linptech Occupancy Sensor ES3")
      #self.add_device("linp_cn_blt_3_1keg2q6k4cg00_es2",  self.room_name + ' Basin Xiaomi Home',      'Motion Sensor',      "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      self.add_device("linp_cn_blt_3_1oniskbboc802_es5b",  self.room_name + ' Basin Xiaomi Home',      'Motion Sensor',      "Linptech Occupancy Sensor ES5", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
  
      self.add_device('0x00158d000460247b',               self.room_name + ' Dressing Room',  'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
      #self.add_device('0x00158d00057b2b4c',               self.room_name + ' Basin',          'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
      #self.add_device('0x00158d00054750ca',               self.room_name + ' Shower',         'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
      self.add_device('smart_switch_2005289130549690814648e1e91dcebd_outlet',
                                                           self.room_name + ' Floor LED',      'Switch',             'Generic Switch') # mss210_cebd_outlet
      self.add_device('0x04cf8cdf3c7cc9c4',                                 self.room_name + ' Mirror Sensor',         'Light Sensor',       'Xiaomi Light Detection Sensor To Mirror Sensor')
      self.add_device('adp_cn_1206089908_adfbt6_switch_b_p_3_2',            self.room_name + ' Mirror LED',            'Switch',             'Generic Switch')
      self.add_device('adp_cn_1206089908_adfbt6_switch_a_p_3_1',            self.room_name + ' Mirror Demister',       'Switch',             'Generic Switch')
      self.add_device('adp_cn_1206089908_adfbt6_battery_percentage_p_3_15', self.room_name + ' Mirror Robot Battery',  'Battery',            'Generic Battery')
      self.add_device('lumi_cn_blt_3_1ev0qguhcec00_mcn001',                 self.room_name + ' Mirror',                'Button',             'MiJia Wireless Switch 2', integration='Xiaomi Home')
  
  
      self.add_device("master_toilet_ceiling_light_hue",  self.room_name + " Ceiling Light",  'Light',              "Generic Light")
      #self.add_device('0x00158d000424f98c',               self.room_name + ' Blind',          'Button',             'MiJia Wireless Switch', integration='Z2M')
      #self.add_device('0x00158d000171756e',      self.room_name + ' Floor LED',             'Switch',             'Mi Power Plug ZigBee')
      # Dressing Room
      self.add_device("0x00158d00042d4092",      self.room_name + " Dressing Room",         'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Single Rocker)")
      self.add_device("28d1272057d5",            self.room_name + " Dressing Room Light",   'Light',              "Mijia BLE Lights")
      self.add_device("0x00158d00070b2f2a",      self.room_name + " Dressing Room Blind",   'Blind',              "Aqara roller shade motor")
      self.add_device('va4111274240',            self.room_name,                            'Raditor',            'Tado Homekit')
  
  
  
    def get_remote_entities(self):
      super().get_remote_entities()
      # N.B. Xiaomi zigbee button rename using template does not sample very well
      # and directly using button sensor is much responsive
      # Use manual rename on the native entity itself
      self.wall_buttons    = [f"sensor.{self.room_entity}_wall_button",
                              f"sensor.{self.room_entity}_dressing_room_wall_button"]
  
  
    def gen_button_automations(self):
      super().gen_button_automations()
  
      # 4-key IKEA Button
      self.button_device_id = 'e1baf91470d870ed5a9ac8e68f0d6227'
  
      self.automation_list += [{
          "alias" : "ZLB-" + self.automation_room_name + " Button Light Control" + "-" + self.room_name,
          "configured": self.cfg_remote_light,
          "trigger":
          ([{"device_id": self.button_device_id, "subtype": "on",                   "id": self.INCREMENT_CEILING_LIGHTS, "domain": "mqtt", "type":"action", "trigger":"device",}]) + \
          ([{"device_id": self.button_device_id, "subtype": "brightness_move_up",   "id": self.INCREMENT_CEILING_LIGHTS, "domain": "mqtt", "type":"action", "trigger":"device",}]) + \
          ([{"device_id": self.button_device_id, "subtype": "off",                  "id": self.DECREMENT_CEILING_LIGHTS, "domain": "mqtt", "type":"action", "trigger":"device",}]) + \
          ([{"device_id": self.button_device_id, "subtype": "brightness_move_down", "id": self.DECREMENT_CEILING_LIGHTS, "domain": "mqtt", "type":"action", "trigger":"device",}]) + \
          ([{"device_id": self.button_device_id, "subtype": "arrow_left_click",     "id": self.TOGGLE_CEILING_LIGHTS   , "domain": "mqtt", "type":"action", "trigger":"device",}]) + \
          ([{"device_id": self.button_device_id, "subtype": "arrow_right_click",    "id": self.TOGGLE_LEDS             , "domain": "mqtt", "type":"action", "trigger":"device",}]) + \
          ([]),
          "mode":"queued", # this has to be queued to make sure no button press is ignored
          "action": self.get_trigger_action_list()
      }]
  
  
      self.automation_list += [{
          "alias" : "ZLB-" + self.automation_room_name + "Mirror Button Control" + "-" + self.room_name,
          "configured": self.cfg_remote_light,
          "trigger":
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_mirror_button_single_click", 'to': 'on', "id": self.TOGGLE_LAMP_0     }]) if len(self.lamps)     > 0 else []) + \
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_mirror_button_double_click", 'to': 'on', "id": self.TOGGLE_LEDS       }]) if len(self.leds)      > 0 else []) + \
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_mirror_button_long_press",   'to': 'on', "id": self.TOGGLE_DEMISTER   }]) if len(self.demisters) > 0 else []) + \
            ([]),
          "mode":"queued", # this has to be queued to make sure no button press is ignored
          "action": self.get_trigger_action_list()
      }]
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.dressing_room_motion_sensors = [
        f"binary_sensor.{self.room_entity}_dressing_room_motion_sensor_motion"]
      self.toilet_motion_sensors = [
        f"binary_sensor.{self.room_entity}_basin_motion_sensor_motion",
        f"binary_sensor.{self.room_entity}_shower_motion_sensor_motion"
      ] + ([f"binary_sensor.{self.room_entity}_basin_xiaomi_home_occupancy_sensor_occupancy"] if self.xiaomi_home_occupancy else []) \
        + ([f"binary_sensor.{self.room_entity}_basin_occupancy_sensor_occupancy"]             if self.gateway_occupancy     else [])
  
      self.all_motion_sensors = self.dressing_room_motion_sensors + self.toilet_motion_sensors
      self.inside_to_outside_timeout = 1*30 # 30s timeout for Linptech ES5
  
    def get_light_entities(self):
      super().get_light_entities()
      # Light/Switch entities
      self.dressing_room_lights    = [f'light.{self.room_entity}_dressing_room_light']
  
      self.ceiling_lights          = self.ceiling_lights  + self.dressing_room_lights
      self.lamps                   = [f"switch.{self.room_entity}_mirror_led"]
      self.leds                    = [f"switch.{self.room_entity}_floor_led"]
      self.lights                  = self.leds + self.lamps + self.ceiling_lights
  
      # Adaptive lighting
      if self.cfg_adaptive_lighting:
        self.al_light_list[0]["lights"]           += self.ceiling_lights
        self.al_light_list[0]["sleep_brightness"]  = 1
  
    def get_mirror_entities(self):
      super().get_mirror_entities()
      self.mirror_sensors          = [f"switch.{self.room_entity}_mirror_led"]
      self.demisters               = [f"switch.{self.room_entity}_mirror_demister"]
  
    def get_cover_entities(self):
      super().get_cover_entities()
      # Cover entities
      self.curtains               = [ "cover.master_toilet_dressing_room_blind"]
  
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'master-room'
      self.dashboard_view_name = 'master-toilet'
      self.room_icon           = 'mdi:shower-head'
  
  
  class Kitchen(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'Kitchen'
      self.room_short_name       = 'KC'
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      self.cfg_scene              = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_auto_curtain_ctl   = True
      self.cfg_adaptive_lighting  = True
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.all_motion_sensors = [
        f"binary_sensor.{self.room_entity}_worktop_motion_sensor_motion",
        f"binary_sensor.{self.room_entity}_dining_motion_sensor_motion",
        f"binary_sensor.{self.room_entity}_dining_table_motion_sensor_motion",
      ] + ([f"binary_sensor.{self.room_entity}_table_xiaomi_home_occupancy_sensor_occupancy"] if self.xiaomi_home_occupancy else []) \
        + ([f"binary_sensor.{self.room_entity}_table_occupancy_sensor_occupancy"]             if self.gateway_occupancy     else [])
  
      self.inside_to_outside_timeout = 2*60
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
  
      self.add_device('ttlock_front_door',              "Front Door",                'Lock',     'Generic Locks')
      self.add_device('ttlock_front_door_battery',      "Front Door Lock Battery",   'Battery',  'Generic Battery')
      self.add_device('e4aaec80bc25',                   "Front Door",                'Door',     'Mijia2 Contact')
  
      #self.add_device('x1_battery_2',                               "Vaccum Online State",            'Vaccum Battery',      'Generic Battery')
      self.gui_ctl_entity_list += ['sensor.x1_battery_2'] # add to GUI
      self.add_automation('vacuum.x1',       'Vacuum Robot',   "Wifi Device Reconnect When Unavailable", unavailable_period='00:03:00', unavailable_device_id='f666003acf32413fb68e8f56007ceaf9')
      self.add_automation('lock.front_door', 'TTLock',         "Wifi Device Reconnect When Unavailable", unavailable_period='00:03:00', unavailable_device_id='7a2c07d362d6bb09ff3edad7ffe37d7a')
  
      self.add_device("582d34828f85",                               self.room_name,                   'Temperature Sensor', "Qingping Lite Temperature Sensor")
      #self.add_device("a4c1380e91a7",                               self.room_name,                   'Temperature Sensor', "Mijia2 Temperature Sensor")
      self.add_device("curtain_50",                                 self.room_name + " Curtain",      'Curtain',            "Generic Curtain") # Switchbot Matter
      self.add_device('0x00158d0005210fa9',                         self.room_name + ' Extractor',    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)', switch_rename_dir={2: 'Kitchen Extractor'})
      self.add_device('0x04cf8cdf3c7ad647',                         self.room_name,                   'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Triple Rocker)', flex_switch=[2], switch_rename_dir={3: 'Kitchen Floor LED'})
      #self.add_device('mss210_c944_outlet',                         self.room_name + ' Plate Warmer', 'Switch',             'Generic Switch')
      #self.add_device('560a_measure_mss310_main_channel',           self.room_name + ' Hot Water',    'Switch',             'Generic Switch')
  
      self.add_device('smart_switch_24110804769064510803c4e7ae0ff809_power',  'Rice Cooker Power',         'Power',          'Generic Power Measurement Switch', power_on_threshold=10)
      self.add_device('smart_switch_24110804769064510803c4e7ae0ff809_outlet', 'Rice Cooker Switch',        'Switch',         'Generic Switch')
      self.add_device('smart_switch_24110805022128510803c4e7ae0ffcf7_power',  'Plate Warmer Power',        'Power',          'Generic Power Measurement Switch', power_on_threshold=10, smooth_power=False) # plate warmer does not need to smooth as it is always above threshold when on
      self.add_device('smart_switch_24110805022128510803c4e7ae0ffcf7_outlet', 'Plate Warmer Switch',       'Switch',         'Generic Switch')
      self.add_device('0x00158d000171756e_power',                             'Baby Food Cooker Power',    'Power',          'Generic Power Measurement Switch', power_on_threshold=5, smooth_power=False, delay_off_minute=3)
      self.add_device('0x00158d000171756e_plug',                              'Baby Food Cooker Switch',   'Switch',         'Generic Switch')
      self.add_device('smart_plug_20030678930061251h3448e1e91852b1_power',    'Washing Machine Power',     'Power',          'Generic Power Measurement Switch', power_on_threshold=10)
      self.add_device('smart_plug_20030602740631251h3448e1e918560a_power',    'Dish Washer Power',         'Power',          'Generic Power Measurement Switch', power_on_threshold=5)
  
      self.add_device('0x00158d00057acaac',                 self.room_name + ' Dining',             'Motion Sensor', 'Aqara Motion and Illuminance Sensor')
      self.add_device('0x00158d0004660308',                 self.room_name + ' Worktop',            'Motion Sensor', 'Aqara Motion and Illuminance Sensor')
      self.add_device("a4c1387f7df0",                       self.room_name + ' Table',              'Motion Sensor', "Linptech Occupancy Sensor ES3")
      #self.add_device("a4c1381a4361",                       self.room_name + ' Table',        'Motion Sensor',      "Linptech Occupancy Sensor ES3")
      #self.add_device("linp_cn_blt_3_1kdf7mlc8k400_es2",   self.room_name + ' Table Xiaomi Home',      'Motion Sensor',      "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      self.add_device("e4aaec4500e4",                       self.room_name + " Window",             'Window',        "Mijia2 Contact")
  
      self.add_device("kitchen_ceiling_light_hue",                  self.room_name + " Ceiling Light",'Light',              "Generic Light")
      self.add_device("yeelink_cn_472898922_ceil30_s_2_light",      self.room_name + " Dining Light", 'Light',              "Generic Light")  # Xiaomi Home
      #self.add_device("kitchen_dining_light_yeelight",              self.room_name + " Dining Light", 'Light',              "Generic Light") # Yeelight - go offline when device is roaming to another AP
      #self.add_device("kitchen_tv_led_magic_home",                  self.room_name + " TV LED",       'Light',              "Generic Light")
      self.add_device("kitchen_worktop_led_tuya",                   self.room_name + " Worktop LED",  'Light',              "Generic Light")
      #self.add_device("18c23c2caa33_water_leak",                    self.room_name + " Water Sensor", 'Water Sensor',       "Generic Binary Sensor")
  
      self.add_device("lumi_cn_blt_3_1h1quuv4s4g00_bmcn01_submersion_state_p_2_1",   self.room_name + " Water Leak Sensor",         'Leak Sensor',       "Generic Binary Sensor")
      self.add_device("lumi_cn_blt_3_1h1quuv4s4g00_bmcn01_battery_level_p_3_1",      self.room_name + " Water Leak Sensor Battery", 'Battery',           "Generic Battery")
  
      self.add_device('va3767669760',                               self.room_name,                   'Raditor',            'Tado Homekit')
      #self.add_device("bot_d980",                                   self.room_name + " Ice Maker",     'Switchbot',        "Generic Switch") #
  
      # MCCGQ02HL
      #self.add_device("0x158d00023e6015",       self.room_name + " Worktop",             "Aqara Wireless Switch")
      #self.add_device('54ef44e559c6',                               self.room_name + ' Dining Table', 'Motion Sensor',      'Mijia Motion Sensor 2')
  
    def get_window_entities(self):
      super().get_window_entities()
      self.windows                 = [f"binary_sensor.{self.room_entity}_window",
                                      f"binary_sensor.front_door",
                                      f"lock.front_door",
                                      ]
      self.timeout_windows         = self.windows
  
    def get_light_entities(self):
      super().get_light_entities()
      # Light/Switch entities
      self.ceiling_lights          = [ f"light.{self.room_entity}_ceiling_light",
                                       f"light.{self.room_entity}_dining_light"]
      self.leds                    = [f"switch.{self.room_entity}_floor_led",
                                       f"light.{self.room_entity}_tv_led"]
      self.lights                  = self.leds + self.lamps + self.ceiling_lights
  
      # Adaptive lighting
      self.al_light_list[0]["lights"] += self.ceiling_lights + [f"light.{self.room_entity}_worktop_led"]
      self.al_light_list[0]["sleep_brightness"]  = 1
  
      self.extractor               = ['switch.' + self.room_entity + '_extractor']
  
  
    def get_cover_entities(self):
      super().get_cover_entities()
      # Cover entities
      self.curtains               = ["cover." + self.room_entity + "_curtain"]
  
    def get_tv_entities(self):
      super().get_tv_entities()
      #self.tvs                     = [f"media_player.{self.room_entity}_tv"]
      #self.tv_picture_mode         = [f"input_select.{self.room_entity}_tv_picture_mode"]
      self.fire_tvs                = [f"media_player.{self.room_entity}_fire_tv"]
      self.media_players            = [f"media_player.{self.room_entity}_sonos"]
  
    def gen_wall_button_single_automations(self):
      self.gen_a_button_toggle_automation(      button_state_list=["single_left", "button_1_single"],
                                                button_state_name='Single Left',
                                                device_list=["light." + self.room_entity + "_ceiling_light"],
                                                device_name='Ceiling Light')
  
      #self.gen_a_button_toggle_automation(      button_state_list=["single_center", "button_2_single"],
      #                                          button_state_name='Single Center',
      #                                          device_list='light.kitchen_dining_light',
      #                                          device_name='Dining Light')
  
      #self.gen_a_button_toggle_automation(      button_state_list=["single_right", "button_3_single"],
      #                                          button_state_name='Single Right',
      #                                          device_list=self.leds,
      #                                          device_name='Floor LED')
  
      self.gen_a_button_toggle_automation(      button_state_list=["single_left", "button_1_single"],
                                                button_state_name='Single Left',
                                                button_list = ["sensor.kitchen_extractor_wall_button"],
                                                device_list = ['light.kitchen_worktop_led'],
                                                device_name ='Worktop LED',
                                                switch_type="Worktop Wall Switch")
  
      #self.gen_a_button_toggle_automation(      button_state_list=["single_right", "button_2_single"],
      #                                          button_state_name='Single Right',
      #                                          button_list = "sensor.kitchen_extractor_wall_button"
      #                                          device_list ='switch.kitchen_extractor',
      #                                          device_name ='Extractor')
  
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'lovelace-kitchen'
      self.dashboard_view_name = 'kitchen'
      self.room_icon           = 'mdi:silverware-clean'
  
    # Customize system card information
    def getNavigationRoomCard (self):
      room_card = super().getNavigationRoomCard()
      # Add vaccum info
      dashboard_view_helpers.append_navigation_title_secondary(
        room_card,
        "{% set vaccum = 'vacuum.x1' %} {% if   is_state(vaccum, 'docked') %}\n 🔋 \n{% elif is_state(vaccum, 'cleaning') %}\n 🧹 \n{% elif is_state(vaccum, 'unavailable') %}\n 🌐 \n{% else %}\n {{states('vacuum.x1')}} \n{% endif %}",
      )
      # Add additional cards
      dashboard_view_helpers.prepend_navigation_status_cards(room_card, [
        self.getTemplateCard(
          icon       = "mdi:pipe-leak",
          icon_color = "red",
          condition_entity = 'binary_sensor.kitchen_water_leak_sensor',
        )
      ] + [
        self.getTemplateCard(
          icon       = "mdi:rice",
          icon_color = "yellow",
          condition_entity = 'binary_sensor.rice_cooker_power'
        )
      ] + [
        self.getTemplateCard(
          icon       = "mdi:robot-vacuum",
          icon_color = "purple",
          condition_entity = 'vacuum.x1',
          condition_state  = 'cleaning'
        )
      ] + [
        self.getTemplateCard(
          icon       = "mdi:washing-machine",
          icon_color = "light-blue",
          condition_entity = 'binary_sensor.washing_machine_power'
        )
      ] + [
        self.getTemplateCard(
          icon       = "mdi:dishwasher",
          icon_color = "pink",
          condition_entity = 'binary_sensor.dish_washer_power'
        )
      ] + [
        self.getTemplateCard(
          icon       = "mdi:ice-cream",
          icon_color = "yellow",
          condition_entity = 'switch.kitchen_ice_maker'
        )
      ] + [
        self.getTemplateCard(
          icon       = "hass:fan",
          icon_color = "cyan",
          condition_entity = 'switch.kitchen_extractor'
        )
      ])
  
      return room_card
  
  
  class LivingRoom(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'Living Room'
      self.room_short_name       = 'LR'
      self.num_of_xiaomi_button  = 1
      self.num_of_lamps          = 2
      # Enables
      self.cfg_scene              = True
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_scene_color_lamp   = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      self.cfg_adaptive_lighting  = True
      self.cfg_led_only_scene     = True
  
    def get_room_name_and_property(self):
      super().get_room_name_and_property()
      self.room_type     = 'bedroom' # as we often fall into sleep in living room
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
  
      self.add_device("a4c138c69e9f",                       self.room_name + ' Door',             'Motion Sensor', "Linptech Occupancy Sensor ES3")
      self.add_device("linp_cn_blt_3_1kdf3f5aokk00_es2",    self.room_name + ' Door Xiaomi Home', 'Motion Sensor', "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      self.add_device("403059d98baf",                       self.room_name + ' TV',               'Motion Sensor', "Xiaomi Occupancy Sensor")
      self.add_device("xiaomi_cn_blt_3_1kfc93o04kc00_03",   self.room_name + ' TV Xiaomi Home',   'Motion Sensor', "Xiaomi Occupancy Sensor", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      self.add_device('d44867b89dd3',                       self.room_name + ' Desk',             'Motion Sensor', 'Xiaomi Occupancy Sensor')
      self.add_device("xiaomi_cn_blt_3_1icm36tbg4s04_03",   self.room_name + ' Desk Xiaomi Home', 'Motion Sensor', "Xiaomi Occupancy Sensor", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      self.add_device('403059d9505f',                       self.room_name + ' Sofa',             'Motion Sensor', 'Xiaomi Occupancy Sensor')
      self.add_device("xiaomi_cn_blt_3_1kfc8s5c0kc00_03",   self.room_name + ' Sofa Xiaomi Home', 'Motion Sensor', "Xiaomi Occupancy Sensor", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
  
      # self.add_device("linp_cn_blt_3_1kdf02hpkk400_es2",    self.room_name + ' Sofa Xiaomi Home', 'Motion Sensor', "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      # self.add_device("a4c1381b8035",                       self.room_name + ' Sofa',             'Motion Sensor', "Linptech Occupancy Sensor ES3")
  
      self.add_device('0x00158d0003140ea8',                 self.room_name + ' Entrance',      'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
     #self.add_device("dced8308e951",                       self.room_name,                    'Motion Sensor',      "Ziqing Occupancy Sensor")
    # self.add_device('0x54ef441000792d1d',                 self.room_name + ' Sofa',          'Pressure Sensor 1',  'Aqara Pressure Sensor')
      self.add_device("1c34f1acbb16",                       self.room_name,                    'Temperature Sensor', "Mijia2 Temperature Sensor",        postfix='1')
      self.add_device("a4c1381d6ddb",                       self.room_name,                    'Temperature Sensor', "Mijia2 Temperature Sensor",        postfix='2')
      # self.add_device("xiaomi_cn_blt_3_1nu46jugl0o00_mini", self.room_name,                    'Temperature Sensor', "Mijia3 Temperature Sensor 3 Mini", postfix='2', integration='Xiaomi Home')
      self.add_average_temperature_sensor(sensor_1=  'sensor.living_room_temperature_sensor_1',
                                          sensor_2=  'sensor.living_room_temperature_sensor_2',
                                          sensor_out='sensor.living_room_temperature_sensor')
      self.add_device('0x00158d0008d8ead8',                 self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', flex_switch=True)
      self.add_device("0x54ef441000452fd8",                 self.room_name + ' Curtain',       'Curtain',            "Aqara B1 curtain motor",    postfix='1')
      self.add_device("0x54ef4410001f409c",                 self.room_name + ' Curtain',       'Curtain',            "Aqara B1 curtain motor",    postfix='2')
      self.add_device('0x04cf8cdf3c7b560f',                 self.room_name + ' East Side',     'Light Sensor',       'Xiaomi Light Detection Sensor')
      self.add_device('0x04cf8cdf3c7b560f_illuminance',     self.room_name ,                   'Light Sensor',       'Generic Light Intensity')
  
      #self.add_device('',                 self.room_name,                    'Button',             'MiJia Wireless Switch')
      self.add_device("sonoff_1001e49906_1",                self.room_name + ' Gateway Power', 'Switch',             "Generic Switch")
      self.add_device("e4aaec80beca",                       self.room_name + " Window",        'Window',             "Mijia2 Contact")
      self.add_device("e4aaec80bedb",                       self.room_name + " Sliding Door",  'Door',               "Mijia2 Contact")
  
      self.add_device('0x00158d00054d83df',                 'Boiler Room',                     'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
      self.add_device('28d127202ef6',                       'Boiler Room Light',               'Light',              'Mijia BLE Lights')
      self.add_device("hue_color_lamp_1",                    self.room_name + " Floor Light 1",'Light',              "Generic Light")
      self.add_device("hue_color_lamp_2",                    self.room_name + " 3 Head Lamp 1",'Light',              "Generic Light")
      self.add_device("hue_color_lamp_3",                    self.room_name + " 3 Head Lamp 2",'Light',              "Generic Light")
      self.add_device("hue_color_lamp_4",                    self.room_name + " 3 Head Lamp 3",'Light',              "Generic Light")
      self.lr_floor_light_2       = ["light.living_room_3_head_lamp_1",
                                     "light.living_room_3_head_lamp_2",
                                     "light.living_room_3_head_lamp_3",
                                     ]
      self.add_group('light', 'Living Room Floor Light 2', self.lr_floor_light_2)
  
      self.add_device('mss210_ef0f_outlet',                  self.room_name + ' Floor Light 3','Switch',             'Generic Switch') # ef0f_29831979
      #self.add_device('smart_switch_2009117038613290829948e1e932ef0f_outlet',
      #                                                       self.room_name + ' Floor Light 3','Switch',             'Generic Switch') # ef0f_29831979_mss210_main_channel
      self.add_device('va2282557696',                        self.room_name,                   'Raditor',            'Tado Homekit')
      #self.add_device("living_room_ceiling_light_yeelight",   self.room_name + ' Ceiling Light','Light',              "Generic Light") # Yeelight integration
      #self.add_device("yeelink_ceil30_3a4b_light",            self.room_name + ' Ceiling Light','Light',              "Generic Light") # MiIoT Auto often disconnected
      self.add_device("yeelink_cn_436905718_ceil30_s_2_light", self.room_name + ' Ceiling Light','Light',              "Generic Light")  # Xiaomi Home integration - often disconnect when using two HA instances
      self.add_automation('light.living_room_ceiling_light', 'Ceiling Light', "Wifi Device Reconnect When Unavailable", unavailable_period='00:02:00', unavailable_device_id='d21abe62c7f76149e534e5a63a9e772e')
  
      self.add_device('lock_ultra_f8',                     "Garden Door Lock",                'Lock',     'Generic Locks')   # Matter via Switchbot Hub - main usecase
      self.add_device('lock_ultra_28f8',                   "Garden Door Lock Bluetooth",      'Lock',     'Generic Locks')   # Bluetooth Switchbot - Only using for jammed state for auto-unlocking
      self.add_device('lock_ultra_silver_battery',         "Garden Door Lock Battery",        'Battery',  'Generic Battery') # Cloud via Switchbot Hub - Only using for battery state reporting
      #self.add_device('0x00158d00052d5691_contact_2',      "Garden Door Handle",              'Door',     'Generic Binary Sensor')
      self.add_device('isa_cn_blt_3_1nu4c6j88c002_dw2hl',  "Garden Door Handle",              'Door',     'Mijia2 Contact', integration='Xiaomi Home') # garden door handle BLE
  
      #('0x00158d0004501b0a', 'Living Room Sofa',           'Aqara Motion and Illuminance Sensor')
      #('0x00158d0001212747', 'Boiler Room',                'Aqara Door & Window Sensor')
  
      self.add_device('remote_control_4dbd', self.room_name +' 6 Key', 'Button', 'Yeelight 6 Key Remote')
  
    def gen_button_automations(self):
      super().gen_button_automations()
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.other_motion_sensors = [
            f"binary_sensor.{self.room_entity}_entrance_motion_sensor_motion",
      ] + ([f"binary_sensor.{self.room_entity}_door_xiaomi_home_occupancy_sensor_occupancy"] if self.xiaomi_home_occupancy else []) + [
      ] + ([f"binary_sensor.{self.room_entity}_door_occupancy_sensor_occupancy"]             if self.gateway_occupancy     else []) + [
      ] + ([f"binary_sensor.{self.room_entity}_desk_xiaomi_home_occupancy_sensor_occupancy"] if self.xiaomi_home_occupancy else []) \
        + ([f"binary_sensor.{self.room_entity}_desk_occupancy_sensor_occupancy"]             if self.gateway_occupancy     else []) + [
      ] + ([f"binary_sensor.{self.room_entity}_tv_xiaomi_home_occupancy_sensor_occupancy"]   if self.xiaomi_home_occupancy else []) \
        + ([f"binary_sensor.{self.room_entity}_tv_occupancy_sensor_occupancy"]               if self.gateway_occupancy     else []) + [
      ] + ([f"binary_sensor.{self.room_entity}_sofa_xiaomi_home_occupancy_sensor_occupancy"] if self.xiaomi_home_occupancy else []) \
        + ([f"binary_sensor.{self.room_entity}_sofa_occupancy_sensor_occupancy"]             if self.gateway_occupancy     else [])
  
      self.entrance_motion_sensors = [
        f"binary_sensor.{self.room_entity}_entrance_motion_sensor_motion",
        f"binary_sensor.{self.room_entity}_sliding_door"
      ] + ([f"binary_sensor.{self.room_entity}_tv_xiaomi_home_occupancy_sensor_occupancy"]   if self.xiaomi_home_occupancy else []) \
        + ([f"binary_sensor.{self.room_entity}_tv_occupancy_sensor_occupancy"]               if self.gateway_occupancy     else [])
  
      self.all_motion_sensors = self.other_motion_sensors + self.entrance_motion_sensors
  
      self.inside_to_outside_timeout = 2*60
      self.sleep_to_outside_timeout  = 3*60
      self.inside_to_sleep_timeout   = 30*60
  
    def get_window_entities(self):
      super().get_window_entities()
      self.windows                 = [f"binary_sensor.{self.room_entity}_sliding_door",
                                      f"binary_sensor.{self.room_entity}_window",
                                      f"binary_sensor.garden_door_handle",
                                      f"lock.garden_door_lock",
                                      ]
      self.timeout_windows         = []
  
    def gen_window_automations(self):
      if len(self.windows) > 0:
        self.add_window_open_notification_when_leaving_zone_automations()
        self.add_window_open_notification_when_going_to_sleep_automations()
        self.add_window_open_notification_when_timeout_automations()
  
    def get_tv_entities(self):
      super().get_tv_entities()
      self.tvs                     = [f"media_player.{self.room_entity}_tv"]
      self.tv_picture_mode         = [f"input_select.{self.room_entity}_tv_picture_mode"]
      self.tv_soundbars            = [f"media_player.{self.room_entity}_sonos"]
      self.fire_tvs                = [f"media_player.{self.room_entity}_fire_tv"]
      self.media_players           = [f"media_player.{self.room_entity}_sonos"]
  
    def get_remote_entities(self):
      super().get_remote_entities()
      self.eight_key_knob_buttons  = ['sensor.df8c562a81a6_action']
  
    def get_light_entities(self):
      super().get_light_entities()
      self.leds                    = [#"light.living_room_tv_led",
                                      #"light.living_room_sofa_led",
                                      f"switch.{self.room_entity}_floor_light_3",
                                      ]
      self.lamps                   = [f"light.{ self.room_entity}_floor_light_1",
                                      f"light.{ self.room_entity}_floor_light_2",
                                      #f"switch.{self.room_entity}_floor_light_3",
                                     ]
  
      self.lights                  = self.leds + self.lamps + self.ceiling_lights
      # Adaptive lighting
      self.al_light_list[0]["max_color_temp"] = 6500
      self.al_light_list[0]["lights"] += self.ceiling_lights + \
                                              [ f"light.{self.room_entity}_floor_light_1",
                                                f"light.{self.room_entity}_3_head_lamp_1",
                                                f"light.{self.room_entity}_3_head_lamp_2",
                                                f"light.{self.room_entity}_3_head_lamp_3",
                                                f"light.boiler_room_light"]
  
      self.screen_leds            = f'switch.{self.room_entity}_desk_screen_led'
  
    def callSceneService(self, scene_name):
      # overwrite Hue scene with Hue light list
      self.hue_light_list        = [f"light.{ self.room_entity}_floor_light_1",
                                    f"light.{ self.room_entity}_3_head_lamp_1",
                                    f"light.{ self.room_entity}_3_head_lamp_2",
                                    f"light.{ self.room_entity}_3_head_lamp_3"] + self.ceiling_lights + self.leds
  
      if scene_name == 'Hue':
        scene_service  = [# turn off non rgb lights
                          { "service" : "pyscript.turn_rgb_light",
                            "data": {"light_list": self.hue_light_list,
                            "state": 'off',
                            "rgb" : 'non_rgb_only'}},
                          # set hue colors
                          { "service" : "pyscript.turn_rgb_light",
                            "data": {"light_list": self.hue_light_list}},
                          self.set(self.tvs, tv_brightness=2)]
        return self.convertToSingleService(scene_service, alias=scene_name)
      else:
        return super().callSceneService(scene_name)
  
  
    def get_cover_entities(self):
      super().get_cover_entities()
      # Cover entities
      self.curtains = [ f"cover.{self.room_entity}_curtain_1",
                        f"cover.{self.room_entity}_curtain_2",
                      ]
  
    def gen_room_specific_automations(self):
      self.add_offline_device_automations(
        device_type          = 'Zigbee',
        offline_device       = f'switch.living_room_wall_switch',
        gateway_power_switch = f'switch.living_room_gateway_power',
        tts_message          = self.automation_room_name + "0F gateway zigbee devices are offline. Restarting gateway."
        )
  
      self.add_offline_device_automations(
        device_type          = 'Wifi',
        offline_device       = 'light.kitchen_worktop_led',
        tts_message          = self.automation_room_name + "0F wifi devices are offline. You may want to manual restart 2.4Ghz Wifi."
        )
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'living-room'
      self.dashboard_view_name = 'living-room'
      self.room_icon           = 'mdi:youtube-tv'
  
    # Customize card information
    def getNavigationRoomCard (self):
      room_card = super().getNavigationRoomCard()
      # Add additional cards
      dashboard_view_helpers.prepend_navigation_status_cards(room_card, [
        self.getTemplateCard(
          icon       = "mdi:lock-open-variant-outline",
          icon_color = "red",
          condition_entity = 'lock.garden_door_lock',
          condition_state  = 'unlocked',
        )
      ] + [
      #  self.getTemplateCard(
      #    icon       = "mdi:door-open",
      #    icon_color = "red",
      #    condition_entity = 'binary_sensor.garden_door_handle',
      #    condition_state  = 'on',
      #  )
      ])
  
      return room_card
  
  
  
  class Garden(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name              = 'Garden'
      self.room_short_name        = 'GD'
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_scene              = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_temp_control       = False
  
    def get_room_name_and_property(self):
      super().get_room_name_and_property()
      self.room_type              = 'landing'
  
    def get_light_entities(self):
      super().get_light_entities()
      self.ceiling_lights          = ["switch.garden_ceiling_light"]
      self.lights                  = self.ceiling_lights
  
      self.al_sleep_mode = 'input_boolean.always_off_constant'
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.all_motion_sensors = [
        "binary_sensor.garden_sliding_door_motion_sensor_motion",
        "binary_sensor.garden_bike_shed_motion_sensor_motion"
      ]
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
      self.add_device('54ef44e34c16',           self.room_name + ' Bike Shed',      'Motion Sensor', 'Mijia Motion Sensor 2')
      self.add_device('0x00158d000548b8a5',     self.room_name + ' Sliding Door',   'Motion Sensor', 'Aqara Motion and Illuminance Sensor')
      self.add_device('0x00158d000522e00e',     self.room_name,                     'Wall Switch',   'Aqara D1 Wall Switch (With Neutral, Double Rocker)', switch_rename_dir={2: 'Garden Wall Light'})
  
      # Must lock to 0F AP, 1F provides bad signal and disconnection issues for both Meross LAN and Homekit integration.
      #self.add_device('smart_switch_2007317607464590823148e1e9295df5_outlet_1',
      #                                          self.room_name + ' Spotlight Meross LAN',   'Switch',        'Generic Switch') # mss425e_5df5_outlet_1 this entity in Meross LAN does not go back online after offline for a while
      self.add_device('mss425e_5df5_outlet_1',  self.room_name + ' Spotlight Homekit',      'Switch',        'Generic Switch') # Homekit went offline and didn't come back even with reload
  
      self.add_group('switch', 'Garden Ceiling Light', [#"switch.garden_spotlight_meross_lan",
                                                        "switch.garden_spotlight_homekit",
                                                        "switch.garden_wall_light",
                                                       ])
  
      #self.add_device('mss425e_5df5_outlet_2',  self.room_name + ' Spotlight 2',    'Switch',        'Generic Switch')
      #self.add_device('mss425e_5df5_outlet_3',  self.room_name + ' Spotlight 3',    'Switch',        'Generic Switch')
      self.add_device('a4c1386b73af_water_leak', self.room_name + ' Rain Sensor',    'Sensor',        'Generic Binary Sensor')
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'lovelace-garden'
      self.dashboard_view_name = 'garden'
      self.room_icon           = 'mdi:beach'
  
    # Customize card information
    def getNavigationRoomCard (self):
      room_card = super().getNavigationRoomCard()
      # Add additional cards
      dashboard_view_helpers.prepend_navigation_status_cards(room_card, [
        self.getTemplateCard(
          icon       = "mdi:weather-pouring",
          icon_color = "blue",
          condition_entity = f'binary_sensor.{self.room_name}_rain_sensor',
        )
      ])
  
      return room_card
  
  
  class EnSuiteRoom(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'En-suite Room'
      self.room_short_name       = 'ER'
      self.num_of_xiaomi_button  = 1
      self.num_of_lamps          = 2
      # Enables
      self.cfg_scene              = True
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      self.cfg_led_only_scene     = True
      self.cfg_motion_bed_led     = True
      self.cfg_auto_curtain_ctl   = True
      self.cfg_adaptive_lighting  = True
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
  
  
      self.add_device('0x00158d00047d69e6',              self.room_name,                       'Wall Switch',         'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
      #self.add_device("a4c1387f7df0",                    self.room_name + ' Bed',              'Motion Sensor',       "Linptech Occupancy Sensor ES3")
      #self.add_device("linp_cn_blt_3_1kenln2kkk800_es2", self.room_name + ' Bed Xiaomi Home',  'Motion Sensor',       "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      self.add_device("linp_cn_blt_3_1o9qf60mscc00_es5b",self.room_name + ' Bed Xiaomi Home',  'Motion Sensor',       "Linptech Occupancy Sensor ES5", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
  
      self.add_device('0x00158d00057b37be',              self.room_name + ' Entrance',         'Motion Sensor',       'Aqara Motion and Illuminance Sensor')
      self.add_device('0x00158d000423319f',              self.room_name + ' Floor 1',          'Motion Sensor',       'Aqara Motion and Illuminance Sensor')
      self.add_device('54ef44e58108',                    self.room_name + ' Floor 2',          'Motion Sensor',       'Mijia Motion Sensor 2')
      self.add_device("84b4dbf83a51",                    self.room_name,                       'Temperature Sensor',  "Mijia2 Temperature Sensor")
      #self.add_device("curtain_d29a",                    self.room_name + " Curtain",          'Curtain',             "Generic Curtain")
      self.add_device("curtain_67",                      self.room_name + " Curtain",          'Curtain',             "Generic Curtain")
  
      self.add_device("e27w_1_hue",                      self.room_name + " Lamp 1",           'Light',               "Generic Light")
      self.add_device("e27w_2_hue",                      self.room_name + " Lamp 2",           'Light',               "Generic Light")
      self.add_device("en_suite_room_ceiling_light_hue", self.room_name + " Ceiling Light",    'Light',               "Generic Light")
      self.add_device("en_suite_room_bed_led_magic_home", self.room_name + " Bed LED",         'Light',               "Generic Light")
      self.add_device('va1167266816',                    self.room_name,                       'Raditor',             'Tado Homekit')
      self.add_device('cxw_cn_blt_3_1hku51pm4ck00_ble006_battery_level_p_7_1003',
                                                         self.room_name + " Eight Button 1 Battery",   'Battery',  'Generic Battery')
      self.add_device('cxw_cn_blt_3_1hku3hs9sc800_ble006_battery_level_p_7_1003',
                                                          self.room_name + " Eight Button 2 Battery",   'Battery',  'Generic Battery')
  
      self.add_device('linp_cn_blt_3_1oquqak3cc801_ks1bp', self.room_name +' 4 Key',                    'Button', 'Linptech KS1 4-Key Button', integration='Xiaomi Home')
      self.add_device('line_cn_1195312213_fms5s_battery_level_p_5_1003', self.room_name + ' Lock Battery', 'Battery',            'Generic Battery')
  
      #self.add_device('0x00158d000403d6c0',              self.room_name,                       'Button',              'MiJia Wireless Switch')
      #self.add_device("0x04cf8cdf3c797717",              self.room_name + " Six Key Button 1", 'Button',              "Aqara Opple switch 3 bands", integration='Z2M')
      #self.add_device("dced8308f496",                    self.room_name,                       'Motion Sensor',       "Ziqing Occupancy Sensor")
      #self.add_device("a4c138a664b0",                    self.room_name + ' Bed',              'Motion Sensor',       "Linptech Occupancy Sensor ES3")
      #self.add_device("linp_cn_blt_3_1kfc8ifhsk400_es2",         \
      #                                                     self.room_name + ' Bed Xiaomi Home',      'Motion Sensor',      "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      #self.add_device('54ef44e559c6',                    self.room_name + ' Bed',              'Motion Sensor',       'Mijia Motion Sensor 2')
      #self.add_device('54ef44e58345',                    self.room_name + ' Bed',              'Motion Sensor',       'Mijia Motion Sensor 2')
      #self.add_device("a4c138b0eb53",                    self.room_name,                       'Temperature Sensor',  "Mijia2 Temperature Sensor")
  
    def get_remote_entities(self):
      super().get_remote_entities()
      # button states do not work well (not responsive) with template sensor renaming
      # and directly using button sensor is much responsive
      self.eight_key_knob_buttons  = ['sensor.d5154864a1bb_action',
                                      'sensor.ce327cd55cd0_action']
  
  
    def gen_button_automations(self):
      super().gen_button_automations()
  
    def get_tv_entities(self):
      super().get_tv_entities()
      #self.tv_room_entity          = 'portable'
      #self.tvs                     = [f"media_player.{self.tv_room_entity}_tv"]
      #self.tv_picture_mode         = [f"input_select.{self.tv_room_entity}_tv_picture_mode"]
      #self.fire_tvs                = [f"media_player.{self.tv_room_entity}_fire_tv"]
  
  
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.non_bed_motion_sensors = ['binary_sensor.en_suite_room_entrance_motion_sensor_motion',
                                     'binary_sensor.en_suite_room_floor_1_motion_sensor_motion',
                                     'binary_sensor.en_suite_room_floor_2_motion_sensor_motion']
  
      self.bed_motion_sensors = [
      ] + ([f"binary_sensor.{self.room_entity}_bed_xiaomi_home_occupancy_sensor_occupancy"] if self.xiaomi_home_occupancy else []) \
        + ([f"binary_sensor.{self.room_entity}_bed_occupancy_sensor_occupancy"]            if self.gateway_occupancy     else [])
  
  
      self.toilet_motion_sensors = [
        "group.en_suite_toilet_motion_group"
      ]
  
      self.all_motion_sensors = self.non_bed_motion_sensors + self.bed_motion_sensors + self.toilet_motion_sensors
  
      self.inside_to_outside_timeout = 2*60
      self.sleep_to_outside_timeout  = 3*60
      self.inside_to_sleep_timeout   = 30*60
  
    def get_light_entities(self):
      super().get_light_entities()
      # Light/Switch entities
      self.lamps                   = ["light.en_suite_room_lamp_1",
                                      "light.en_suite_room_lamp_2",]
      self.add_group('light', self.room_name + ' Lamp', self.lamps)
  
      self.leds                    = ["light.en_suite_room_bed_led"]
      self.lights                  = self.leds + self.lamps + self.ceiling_lights
  
      # Adaptive lighting
      self.al_light_list[0]["lights"] += self.lamps + self.ceiling_lights
  
    def get_cover_entities(self):
      super().get_cover_entities()
      # Cover entities
      self.curtains               = [ "cover.en_suite_room_curtain"]
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'en-suite-room'
      self.dashboard_view_name    = 'en-suite-room'
      self.room_icon              = 'mdi:bed-queen'
  
  class EnSuiteToilet(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'En-suite Toilet'
      self.room_short_name       = 'ET'
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_temp_control       = True
      self.cfg_scene              = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_led_only_scene     = True
      self.cfg_adaptive_lighting  = True
      self.cfg_temp_calibration   = True
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
      #self.add_device("0x158d00053fdaba",   self.room_name + ' Door',  'Door',               "Aqara Door & Window Sensor")
      self.add_device('0x158d000572839f',                     self.room_name,                       'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
      self.add_device("linp_cn_blt_3_1onif11i44g00_es5b",     self.room_name + ' Xiaomi Home',      'Motion Sensor',      "Linptech Occupancy Sensor ES5", integration='Xiaomi Home')
  
  
      self.add_device('0x158d000522d90c',           self.room_name,                       'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
      #self.add_device("582d34828cc6",               self.room_name,                       'Temperature Sensor', "Qingping Lite Temperature Sensor", enable_humidity_sensor=True)
      self.add_device("xiaomi_cn_blt_3_1nt5fj3n0c800_mini",      self.room_name,           'Temperature Sensor', "Mijia3 Temperature Sensor 3 Mini", integration='Xiaomi Home', enable_shower_sensor=True)
  
      #self.add_device("a4c1380e91a7",               self.room_name + ' Mirror','Temperature Sensor for Mirror Defrog', "Mijia2 Temperature Sensor")
      self.add_device('va0429069312',               self.room_name,                       'Raditor',            'Tado Homekit')
      self.add_device("en_suite_toilet_light_hue",  self.room_name + " Ceiling Light",    'Light',              "Generic Light")
  
      self.add_device('adp_cn_1206094287_adfbt6_switch_a_p_3_1',            self.room_name + ' Mirror LED',            'Switch',             'Generic Switch')
      self.add_device('adp_cn_1206094287_adfbt6_switch_b_p_3_2',            self.room_name + ' Mirror Demister',       'Switch',             'Generic Switch')
      self.add_device('adp_cn_1206094287_adfbt6_battery_percentage_p_3_15', self.room_name + ' Mirror Robot Battery',  'Battery',            'Generic Battery')
      self.add_device('lumi_cn_blt_3_1euso42kkc800_mcn001',                 self.room_name + ' Mirror',                'Button',             'MiJia Wireless Switch 2', integration='Xiaomi Home')
  
  
    def get_light_entities(self):
      super().get_light_entities()
      # Light/Switch entities
      self.lamps                   = [f"switch.{self.room_entity}_mirror_led"]
      self.lights                  = self.leds + self.lamps + self.ceiling_lights
      # Adaptive lighting
      self.al_light_list[0]["lights"] += self.ceiling_lights
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.all_motion_sensors = [
             f"binary_sensor.{self.room_entity}_motion_sensor_motion",
      ]  + ([f"binary_sensor.{self.room_entity}_xiaomi_home_occupancy_sensor_occupancy"] if self.xiaomi_home_occupancy else []) \
         #+ ([f"binary_sensor.{self.room_entity}_occupancy_sensor_occupancy"]            if self.gateway_occupancy     else [])
  
      self.inside_to_outside_timeout = 1*30 # 30s timeout for Linptech ES5
  
    def get_mirror_entities(self):
      super().get_mirror_entities()
      self.mirror_sensors          = [f"switch.{self.room_entity}_mirror_led"]
      self.demisters               = [f"switch.{self.room_entity}_mirror_demister"]
  
    def gen_button_automations(self):
      super().gen_button_automations()
  
      self.automation_list += [{
          "alias" : "ZLB-" + self.automation_room_name + "Mirror Button Control" + "-" + self.room_name,
          "configured": self.cfg_remote_light,
          "trigger":
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_mirror_button_single_click", 'to': 'on', "id": self.TOGGLE_LAMP_0     }]) if len(self.lamps)     > 0 else []) + \
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_mirror_button_double_click", 'to': 'on', "id": self.TOGGLE_LEDS       }]) if len(self.leds)      > 0 else []) + \
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_mirror_button_long_press",   'to': 'on', "id": self.TOGGLE_DEMISTER   }]) if len(self.demisters) > 0 else []) + \
            ([]),
          "mode":"queued", # this has to be queued to make sure no button press is ignored
          "action": self.get_trigger_action_list()
      }]
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'en-suite-room'
      self.dashboard_view_name    = 'en-suite-toilet'
      self.room_icon              = 'mdi:shower-head'
  
  class GuestRoom(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name              = 'Guest Room'
      self.room_short_name        = 'GR'
      self.num_of_xiaomi_button   = 2
      self.num_of_lamps           = 1
  
      # automatiom
      self.cfg_scene              = True
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      self.cfg_custom_scene       = False
      self.cfg_auto_curtain_ctl   = True
      self.cfg_adaptive_lighting  = True
  
      self.manual_added_automations = [ "automation.l_od_tai_s_desk_light_on_if_people_present_sits_in_the_chair",
                                        "automation.l_od_tai_s_desk_light_off_if_person_left_the_chair",
                                        ]
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
      self.add_device('sonoff_1001e49dd9_1',              self.room_name + ' Desk Screen LED', 'Switch',           'Generic Switch')
      self.add_device("582d343483e9",                     self.room_name + ' Unsmoothed',      'Temperature Sensor', "Qingping Temperature Sensor")
      self.add_smooth_temperature_sensor(     sensor_in= f'sensor.{self.room_entity}_unsmoothed_temperature_sensor',
                                              sensor_out=f'sensor.{self.room_entity}_temperature_sensor', )
  
      self.add_device('0x00158d00047b69d2',               self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)')#, flex_switch=True)
      self.add_device("lemesh_cn_1005553423_wy0c09_s_2",  self.room_name + " Ceiling Light", 'Light',              "Generic Light")
      self.add_device("50ec50ded70f_light",               self.room_name + " Lamp 1",        'Light',              "Generic Light")
      self.add_device("hue_ambiance_lamp_3",              self.room_name + " Lamp 2",        'Light',              "Generic Light")
      self.add_device("50ec50dd67be_light",               self.room_name + " Lamp 3",        'Light',              "Generic Light")
      #self.add_device("yeelink_cn_1040743458_mbulb3_s_2", self.room_name + " Lamp 4",        'Light',              "Generic Light")
      self.add_group('light', 'Guest Room Lamp',     ["light.guest_room_lamp_1",
                                                      "light.guest_room_lamp_2",
                                                      "light.guest_room_lamp_3",
                                                      #"light.guest_room_lamp_4",
                                                      ])
      self.add_device('18c23c27fc55',       self.room_name + ' Entrance',      'Motion Sensor',      'Mijia Motion Sensor 2')
      self.add_device("linp_cn_blt_3_1o91vfk5s4402_es5b",  self.room_name + ' Bed Xiaomi Home',  'Motion Sensor',      "Linptech Occupancy Sensor ES5", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
  
      #self.add_device("dced8308f596",       self.room_name,                    'Motion Sensor',      "Ziqing Occupancy Sensor")
      #self.add_device('e0798dba9ae1',       self.room_name + ' Bed',           'Motion Sensor',      'Mijia Motion Sensor 2')
      #self.add_device("a4c1387f7df0",       self.room_name + ' Bed',           'Motion Sensor',      "Linptech Occupancy Sensor ES3")
      #self.add_device("linp_cn_blt_3_1kenln2kkk800_es2",     self.room_name + ' Bed Xiaomi Home',      'Motion Sensor',      "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      #self.add_device("xiaomi_cn_blt_3_1kfc93o04kc00_03",    self.room_name + ' Desk Xiaomi Home',     'Motion Sensor',      "Xiaomi Occupancy Sensor", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
  
      self.add_device('va1049826304',       self.room_name,                    'Raditor',            'Tado Homekit')
      #self.add_device("curtain_1050",       self.room_name + " Curtain",       'Curtain',            "Generic Curtain")
  
      # This Ziqing Occupancy Sensor is Out of Order
      #self.add_device("dced8309090d",       self.room_name,                    'Motion Sensor',      "Ziqing Occupancy Sensor")
      #self.add_device('18c23c25a26c',       self.room_name,                    'Button',             'MiJia Wireless Switch 2', postfix='1')
      #self.add_device('18c23c246426',       self.room_name,                    'Button',             'MiJia Wireless Switch 2', postfix='1')
      #self.add_device('18c23c2826fc',       self.room_name,                    'Button',             'MiJia Wireless Switch 2', postfix='2')
  
    def get_cover_entities(self):
      super().get_cover_entities()
      # Cover entities
      self.curtains               = [ "cover.guest_room_curtain"]
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.all_motion_sensors = [
        f"binary_sensor.{self.room_entity}_entrance_motion_sensor_motion",
      ] + [] \
        + ([f"binary_sensor.{self.room_entity}_bed_xiaomi_home_occupancy_sensor_occupancy"] if self.xiaomi_home_occupancy else []) \
        #+ ([f"binary_sensor.{self.room_entity}_bed_occupancy_sensor_occupancy"]             if self.gateway_occupancy     else [])
  
      self.occupancy_override_default_timeout = '03:00:00'
  
      self.inside_to_outside_timeout = 2*60
      self.sleep_to_outside_timeout  = 5*60
      self.inside_to_sleep_timeout   = 30*60
  
    def get_tv_entities(self):
      super().get_tv_entities()
      self.media_players            = [f"media_player.xiaomi_lx5a_a862_play_control"]
  
    def get_remote_entities(self):
      super().get_remote_entities()
      # button states do not work well (not responsive) with template sensor renaming
      # and directly using button sensor is much responsive
      self.eight_key_knob_buttons  = ['sensor.ca6e1b6a8f89_action']
  
  
    def get_light_entities(self):
      super().get_light_entities()
      # Light/Switch entities
      self.leds                    = ["light.guest_room_desk_screen_led"]
      self.lamps                   = ["light.guest_room_lamp"]
      self.lights                  = self.leds + self.lamps + self.ceiling_lights
  
      # Adaptive lighting
      self.al_light_list[0]["lights"] += self.ceiling_lights + self.lamps
      self.al_light_list[0]["sleep_brightness"]  = 1
      self.al_light_list[0]["max_color_temp"]    = 6500
      self.al_light_list[0]["min_brightness"]    = 100  # Kids room should be as bright as possible
  
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'guest-room'
      self.dashboard_view_name = 'guest-room'
      self.room_icon           = 'mdi:bed-queen-outline'
  
  class GuestToilet(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'Guest Toilet'
      self.room_short_name       = 'GT'
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      self.cfg_scene              = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_adaptive_lighting  = True
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.all_motion_sensors = [
        "binary_sensor.guest_toilet_entrance_motion_sensor_motion",
        "binary_sensor.guest_toilet_shower_motion_sensor_motion",
      ]
  
    def get_light_entities(self):
      super().get_light_entities()
      # Light/Switch entities
      self.leds                    = ["switch.guest_toilet_floor_led"]
      self.lamps                   = [f"switch.{self.room_entity}_mirror_led"]
      self.lights                  = self.leds + self.lamps + self.ceiling_lights
      self.extractor               = ['switch.' + self.room_entity + '_extractor']
  
      # Adaptive lighting
      self.al_light_list[0]["lights"] += self.ceiling_lights
      self.al_light_list[0]["sleep_brightness"]  = 1
      self.al_light_list[0]["min_brightness"]    = 100   # This toilet is too dark, make it as bright as possible
  
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
      #self.add_device("a4c1387a7b78",                       self.room_name,                'Temperature Sensor', "Mijia2 Temperature Sensor", enable_humidity_sensor=True)
      self.add_device("xiaomi_cn_blt_3_1oquokb4c4000_mini", self.room_name,                'Temperature Sensor', "Mijia3 Temperature Sensor 3 Mini", integration='Xiaomi Home', enable_shower_sensor=True)
  
      self.add_device('0x00158d000487851a',             self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)')
      self.add_device("0x00158d000487851a_channel_2",   self.room_name + " Floor LED",     'Wall Switch',        "Generic Switch")
      self.add_device("guest_toilet_ceiling_light_hue", self.room_name + " Ceiling Light", 'Light',              "Generic Light")
      self.add_device('0x00158d0008d94c10',             self.room_name + ' Extractor',     'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', switch_rename_dir={1: 'Guest Toilet Extractor'})
      self.add_device('54ef44e3237b',                   self.room_name + ' Shower',        'Motion Sensor',      'Mijia Motion Sensor 2')
      self.add_device('e0798dba988e',                   self.room_name + ' Entrance',      'Motion Sensor',      'Mijia Motion Sensor 2')
      #self.add_device('0x00158d00052b35f7',             self.room_name,                    'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Xiaomi Home')
  
      self.add_device('0x04cf8cdf3c7cafdc',             self.room_name + ' Mirror Sensor', 'Light Sensor',       'Xiaomi Light Detection Sensor To Mirror Sensor')
      self.add_device('va0781390848',                   self.room_name,                    'Raditor',            'Tado Homekit')
      self.add_device("switchbot_finger_robot",         self.room_name + " Air Refresher", 'Button',             "Generic Button")
  
      self.add_device('adp_cn_1206102799_adfbt6_switch_a_p_3_1',            self.room_name + ' Mirror LED',            'Switch',             'Generic Switch')
      self.add_device('adp_cn_1206102799_adfbt6_switch_b_p_3_2',            self.room_name + ' Mirror Demister',       'Switch',             'Generic Switch')
      self.add_device('adp_cn_1206102799_adfbt6_battery_percentage_p_3_15', self.room_name + ' Mirror Robot Battery',  'Battery',            'Generic Battery')
      self.add_device('lumi_cn_blt_3_1ormnfq250400_mcn001',                 self.room_name + ' Mirror',                'Button',             'MiJia Wireless Switch 2', integration='Xiaomi Home')
  
  
      #self.add_device('sonoff_10020aa912_1',        self.room_name + ' Screen Light',   'Switch',             'Generic Switch')
  
      # guest toilet mirrormirror sensor    a4c138cfc701
      #    - en-suite toilet mirror
  
  #('0x00158d00052b35f7', 'Guest Toilet',               'Aqara Motion and Illuminance Sensor')
  #('0x00158d00053e96ae', 'Guest Toilet',               'Aqara Door & Window Sensor')
  
    def get_mirror_entities(self):
      super().get_mirror_entities()
      self.mirror_sensors          = [f"switch.{self.room_entity}_mirror_led"]
      self.demisters               = [f"switch.{self.room_entity}_mirror_demister"]
  
    def gen_button_automations(self):
      super().gen_button_automations()
  
      self.automation_list += [{
          "alias" : "ZLB-" + self.automation_room_name + "Mirror Button Control" + "-" + self.room_name,
          "configured": self.cfg_remote_light,
          "trigger":
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_mirror_button_single_click", 'to': 'on', "id": self.TOGGLE_LAMP_0     }]) if len(self.lamps)     > 0 else []) + \
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_mirror_button_double_click", 'to': 'on', "id": self.TOGGLE_LEDS       }]) if len(self.leds)      > 0 else []) + \
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_mirror_button_long_press",   'to': 'on', "id": self.TOGGLE_DEMISTER   }]) if len(self.demisters) > 0 else []) + \
            ([]),
          "mode":"queued", # this has to be queued to make sure no button press is ignored
          "action": self.get_trigger_action_list()
      }]
  
  
    # Guest Toilet - Left key - Ceiling light
    # Guest Toilet - Right key - Floor LED
    def gen_wall_button_single_automations(self):
      self.gen_a_button_toggle_automation(      button_state_list=["single_left", 'button_1_single'],
                                                button_state_name='Single Left',
                                                device_list=self.ceiling_lights,
                                                device_name='Ceiling Light')
  
      #self.gen_a_button_toggle_automation(      button_state_list=["single_right"],
      #                                          button_state_name='Single Right',
      #                                          device_list=self.leds,
      #                                          device_name='Floor LEDs')
  
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'guest-room'
      self.dashboard_view_name = 'guest-toilet'
      self.room_icon           = 'mdi:shower'
  
  class Study(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'Study'
      self.room_short_name       = 'ST'
      self.num_of_xiaomi_button  = 0
      self.num_of_lamps          = 0
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      self.cfg_scene              = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_auto_curtain_ctl   = True
      self.cfg_adaptive_lighting  = True
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.all_motion_sensors = [
        "binary_sensor.study_motion_sensor_motion",
        "binary_sensor.study_desk_motion_sensor_motion"
      ]
  
      self.occupancy_override_default_timeout = '03:00:00'
  
  
    def get_cover_entities(self):
      super().get_cover_entities()
      # Cover entities
      self.curtains            = [ "cover.study_blind"]
  
    def get_remote_entities(self):
      super().get_remote_entities()
      # N.B. Xiaomi zigbee button rename using template does not sample very well
      # Use manual rename on the native entity itself
      self.curtain_buttons = ["sensor.study_curtain_button"]
      self.desk_buttons =    ['sensor.study_desk_button']
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'lovelace-misc'
      self.dashboard_view_name = 'study'
      self.room_icon           = 'mdi:desk'
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
  
      #self.add_device("a4c138cfc701",               self.room_name,                     'Temperature Sensor', "Mijia2 Temperature Sensor")
      #self.add_device("582d34828cc1",               self.room_name,                     'Temperature Sensor', "Qingping Lite Temperature Sensor")
      #self.add_device("2ab7",                       self.room_name,                     'Temperature Sensor', "Mijia2 Temperature Clock",  integration='Passive BLE Monitor')
  
      self.add_device("xiaomi_cn_blt_3_1nu46s61t0g00_mini",      self.room_name,                    'Temperature Sensor', "Mijia3 Temperature Sensor 3 Mini", integration='Xiaomi Home')
  
      self.add_device('0x00158d00045245be',         self.room_name,                     'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', flex_switch=True)
      self.add_device("0x00158d00070b2f26",         self.room_name + ' Blind',          'Curtain',            "Aqara roller shade motor")
  
      #self.add_device("mss210_b083_outlet",         self.room_name + ' Studio Lamp 1',  'Switch',             "Generic Switch")
      self.add_device('lumi_cn_blt_3_1ev0s1bp0c400_mcn001',  self.room_name + ' Desk',     'Button',          'MiJia Wireless Switch 2', integration='Xiaomi Home')
  
  
      self.add_device('sonoff_10020aa912_1',        self.room_name + ' Screen Light',   'Switch',             'Generic Switch')
      #self.add_device('0x00158d000171756e_power',   'Feeding Bottle Warmer',            'Power',              'Generic Power Measurement Switch', power_on_threshold=1.5)
      #self.add_device("0x00158d000171756e_plug",    'Feeding Bottle Warmer',            'Switch',             "Generic Switch")
      #self.add_device("sonoff_1001e49ade_1",        self.room_name + ' Gateway Power',  'Switch',             "Generic Switch")
      self.add_device("sonoff_10020a8ba4_1",        self.room_name + ' Gateway Power 2','Switch',             "Generic Switch")
      self.add_device('0x00158d00054a6eb9',         self.room_name ,                    'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
      self.add_device('18c23c26ea40',               self.room_name + ' Desk',           'Motion Sensor',      'Mijia Motion Sensor 2')
      self.add_device('va4136768512',               self.room_name,                     'Raditor',            'Tado Homekit')
      #self.add_device("1740106002071949312_light",  self.room_name + ' Ceiling Light',  'Light',              "Generic Light")
      self.add_device("e14w_1_tuya",                self.room_name + ' Lamp 1',         'Light',              "Generic Light")
      self.add_device("e14w_2_tuya",                self.room_name + ' Lamp 2',         'Light',              "Generic Light")
      self.add_device("50ec50df0a79_light",         self.room_name + ' Lamp 3',         'Light',              "Generic Light")
      self.add_automation('light.e14w_1_tuya', 'E14W_1', "Wifi Device Reconnect When Unavailable", unavailable_period='00:02:00', unavailable_device_id='b1eb8398e1689392f398854c65d5bb37')
      self.add_automation('light.e14w_2_tuya', 'E14W_2', "Wifi Device Reconnect When Unavailable", unavailable_period='00:02:00', unavailable_device_id='0aa94946c833610ac68d26fbf53c20fe')
  
  
  
    def get_light_entities(self):
      super().get_light_entities()
      self.lamps                   = ["light.study_lamp_1",
                                      "light.study_lamp_2",
                                      "light.study_lamp_3",
                                     ]
      self.add_group('light', 'Study Lamp', self.lamps)
      self.ceiling_lights         = ["light.ccb5d1ab99bd_light",
                                     "light.ccb5d1ab3f31_light",
                                     "light.ccb5d1ab63f6_light",
                                     ]
      self.add_group('light', 'Study Ceiling Light', self.ceiling_lights)
      self.leds                    = ["switch.study_screen_light"]
      self.lights                  = self.leds + self.lamps + self.ceiling_lights
  
      # Adaptive lighting
      if self.cfg_adaptive_lighting:
        self.al_light_list[0]["lights"] += self.ceiling_lights + self.lamps
        self.al_light_list[0]["sleep_brightness"]  = 1
        self.al_light_list[0]["max_color_temp"] = 6500
  
  
    def gen_button_automations(self):
      super().gen_button_automations()
  
      self.automation_list += [{
          "alias" : "ZLB-" + self.automation_room_name + " Button Light Control" + "-" + self.room_name,
          "configured": self.cfg_remote_light,
          "trigger":
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_desk_button_single_click", 'to': 'on', "id": self.TOGGLE_LEDS           }]) if len(self.leds)           > 0 else []) + \
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_desk_button_double_click", 'to': 'on', "id": self.TOGGLE_CEILING_LIGHTS }]) if len(self.ceiling_lights) > 0 else []) + \
            (([{"platform": "state",  "entity_id": f"binary_sensor.{self.room_entity}_desk_button_long_press",   'to': 'on', "id": self.TOGGLE_CURTAINS       }]) if len(self.curtains)       > 0 else []) + \
            ([]),
          "mode":"queued", # this has to be queued to make sure no button press is ignored
          "action": self.get_trigger_action_list()
      }]
  
  
    def gen_room_specific_automations(self):
  #    self.add_offline_device_automations(
  #      device_type          = 'Zigbee',
  #      offline_device       = 'binary_sensor.en_suite_toilet_motion_sensor_motion',
  #      gateway_power_switch = 'switch.study_gateway_power',
  #      tts_message          = self.automation_room_name + "1F gateway 1 zigbee devices are offline. Restarting gateway."
  #      )
  
      self.add_offline_device_automations(
        device_type          = 'Zigbee',
        offline_device       = 'switch.study_wall_switch',
        gateway_power_switch = 'switch.study_gateway_power_2',
        tts_message          = self.automation_room_name + "1F gateway 2 zigbee devices are offline. Restarting gateway."
        )
  
      self.add_offline_device_automations(
        device_type          = 'Wifi',
        offline_device       = 'light.master_room_drawer_led',
        tts_message          = self.automation_room_name + "1F wifi devices are offline. You may want to manual restart 2.4Ghz Wifi."
        )
  
  
  class Corridor(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name              = 'Corridor'
      self.room_short_name        = 'CR'
      self.cfg_motion_light       = True
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_temp_control       = True
      self.cfg_remote_light       = True
      self.cfg_adaptive_lighting  = True
      self.manual_added_automations = [ #'automation.l_gc_corridor_lights_on_if_people_present',
                                        #'automation.l_gc_ground_corridor_lights_off_if_no_person_for_2_min',
                                        "automation.h_downstairs_zone_heating_off_when_no_heating_required",
                                        "automation.h_downstairs_zone_heating_on_when_heating_required",
                                        "automation.h_upstairs_zone_heating_off_when_no_heating_required",
                                        "automation.h_upstairs_zone_heating_on_when_heating_required",
                                        'automation.h_workaround_upstairs_downstair_zone_heating_off_when_no_heating_required',
                                        'automation.h_workaround_upstairs_downstair_zone_heating_on_when_heating_required',
                                        ]
  
    def get_room_name_and_property(self):
      super().get_room_name_and_property()
      self.room_type              = 'landing'
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
  
    def get_tv_entities(self):
      super().get_tv_entities()
      self.media_players            = [f"media_player.first_corridor_sonos"]
  
    def get_window_entities(self):
      super().get_window_entities()
      self.windows                 = [f"binary_sensor.front_door",
                                      ]
      self.timeout_windows         = self.windows
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.all_motion_sensors = [
        "binary_sensor.ground_corridor_xiaomi_home_occupancy_sensor_occupancy",
        "binary_sensor.ground_corridor_motion_sensor_motion_1",
        "binary_sensor.ground_corridor_motion_sensor_motion_2",
        "binary_sensor.first_corridor_motion_sensor_motion_1",
        "binary_sensor.first_corridor_motion_sensor_motion_2",
        "binary_sensor.en_suite_room_entrance_motion_sensor_motion",
        "binary_sensor.living_room_entrance_motion_sensor_motion",
        "binary_sensor.master_room_entrance_motion_sensor_motion"
      ]
  
      self.occupancy_override_default_timeout = '03:00:00'
  
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
  
      self.add_device('front_door_battery',           "Front Doorbell Ring Battery",  'Battery',       'Generic Battery')
      #self.add_device('50ec50ded70f',                 'First Corridor BLE Light',     'Light',         'Mijia BLE Lights')
      self.add_device('msl120_0a57_lightbulb',        'First Corridor Light',         'Light',         'Generic Light')
      self.add_device('50ec50df9323',                 'Ground Corridor Light',        'Light',         'Mijia BLE Lights')
      self.add_device('0x00158d0004667569',           'Ground Corridor',              'Motion Sensor', 'Aqara Motion and Illuminance Sensor', postfix='1')
      self.add_device('0x00158d00045019fd',           'Ground Corridor',              'Motion Sensor', 'Aqara Motion and Illuminance Sensor', postfix='2')
      self.add_device("a4c138961632",                      'Ground Corridor',                 'Motion Sensor',      "Linptech Occupancy Sensor ES3")
      self.add_device("linp_cn_blt_3_1kfc872k0k800_es2",   'Ground Corridor Xiaomi Home',     'Motion Sensor',      "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
  
  
      self.add_device('0x00158d0004525183',           'First Corridor',               'Motion Sensor', 'Aqara Motion and Illuminance Sensor', postfix='1')
      self.add_device('e0798dba9ae1',                 'First Corridor',               'Motion Sensor', 'Mijia Motion Sensor 2',               postfix='2')
  
  
      self.add_device('0x00158d00048783e5',           'Ground Corridor',              'Wall Switch',   'Aqara D1 Wall Switch (With Neutral, Double Rocker)', flex_switch=[1])
      self.add_device('0x00158d0005210fcf',           'First Corridor',               'Wall Switch',   'Aqara D1 Wall Switch (With Neutral, Double Rocker)')#, flex_switch=[2])
      self.add_device('0x00158d0005227632_channel_1', 'Downstairs Heating',           'Switch',        'Generic Switch')
      self.add_device('0x00158d0005227632_channel_2', 'Water Heater',                 'Switch',        'Generic Switch')
      self.add_device('0x00158d0008cb1681_switch',    'Upstairs Heating',             'Switch',        'Generic Switch')
      self.add_device('va0395514880',                 self.room_name,                 'Raditor',       'Tado Homekit')
  
    def get_light_entities(self):
      super().get_light_entities()
      self.ceiling_lights = ["light.first_corridor_light",
                             "light.ground_corridor_light",
                            ]
      self.add_group('light', 'Corridor Ceiling Light',  self.ceiling_lights)
  
      # Adaptive lighting
      self.al_light_list = [deepcopy(self.al_light_list[0]), deepcopy(self.al_light_list[0])]
      self.al_light_list[0]["name"]             = 'Corridor Ground Floor'
      self.al_light_list[0]["lights"]           = ["light.ground_corridor_light"]
      self.al_light_list[1]["name"]             = 'Corridor First Floor'
      self.al_light_list[1]["lights"]           = ["light.first_corridor_light"]
      self.al_light_list[1]["sleep_brightness"] = 5
  
      self.al_sleep_mode   = ['switch.adaptive_lighting_sleep_mode_corridor_first_floor',
                              'switch.adaptive_lighting_sleep_mode_corridor_ground_floor']
  
  
    def get_remote_entities(self):
      super().get_remote_entities()
      self.wall_buttons            = ["sensor.ground_corridor_wall_button",
                                      "sensor.first_corridor_wall_button"]
      self.buttons                 = self.wall_buttons
  
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'lovelace-misc'
      self.dashboard_view_name = 'corridors'
      self.room_icon           = 'mdi:toilet'
  
    # Customize card information
    def getNavigationRoomCard (self):
      room_card = super().getNavigationRoomCard()
      # Add additional cards
      dashboard_view_helpers.prepend_navigation_status_cards(room_card, [
        self.getTemplateCard(
          icon       = "mdi:lock-open-variant-outline",
          icon_color = "red",
          condition_entity = 'lock.front_door',
          condition_state  = 'unlocked',
        )
      ] + [
        self.getTemplateCard(
          icon       = "mdi:home-floor-g",
          icon_color = "deep-orange",
          tap_action = 'more-info',
          condition_entity = 'switch.downstairs_heating'
        ),
      ] + [
        self.getTemplateCard(
          icon       = "mdi:home-floor-1",
          icon_color = "deep-orange",
          tap_action = 'more-info',
          condition_entity = 'switch.upstairs_heating'
        ),
      ])
  
      return room_card
  
  
  
  class GroundToilet(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'Ground Toilet'
      self.room_short_name       = '0T'
      self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      self.cfg_scene              = True
      self.cfg_motion_light       = True
      self.cfg_remote_light       = True
      self.cfg_adaptive_lighting  = True
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
  
      self.all_motion_sensors = ['binary_sensor.ground_toilet_entrance_motion_sensor_motion'
      ] + ([f"binary_sensor.{self.room_entity}_xiaomi_home_occupancy_sensor_occupancy"] if self.xiaomi_home_occupancy else []) \
        + ([f"binary_sensor.{self.room_entity}_occupancy_sensor_occupancy"]             if self.gateway_occupancy     else [])
  
      self.inside_to_outside_timeout = 1*30 # 30s timeout for Linptech ES3 which has very accurate motion detection, to avoid false trigger when people are just sitting still for a while
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
      self.add_device("a4c1387c09bd",                    self.room_name,                                'Temperature Sensor', "Mijia2 Temperature Sensor")
      self.add_device("a4c1385ab801",                    self.room_name,                                'Motion Sensor',      "Linptech Occupancy Sensor ES3")
      self.add_device("linp_cn_blt_3_1kas24de8ck00_es2", self.room_name + ' Xiaomi Home',               'Motion Sensor',      "Linptech Occupancy Sensor ES3", integration='Xiaomi Home') # xiaomi home has more accurate states than gw3
      self.add_device("54ef44e58345",                    self.room_name + ' Entrance',                  'Motion Sensor',      "Mijia Motion Sensor 2")
  
  
      #self.add_device('0x00158d0004667569',              self.room_name,                                'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
      self.add_device("0x00158d0005435643",              self.room_name,                                'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Double Rocker)")
    # self.add_device('0x00158d00053fdaa8',              self.room_name + ' Door',                      'Door',               'Aqara Door & Window Sensor')
    # self.add_device("0x90fd9ffffe8e24b6",              self.room_name + " Ceiling Light Spotlight 1", 'Light',              "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum", integration='Z2M')
    # self.add_device("0x000b57fffee8e6b4",              self.room_name + " Ceiling Light Spotlight 2", 'Light',              "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum", integration='Z2M')
      self.add_device("ground_toilet_ceiling_light_hue", self.room_name + " Ceiling Light",             'Light',              "Generic Light")
      self.add_device('va2241008640',                    self.room_name,                                'Raditor',            'Tado Homekit')
  
  
    def get_light_entities(self):
      super().get_light_entities()
      # Light/Switch entities
      # Adaptive lighting
      self.al_light_list[0]["lights"] += self.ceiling_lights
      self.al_light_list[0]["sleep_brightness"]  = 15
  
  #  def gen_wall_button_single_automations(self):
  #    self.gen_a_button_toggle_automation( button_state_list=[ "1", "single", "single_left", "single_right", "single_center",
  #                                                            "button_1_single", "button_2_single", "button_3_single"],
  #                                         button_state_name='Single',
  #                                         device_list=['switch.ground_toilet_wall_switch_1'],
  #                                         device_name='Wall Switch',
  #                                         )
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'lovelace-misc'
      self.dashboard_view_name = 'corridors'
      self.room_icon           = 'mdi:toilet'
  
  class WholeHome(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'Whole Home'
      self.room_short_name       = 'WH'
      self.cfg_occupancy          = True
  
    def get_motion_sensor_entities(self):
      super().get_motion_sensor_entities()
      self.all_motion_sensors = [
        "group.living_room_motion_group",
        #"group.garden_motion",
        "group.kitchen_motion_group",
        "group.corridor_motion_group",
        "group.study_motion_group",
        "group.ground_toilet_motion_group",
        "group.master_room_motion_group",
        "group.master_toilet_motion_group",
        "group.en_suite_room_motion_group",
        "group.en_suite_toilet_motion_group",
        "group.guest_room_motion_group",
        "group.guest_toilet_motion_group"
      ]
  
  class System(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'System'
      self.room_short_name       = 'SY'
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'lovelace-system'
      self.dashboard_view_name = 'system'
      self.room_icon           = 'mdi:server'
  
    def writeConfig(self):
      # Don't allow system to render a package config
      pass
  
    # Customize system card information
    def getNavigationRoomCard (self):
      card_type = 'mushroom'
  
      if card_type == 'mushroom':
         room_card = dashboard_view_helpers.navigation_status_room_card(
            dashboard_view_helpers.system_navigation_title_card(),
            self.getCardModColor("transparent"),
            dashboard_view_helpers.system_navigation_status_cards(
              self.getTemplateCard,
            )
         )
  
      elif card_type == 'button':
        room_card = dashboard_view_helpers.button_navigation_room_card(
          self.room_name,
          self.room_icon,
          self.dashboard_view_path,
        )
  
      return self.getRestricedAccess('us', room_card)
  
  
  #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  #
  #    HOME in China
  #
  #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  class CN_MasterRoom(RoomBase):
    def get_room_config(self):
      super().get_room_config()
      self.room_name             = 'Master Room'
      self.room_short_name       = 'MR'
      #self.num_of_xiaomi_button  = 3
      self.num_of_lamps          = 2
      # Enables
      self.cfg_scene              = True
      #self.cfg_occupancy          = True
      self.cfg_group_auto         = True
      #self.cfg_motion_light       = True
      #self.cfg_remote_light       = True
      self.cfg_temp_control       = True
      self.cfg_temp_calibration   = True
      #self.cfg_scene_color_led   = True
      self.cfg_scene_color_lamp  = True
      #self.cfg_custom_scene       = True
      #self.cfg_motion_bed_led     = True
      #self.cfg_auto_curtain_ctl   = True
      self.cfg_adaptive_lighting  = True
  
    def get_entity_declarations(self):
      super().get_entity_declarations()
    # self.add_device('0x54ef441000792d09',                self.room_name + ' Bed',                 'Pressure Sensor',    'Aqara Pressure Sensor')
    # self.add_device('e4aaec755efa',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='1')
    # self.add_device('e4aaec755f4b',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='2')
  
    def get_light_entities(self):
      super().get_light_entities()
  
      # Adaptive lighting
      if self.cfg_adaptive_lighting:
        self.al_light_list[0]["lights"] += self.lights
  
  
    def get_tv_entities(self):
      super().get_tv_entities()
      #self.tvs                     = [f"media_player.{self.room_entity}_tv"]
      #self.tv_picture_mode         = [f"input_select.{self.room_entity}_tv_picture_mode"]
  
    def getDashboardSettings(self):
      super().getDashboardSettings()
      self.dashboard_default_root = 'master-room'
      self.dashboard_view_name    = 'master-room'
      self.room_icon              = 'mdi:bed-king-outline'
      #self.room_theme             = 'ios-dark-mode-dark-green'
  
  

  return {
    "MasterRoom": MasterRoom,
    "MasterToilet": MasterToilet,
    "Kitchen": Kitchen,
    "LivingRoom": LivingRoom,
    "Garden": Garden,
    "EnSuiteRoom": EnSuiteRoom,
    "EnSuiteToilet": EnSuiteToilet,
    "GuestRoom": GuestRoom,
    "GuestToilet": GuestToilet,
    "Study": Study,
    "Corridor": Corridor,
    "GroundToilet": GroundToilet,
    "WholeHome": WholeHome,
    "System": System,
    "CN_MasterRoom": CN_MasterRoom,
  }
