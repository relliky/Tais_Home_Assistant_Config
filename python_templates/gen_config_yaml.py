#!/usr/bin/env python3

#####################################################################
# This script won't update En-suite Room/Toilet configurations
# It is intentional to stop breaking automations in tenant room. 
#####################################################################

from HA_Composite_Card_Lib.src.main import HA_Composite_Card_Lib 
import re
import yaml
import os
import json
import copy
import argparse
#from HA_Composite_Card_Lib import HA_Composite_Card_Lib as self.hccl
#from translate import Translator
#global translator 
#translator = Translator(to_lang="zh")

# Set home
home = 'CN'
#home = UK

##################################################################
#  Room Yaml Configurations
##################################################################

class RoomBase:
  def __init__ (self, dashboard_type=None, dashboard_language='English'):
    #cc = self.hccl()
    #self.translation = translator.translate("This is a pen.")
    #print (self.translation)

    self.hccl = HA_Composite_Card_Lib()
    # Create Empty JSON Database
    self.reset_json_environment()
    
    # Name and basic configs
    self.get_room_config()
    self.get_room_name_and_property()
    
    self.info ("Generating " + self.room_name + " Yaml Package")

    # Entities
    self.get_time_entities()
    self.get_motion_sensor_entities()
    self.get_remote_entities()
    self.get_wall_switches()
    self.get_light_entities()
    self.get_mirror_sensor_entities()
    self.get_lighting_control_entities()
    self.get_tv_entities()
    self.get_time_setup()
    self.get_cover_entities()
    self.get_window_entities()
    self.get_temperature_control_entities()
    self.get_post_room_config()

    # Populate entities into database
    self.get_entity_declarations()
    self.get_automation_declarations()
    self.populate_entities_into_database()

    # Remove disabled entities
    self.remove_disabed_entities()
    # Generate user control group including automations and other controls
    self.get_automation_group_declarations()

    # Get dashboard settings
    self.dashboard_type = dashboard_type
    #self.dashboard_language = dashboard_language
    #print (self.dashboard_language) 
    self.getDashboardSettings()
    self.dashboard_root = self.dashboard_default_root if dashboard_type == 'default' else \
                          'dashboard-tablet'          if dashboard_type == 'tablet'  else \
                          'dashboard-mobile'          if dashboard_type == 'mobile'  else \
                          'uninitialized_dashboard_root'
    # Render config
    self.writeConfig()

  def get_room_config(self):  
    # Room configuration                    
    self.room_entity           = False
    self.num_of_xiaomi_button  = 0
    self.num_of_lamps          = 0
    # Basic Enables
    self.cfg_scene              = False            
    self.cfg_occupancy          = False        
    self.cfg_group_auto         = False       
    self.cfg_motion_light       = False
    self.cfg_remote_light       = False
    self.cfg_temp_control       = False
    self.cfg_temp_calibration   = False

    # Adavanced Enables
    self.cfg_scene_color_led   = False
    self.cfg_scene_color_lamp  = False
    self.cfg_custom_scene       = False
    self.cfg_led_only_scene     = False
    self.cfg_motion_bed_led     = False
    self.cfg_auto_curtain_ctl   = False
    self.cfg_adaptive_lighting  = False
    
    # Automatically loaded by settings later
    self.cfg_flex_switch       = False
    self.room_entity           = 'uninitialized_room_entity'
    self.room_name             = 'Uninitialized_room_name'    
    self.room_short_name       = 'uninitialized_room_short_name'

  def error(self, msg):
        raise TypeError( "\n" +\
                         "###################################################################################\n" + \
                         msg + "\n" + \
                         "###################################################################################\n")

  def warn(self, str):
      warnings.warn("\n" +\
          "-----------------------------------------------------\n" + \
          str + "\n" + \
          "-----------------------------------------------------\n")

  def info(self, str):
      print(str)

  def get_time_entities(self):
    self.end_of_sleep_time   = '06:30:00'
    self.start_of_sleep_time = '23:00:00'

  def get_room_name_and_property(self):  
    self.room_entity          = self.getIDFromName(self.room_name)
    self.room_navi_path       = self.room_entity.replace("_", "-")
    self.automation_room_name = self.room_short_name + " " 

    self.room_type =  'bedroom'       if (('_room' in self.room_entity) and ('living_room' != self.room_entity)) else \
                      'toilet'        if '_toilet' in self.room_entity else \
                      'common_area'

    self.west_face_windows = True     if self.room_entity in ['en_suite_room', 'master_room', 'kitchen'] else False
    
  def get_motion_sensor_entities(self):  
    self.motion_group    = "group." + self.room_entity + "_motion_group"
    self.occupancy_group = "group." + self.room_entity + "_occupancy_group"


    # Motion sensor entities
    self.bed_motion_sensors      =  ["binary_sensor." + self.room_entity + "_bed_motion_sensor_motion"] if self.room_type == 'bedroom' else []
    self.non_bed_motion_sensors  =  []
    self.all_motion_sensors      =  ["uninitialized_all_motion_sensors"]
    self.entrance_motion_sensors =  ["binary_sensor." + self.room_entity + "_entrance_motion_sensor_motion"] if self.room_type == 'bedroom' else \
                                    [self.motion_group]

    self.room_occupancy          = "input_select."  + self.room_entity + "_occupancy"         
    self.sleep_time              = 'input_boolean.' + self.room_entity + '_sleep_time' if self.room_type == 'bedroom' else \
                                   'input_boolean.always_off_constant' 
    
    self.inside_to_outside_timeout = 1*60 if self.room_type == 'landing' else 5*60
    self.sleep_to_outside_timesout = 60*60
    self.inside_to_sleep_timeout   = 30*60 

    self.automation_occupancy = { "alias":"ZOc-" + self.automation_room_name + "Occupancy Update" + "-" + self.room_name}
    self.automation_occupancy['id'] = self.getIDFromAlias(self.automation_occupancy['alias'])


    self.occupancy_state_duration= 4 # Minutes
    self.occupancy_on_x_min_ratio_sensor  = "unitialized_ratio_sensor"
    self.occupancy_on_2x_min_ratio_sensor = "unitialized_ratio_sensor"

    # default to assume that no motion requires a longer timeout than immediately set the room occupancy to Outside
    self.turn_to_outside_when_no_motion = 'no'
    
  def get_remote_entities(self):  
    # Button (sensor) entities
    self.xiaomi_buttons          = []
    for i in range(self.num_of_xiaomi_button):
      self.xiaomi_buttons       += ["sensor." + self.room_entity + "_button"] 
      if self.num_of_xiaomi_button != 1:
        self.xiaomi_buttons[i]  += "_" + str(i+1)
    self.wall_buttons            = ["sensor." + self.room_entity + "_wall_button",
                                    "sensor." + self.room_entity + "_wall_button_2",] # sometimes the entity is duplicated and need _2 postfix
    self.buttons                 = self.wall_buttons + self.xiaomi_buttons
    self.curtain_buttons         = []
    self.six_key_buttons         = []
    self.four_key_buttons        = []
    self.eight_key_knob_buttons  = []

  def get_wall_switches(self):
    self.wall_switches          = []
    self.decouple_wall_switches = []
    self.raw_wall_switches      = []
    self.alias_wall_switches    = []

    
  def get_light_entities(self):
    # Light/Switch entities
    self.ceiling_lights          = ["light." + self.room_entity + "_ceiling_light"]
    self.lamps                   = []
    for i in range(self.num_of_lamps):
      self.lamps                += ["light." + self.room_entity + "_lamp"]
      if self.num_of_lamps != 1:
        self.lamps[i]           += "_" + str(i+1)
    self.leds                    = []
    self.lights                  = self.leds + self.lamps + self.ceiling_lights
    self.light_group             =  'group.' + self.room_entity + '_light_group'

    self.extractor               = []

    # Adaptive Light settings
    self.al_sleep_mode       = 'switch.adaptive_lighting_sleep_mode_'       + self.room_entity
    self.al_adapt_brightness = 'switch.adaptive_lighting_adapt_brightness_' + self.room_entity

    if self.cfg_adaptive_lighting == True:
      self.al_light_list += \
        [
          {
            "configured": True,
            "name": self.room_name,
            "lights": [],
            "prefer_rgb_color": False,
            "transition": 45,
            "initial_transition": 1,
            "interval": 90,
            "min_brightness": 50,
            "max_brightness": 100,
            "min_color_temp": 2700,
            "max_color_temp": 4000,
            "sleep_brightness": 20,
            "sleep_color_temp": 2200,
            #"sunrise_time": None,
            #"sunrise_offset": None,
            #"sunset_time": None,
            #"sunset_offset": None,
            "take_over_control": True, # Does not work, after update brightness manually on lovelace, it still applies adaptive lighting at each interval
            "autoreset_control_seconds": 86400,
            "detect_non_ha_changes": False,
            "only_once": False,
            "adapt_only_on_bare_turn_on": True,
            "separate_turn_on_commands": False, # Only setting it False will make "take_over_control" work. But adaptive on color transition may fail, such as living room lamps.
            "send_split_delay": 500, 
            "adapt_delay": 0.5,
            "intercept": True,
            "multi_light_intercept": True,
            "include_config_in_attributes": False
          }
        ]


  def get_mirror_sensor_entities(self):
    self.mirror_sensors          = []

  def get_lighting_control_entities(self):
    
    self.ceiling_light_control_when = {}
    self.ceiling_light_control_when['States when bright morning']   = "input_boolean.ceiling_light_control_" + "bright_morning_"   + self.room_entity
    self.ceiling_light_control_when['States when bright afternoon'] = "input_boolean.ceiling_light_control_" + "bright_afternoon_" + self.room_entity
    self.ceiling_light_control_when['States when dark']             = "input_boolean.ceiling_light_control_" + "dark_"             + self.room_entity

    self.lamp_control_when = {}
    self.lamp_control_when['States when bright morning']            = "input_boolean.lamp_control_" +          "bright_morning_"   + self.room_entity
    self.lamp_control_when['States when bright afternoon']          = "input_boolean.lamp_control_" +          "bright_afternoon_" + self.room_entity
    self.lamp_control_when['States when dark']                      = "input_boolean.lamp_control_" +          "dark_"             + self.room_entity
                
    self.led_control_when = {}                
    self.led_control_when['States when bright morning']             = "input_boolean.led_control_" +           "bright_morning_"   + self.room_entity
    self.led_control_when['States when bright afternoon']           = "input_boolean.led_control_" +           "bright_afternoon_" + self.room_entity
    self.led_control_when['States when dark']                       = "input_boolean.led_control_" +           "dark_"             + self.room_entity
      
    self.curtain_control_when = {}      
    self.curtain_control_when['States when left']                   = "input_boolean.curtain_control_" +      "when_left_"         + self.room_entity
    self.curtain_control_when['States when bright morning']         = "input_boolean.curtain_control_" +      "bright_morning_"    + self.room_entity
    self.curtain_control_when['States when bright afternoon']       = "input_boolean.curtain_control_" +      "bright_afternoon_"  + self.room_entity
    self.curtain_control_when['States when dark']                   = "input_boolean.curtain_control_" +      "dark_"              + self.room_entity

    self.morning_start_time    =  "input_datetime.morning_start_time_"   + self.room_entity
    self.morning_end_time      =  "input_datetime.morning_end_time_"     + self.room_entity
    self.afternoon_start_time  =  "input_datetime.afternoon_start_time_" + self.room_entity
    self.afternoon_end_time    =  "input_datetime.afternoon_end_time_"   + self.room_entity

    self.datetimes = [self.morning_start_time, 
                      self.morning_end_time,
                      self.afternoon_start_time,
                      self.afternoon_end_time,  
                      ]

  def getPostfix(self, entity):
    postfix = re.sub("^.*\.", "", entity)
    
    # This regex does not seem to work to capture special characters
    if re.search('[\./!"£$%^&*()]', postfix) != None:
      raise TypeError( "\n" +\
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                       "Postfix " + postfix + " still have specical characters $./!\"£$%^&*()" + "\n" + \
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
    return postfix

  def convertPostfixToName(self, postfix):
    return re.sub("_", " ", postfix)

  # match the beginning of the string or a space, followed by a non-space
  def captilizeSentence(self, s):
    return re.sub("(^|\s)(\S)", lambda m: m.group(1) + m.group(2).upper(), s)

  def getName(self, entity):
    postfix = self.getPostfix(entity)
    name    = self.convertPostfixToName(postfix)
    name    = self.captilizeSentence(name)
    return  name

  def get_tv_entities(self):
    self.tv_room_entity          = None
    self.tvs                     = []
    self.tv_picture_mode         = []
    self.tv_soundbars            = []
    self.fire_tvs                = []
      
  def get_time_setup(self):
    # Time setup
    self.daytime_lights_off_timeout   = "00:15:00"
    self.nighttime_lights_off_timeout = "02:00:00" if self.room_type == "bedroom" else \
                                        self.daytime_lights_off_timeout
    self.daytime_start                = "06:00:00"
    self.afternoon_start              = "13:00:00"
    self.daytime_end                  = "21:00:00"

  def get_cover_entities(self):
    # Cover entities
    self.curtains                      = []
    self.aqara_shutter_blind           = False
    self.curtain_group                 = 'group.' + self.room_entity + '_curtain_group'

    # Cover extra controls
#    self.light_in_daytime_postfix      = self.room_entity + "_light_in_daytime" 
#    self.light_in_daytime              = "input_boolean." + self.room_entity + "_light_in_daytime" 
#    self.curtain_in_nighttime_postfix = self.room_entity + "_curtain_in_nighttime" 
#    self.curtain_in_nighttime          = "input_boolean." + self.room_entity + "_curtain_in_nighttime" 


  def get_window_entities(self):
    self.windows                        = []
    self.window_group                   = 'group.' + self.room_entity + '_window_group'

  def get_temperature_control_entities(self):
    # Temperature sensor entities
    self.outside_temperature              = "sensor.met_office_cambridge_city_airport_temperature_3_hourly"
    self.room_default_temperature         = "input_number."    + self.room_entity + "_default_temperature" 
    self.thermostat                       = "climate."         + self.room_entity
    self.thermostat_schedule              = "switch.schedule_" + self.room_entity + "_temperature"
    self.temperature_sensor               = "sensor."          + self.room_entity + "_temperature_sensor"
    self.room_heating_override            = "input_boolean."   + self.room_entity + "_heating_override"
    
    # Getting heating required sensor
    self.template_list += [
      {
        "binary_sensor": [
          {
            "name": self.room_name + " Heating Required",
            "state":  '{% set climate = "climate.' + self.room_entity + '" %}'  + \
                      '{% if states(climate) == "unavailable" %}'               + \
                      'off'                                                     + \
                      '{% else %} '                                             + \
                        '{{ ((state_attr(climate, "temperature")  > state_attr(climate, "current_temperature"))  and  (states(climate) != "off"))  }}'  + \
                      '{% endif %}'                                           
                      
          }
        ],
        "configured": self.cfg_temp_control 
      }        
    ]    
    
  def get_post_room_config(self):

    # Scene 
    self.room_scene_ctl          = "input_select." + self.room_entity + "_scene"
    
    # Scene automation internal variable
    self.cur_scene           = 'unintialized_cur_scene'
    
    if self.cfg_group_auto:
      self.room_auto_gen_automations = "group." + self.room_entity + "_auto_gen_automations"

  def reset_json_environment(self):
    self.automations            = []
    self.entity_declarations    = {}
    self.input_select_dict      = {}
    self.sensor_list            = []
    self.group_dict             = {}
    self.input_boolean_dict     = {}
    self.input_datetime_dict    = {}
    self.script_dict            = {}
    self.switch_list            = []
    self.cover_list             = []
    self.template_list          = []
    self.binary_sensor_list     = []
    self.light_list             = []
    self.room_cards             = []
    self.views                  = []
    self.dashboard_type         = None
    self.header_card_list       = []
    self.main_card_list         = []
    self.tail_card_list         = []    
    self.al_light_list = []

  def get_occupancy_ratio_sensor_config(self, x_minutes_multiple_str):
    x_minutes_multiple =  1 if x_minutes_multiple_str == '1x' else \
                          2 if x_minutes_multiple_str == '2x' else \
                          0;  

    x_minutes_total = x_minutes_multiple * self.occupancy_state_duration
    sensor_name = self.room_name + " Motion On Ratio For Last " + str(x_minutes_total) +" Minutes"
    
    
    if   x_minutes_multiple == 1:
      self.occupancy_on_x_min_ratio_sensor = "sensor." + self.getIDFromName(sensor_name)
    elif x_minutes_multiple == 2:  
      self.occupancy_on_2x_min_ratio_sensor = "sensor." + self.getIDFromName(sensor_name)

    #print (self.room_name + " occupancy_on_x_min_ratio_sensor is " + self.occupancy_on_x_min_ratio_sensor)
    
    ratio_sensor_config = {
        "platform": "history_stats",
        "name": sensor_name,
        "entity_id": self.motion_group,
        "state": "on",
        "type": "ratio",
        "duration": {
          "minutes": str(x_minutes_total)
        },
        "end": "{{ (now() | as_timestamp) | as_datetime | as_local }}",
        "configured": self.cfg_occupancy
      }
    return ratio_sensor_config

#  def addEntityCard(self, entity, entity_name=None, entity_name_translation=None, 
#                          card_name=None, card_type=None,card_icon=None,card_icon_color=None,double_tab_action=None, card_group=None):
#
#
#    self.room_cards += [self.hccl.getEntityCard(entity=entity,
#                                          entity_name=entity_name,
#                                          entity_name_translation=entity_name_translation,
#                                          card_name=card_name,
#                                          card_type=card_type,
#                                          card_icon=card_icon,
#                                          card_icon_color=card_icon_color,
#                                          double_tab_action=double_tab_action
#                                         )]

  def add_mac_device(self, mac, name, comment, model, postfix=None, integration='Xiaomi Gateway 3', flex_switch=None, power_on_threshold=None, switch_rename_dir=None, light_wall_switch=True, belong_to_group=None):

    # Check if inputs are legal
    group = belong_to_group 
    if belong_to_group != None and type(belong_to_group) is not list: 
        raise TypeError( "\n" +\
           "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
           "Model " + model + " belong_to_group is not a list. Name = " + name + name_postfix + ', MAC Address:' + mac + ", Integration " + integration + "\n" + \
           "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

    name_postfix   = ' ' + postfix if postfix != None else ''

    # 0 padding mac address to 64-bit for Zigbee device
    if re.match("^0x[A-Fa-f0-9]*$", mac):
      mac_in_decimal = int(mac, 16) # convert hexadecimal to decimal
      mac = "0x{:0>16x}".format(mac_in_decimal) # format hexadecimal with 0 padding to 16 characters (64-bit)
    
    
    ###################################################################################################
    # Wall Switches
    #
    # Aqara D1 Wall Switch (With Neutral, Triple Rocker)  QBKG26LM  ZigbeeID: ["lumi.switch.n3acn3"]
    # Aqara D1 Wall Switch (With Neutral, Double Rocker)  QBKG24LM  ZigbeeID: ["lumi.switch.b2nacn02"]
    # Aqara D1 Wall Switch (With Neutral, Single Rocker)  QBKG23LM  ZigbeeID: ["lumi.switch.b1nacn02"]
    # Aqara Single Key Wired Wall Switch Without Neutral Wire QBKG04LM
    ###################################################################################################
    if((model == "Aqara D1 Wall Switch (With Neutral, Triple Rocker)"     ) or \
       (model == "Aqara D1 Wall Switch (With Neutral, Double Rocker)"     ) or \
       (model == "Aqara D1 Wall Switch (With Neutral, Single Rocker)"     ) or \
       (model == "Aqara Single Key Wired Wall Switch Without Neutral Wire")): 
      
      key_num = 0
      if   model == "Aqara D1 Wall Switch (With Neutral, Triple Rocker)": 
        key_num = 3
      elif model == "Aqara D1 Wall Switch (With Neutral, Double Rocker)": 
        key_num = 2
      elif model == "Aqara D1 Wall Switch (With Neutral, Single Rocker)": 
        key_num = 1
      elif model == "Aqara Single Key Wired Wall Switch Without Neutral Wire": 
        key_num = 1
      else:
        raise TypeError( "\n" +\
                         "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                         "Model " + model + " does not have a key_num. Name = " + name + name_postfix + ', MAC Address:' + mac + ", Integration " + integration + "\n" + \
                         "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

      # Wall Switches Per Each Physical Wall Switch
      for index in range(1,key_num+1):
        
        if integration == 'Xiaomi Gateway 3':
          # single switch is with different postfix
          i = '' if key_num == 1 else index
          alias_switch_name          = name + " Wall Switch " + str(i) + name_postfix
          raw_switch_entity          = "switch." + mac + ('_switch' if key_num == 1 else '_channel_' + str(i))
          raw_decouple_switch_entity = "switch." + mac + '_wireless' + ('' if key_num == 1 else  '_' + str(i))          
        elif integration == 'Z2M':
          i = index
          # Hack Z2M renamed devices to standard name
          postfix = ''          if key_num == 1            else \
                    '_left'     if i == 1                  else \
                    '_center'   if i == 2 and key_num == 3 else \
                    '_right'    if i == 3 and key_num == 3 or i == 2 and key_num == 2 else ''
                    
          alias_switch_name          = name + " Wall Switch " + str(i) + name_postfix
          raw_switch_entity          = "switch." + self.room_entity + '_wall_switch' + postfix
          raw_decouple_switch_entity = 'unintialized_raw_decouple_switch_entity'
        else:
          raise TypeError("\n" +\
                          "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                          "Model " + model + " does not support this integration. Name = " + name + name_postfix + ', MAC Address:' + mac + ", Integration " + integration + "\n" + \
                          "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
                
          
        self.switch_list += [
          {
            "platform": "group",
            "name": alias_switch_name,
            "entities": raw_switch_entity,
            "configured": True 
          }        
        ]

        #print (alias_switch_name + "      "  + str(index))
        # Rename switches based on switch rename
        if switch_rename_dir is not None and index in switch_rename_dir:
          self.switch_list += [
            {
              "platform": "group",
              "name": switch_rename_dir[index],
              "entities": raw_switch_entity,
              "configured": True 
            }        
          ]
        
        # added wall switches
        self.wall_switches          += [raw_switch_entity]
        self.decouple_wall_switches += [raw_decouple_switch_entity] if raw_decouple_switch_entity != 'unintialized_raw_decouple_switch_entity' else []
        
        # added Yeelight Flex automation
        if flex_switch != None:
          # Disable wall button single automation
          self.cfg_flex_switch = True
          
          # Generate flex automation instead
          if flex_switch is True:
            self.gen_flex_wall_switch_automations(flex_wall_switch_index=1, flex_wall_switch_entity=raw_switch_entity)
          else:
            for flex_switch_index_local in flex_switch:
              if flex_switch_index_local == i:
                self.gen_flex_wall_switch_automations(flex_wall_switch_index=i, flex_wall_switch_entity=raw_switch_entity)


        
      # Wall Buttons
      # Hack Z2M integration and no need to rename the devices for now
      if integration == 'Xiaomi Gateway 3':
        self.template_list += [
          {
            "sensor": [
              {
                "name": name + " Wall Button" + name_postfix,
                # Entity id starts with 0 so have to use a different format
                # https://community.home-assistant.io/t/error-in-template-i-am-missing-something/92464/3
                "state": '{{states.sensor["' + mac + '_action"].state}}'
              }
            ],
            "configured": True 
          }        
        ]
    ###################################################################################################
    # Contacts
    #
    # Aqara Door & Window Sensor, MCCGQ11LM ZigbeeID: ["lumi.sensor_magnet.aq2"]
    # Mijia2 Contact, MCCGQ02HL
    ###################################################################################################
    elif((model == "Aqara Door & Window Sensor"        and integration == 'Xiaomi Gateway 3') or \
         (model == "Mijia2 Contact"                    and integration == 'Xiaomi Gateway 3')): 
    
      #entity_name = name + name_postfix
      #if group != None:
      #    group += ["binary_sensor." + self.getIDFromName(entity_name)]
    
      self.binary_sensor_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "binary_sensor." + mac + '_contact',
          "configured": True 
        }        
      ]
   
    elif((model == "Aqara Pressure Sensor") or \
         (model == "Mijia2 Pressure Sensor")): 

      self.template_list += [
        {
          "binary_sensor": [
            {
              "name": name + " Pressure Sensor" + name_postfix,
              "state": '{% set state = states.binary_sensor["' + mac + '_contact"].state %} {% if state == "on"%} off {% elif state == "off"%} on {% else%} {{state}} {% endif %}'
            }
          ],
          "configured": True 
        }        
      ]      

    ###################################################################################################
    # Buttons
    # Aqara Wireless Switch,   WXKG11LM  ZigbeeID: ["lumi.sensor_switch.aq2"]       action_list:[]
    # MiJia Wireless Switch,   WXKG01LM  ZigbeeID: ["lumi.sensor_switch"]           action_list:['single', 'double', 'triple', 'quadruple', 'many','release', 'hold']                                                                              
    # MiJia Wireless Switch 2, ble XMWXKG01LM                                       action_list:['single', 'double', 'hold']         
    # Aqara Opple switch 3 bands, WXCJKG13LM, ZigbeeID: ["lumi.remote.b686opcn01"]  action_list:['button_1_single', 'button_2_single', 'button_3_single', 'button_4_single', 'button_5_single', 'button_6_single'] - more buttons for double/hold etc                                               
    ###################################################################################################
    elif((model == "Aqara Wireless Switch") or \
         (model == "MiJia Wireless Switch") or \
         (model == "Aqara Opple switch 3 bands") or \
         (model == "MiJia Wireless Switch 2")): 

      if model == "Aqara Opple switch 3 bands" and integration == 'Z2M':
        mac = mac + "_" + mac
        mac_postfix = '_action'
      else:
        mac_postfix = '_button_action' if integration == 'Z2M' else \
                      '_action'

      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Button" + name_postfix,
              "state": '{{states.sensor["' + mac + mac_postfix + '"].state}}'
            }
          ],
          "configured": True 
        }        
      ]
    ###################################################################################################
    # Light Sensors
    # Xiaomi Light Detection Sensor GZCGQ01LM ZigbeeID: ["lumi.sen_ill.mgl01"]
    # Xiaomi Light Detection Sensor To Mirror Sensor GZCGQ01LM ZigbeeID: ["lumi.sen_ill.mgl01"]
    ###################################################################################################
    elif((model == "Xiaomi Light Detection Sensor")): 

      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Light Sensor" + name_postfix,
              "state": '{{states.sensor["' + mac + '_illuminance"].state}}'
            }
          ],
          "configured": True 
        }        
      ]

    elif((model == "Xiaomi Light Detection Sensor To Mirror Sensor")): 

      self.template_list += [
        {
          "binary_sensor": [
            {
              "name": name + name_postfix,
              "state": '{{states.sensor["' + mac + '_illuminance"].state |int > 500 }}'
            }
          ],
          "configured": True 
        }        
      ]

    ###################################################################################################
    # Motion Sensors, Occupancy Sensor
    #
    # Aqara Motion and Illuminance Sensor, RTCGQ11LM ZigbeeID: ["lumi.sensor_motion.aq2"]
    # MiJia Human Body Movement Sensor, RTCGQ01LM
    # Mijia Motion Sensor 2,   RTCGQ02LM
    # Mijia Motion Sensor 2s,   RTCGQ02LM
    # Ziqing Occupancy Sensor, Mesh model: "mesh IZQ-24"
    ###################################################################################################
    elif((model == "Aqara Motion and Illuminance Sensor"                                           ) or \
         (model == "MiJia Human Body Movement Sensor"                                              ) or \
         (model == "Mijia Motion Sensor 2s"                   and integration == 'Xiaomi Gateway 3') or \
         (model == "Mijia Motion Sensor 2"                    and integration == 'Xiaomi Gateway 3')): 
      
      motion_entity_postfix = '_occupancy' if integration == 'Z2M' else \
                              '_motion'  # if integration == 'Xiaomi Gateway 3'

      self.binary_sensor_list += [
        {
          "platform": "group",
          "name": name + " Motion Sensor Motion" + name_postfix,
          "entities": "binary_sensor." + mac + motion_entity_postfix,
          "configured": True 
        }        
      ]

      light_entity_postfix = '_illuminance_lux' if integration == 'Z2M' else \
                             '_illuminance'   # if integration == 'Xiaomi Gateway 3'

      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Motion Sensor Light" + name_postfix,
              "unit_of_measurement": "lx",
              "state": '{{states.sensor["' + mac + light_entity_postfix + '"].state}}'
            }
          ],
          "configured": True 
        }        
      ]
      
      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Motion Sensor Battery" + name_postfix,
              "unit_of_measurement": "%",
              "state": '{{states.sensor["' + mac + '_battery"].state}}'
            }
          ],
          "configured": True 
        }        
      ]

    elif (model == "Ziqing Occupancy Sensor") or \
         (model == "Xiaomi Occupancy Sensor") or \
         (model == "Linptech Occupancy Sensor") : 

      self.binary_sensor_list += [
        {
          "platform": "group",
          "name": name + " Occupancy Sensor Occupancy" + name_postfix,
          "entities": "binary_sensor." + mac + '_occupancy',
          "configured": True 
        }        
      ]

      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Occupancy Sensor Light" + name_postfix,
              "unit_of_measurement": "lx",
              "state": '{{states.sensor["' + mac + '_illuminance"].state}}'
            }
          ],
          "configured": True 
        }        
      ]



    ###################################################################################################
    # Generic Binary Sensor
    ###################################################################################################
    elif(model == "Generic Binary Sensor"):

      self.binary_sensor_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "binary_sensor." + mac,
          "configured": True 
        }        
      ]

    ###################################################################################################
    # Temperature Sensor in Xiaomi Gateway 3
    # Qingping Temperature Sensor,      id: "ble LYWSDCGQ/01ZM"
    # Qingping Lite Temperature Sensor, id: "ble CGDK2"
    # Mijia2 Temperature Sensor,        id: "ble LYWSD03MMC"
    #
    # Temperature Sensor in Passive BLE 
    # "Mijia2 Temperature Clock", id:"ble LYWSD02MMC"
    ###################################################################################################
    elif((model == "Qingping Temperature Sensor"      and integration == 'Xiaomi Gateway 3') or \
         (model == "Mijia2 Temperature Sensor"        and integration == 'Xiaomi Gateway 3') or \
         (model == "Qingping Lite Temperature Sensor" and integration == 'Xiaomi Gateway 3')): 

      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Temperature Sensor" + name_postfix,
              "unit_of_measurement": "°C",
              "state": '{{states.sensor["' + mac + '_temperature"].state | float | round(1)}}'
            }
          ],
          "configured": True 
        }        
      ]

    elif model in [ "Mijia2 Temperature Clock" ] and integration == 'Passive BLE Monitor': 

      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Temperature Sensor" + name_postfix,
              "unit_of_measurement": "°C",
              "state": '{{states.sensor["temperature_humidity_sensor_' + mac + '_temperature"].state | float | round(1)}}'
            }
          ],
          "configured": True 
        }        
      ]

    elif((model in ["Aqara B1 curtain motor", "Aqara roller shade motor"] and integration == 'Xiaomi Gateway 3')): 
      
      self.cover_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "cover." + mac + "_motor",
          "configured": True 
        }        
      ]   
      
      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Curtain Battery" + name_postfix,
              "unit_of_measurement": "%",
              "state": '{{states.sensor["' + mac + '_battery"].state}}'
            }
          ],
          "configured": True 
        }        
      ]      
      
      self.aqara_shutter_blind = True if model in ["Aqara roller shade motor"] else False
      
    ###################################################################################################
    # Generic lights
    # Mijia BLE Lights, MJDP09YL
    ###################################################################################################
    elif((model == "Generic Lights"                                                                    ) or \
         (model == "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum" and integration == 'Z2M')): 
             
      self.light_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "light." + mac,
          "configured": True 
        }        
      ]    

    elif model == "Mijia BLE Lights": 
      self.light_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "light." + mac + "_light",
          "configured": True 
        }        
      ]          
    ###################################################################################################
    # Generic switches
    # Mi Power Plug ZigBee, ZNCZ02LM ZigbeeID: ["lumi.plug"]
    ###################################################################################################
    elif((model == "Generic Switches"      ) or \
         (model == "Mi Power Plug ZigBee"  )): 

      switch_entity_postfix = '_plug' if model == "Mi Power Plug ZigBee" else ''
      
      self.switch_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "switch." + mac + switch_entity_postfix,
          "configured": True 
        }        
      ]   

    elif(model == "Generic Power Measurement Switch"): 
      
      if power_on_threshold == None:
        raise TypeError( "\n" +\
                         "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                         "Model " + model + " needs power_on_threshold to be dinfed. Name = " + name + name_postfix + ', MAC Address:' + mac + ", Integration " + integration + "\n" + \
                         "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
      
      self.template_list += [
        {
          "binary_sensor": [
            {
              "name": name + name_postfix,
              # round(1) means to round to 0.1 
              "state": '{% if (states.sensor["' + mac + '"].state) | float | round(1) > ' + str(power_on_threshold) + ' %} on {% else %} off {% endif %}'
            }
          ],
          "configured": True 
        }        
      ]        
      
    ###################################################################################################
    # Generic covers/Generic curtains
    ###################################################################################################
    elif model == "Generic Curtains": 
      self.cover_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "cover." + mac,
          "configured": True 
        }        
      ]         
    ###################################################################################################
    # Model not found, throw an error
    ###################################################################################################
    else:
      raise TypeError( "\n" +\
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                       "Model " + model + " is not supported. Name = " + name + name_postfix + ', MAC Address:' + mac + ", Integration " + integration + "\n" + \
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")



  def add_average_temperature_sensor(self, sensor_1, sensor_2, name):
      self.template_list += [
        {
          "sensor": [
            {
              "name": name,
              "unit_of_measurement": "°C",
              "state": "" + \
                  "{% if   states('"+sensor_1 +"') != 'unavailable' and states('" + sensor_2 + "') == 'unavailable' %}" + \
                     "{{states('"+sensor_1 +"')}}"    + \
                  "{% elif states('"+sensor_1 +"') == 'unavailable' and states('" + sensor_2 + "') != 'unavailable' %}" + \
                     "{{states('"+sensor_2 +"')}}"    + \
                  "{% else %}"  + \
                    "{% set sensor_1 = states('"+sensor_1 +"') | float | round(1) %}" + \
                    "{% set sensor_2 = states('"+sensor_2 +"') | float | round(1) %}" + \
                    "{% if sensor_1 < 1.0 or sensor_2 < 1.0 or (sensor_1 + sensor_2) < 1.0 %}" + \
                       "22.0" + \
                    "{% else %}" + \
                       "{{ ((sensor_1 + sensor_2) / 2) | round(1) }}" + \
                    "{% endif %}" + \
                  "{% endif %}"                     
            }
          ],
          "configured": True 
        }        
      ]

  def get_entity_declarations(self):
      self.get_script_dict()
      self.input_select_dict |= {
        self.getPostfix(self.room_scene_ctl) : {
          "name" :  self.getName(self.room_scene_ctl),
          "configured": self.cfg_scene,
          "options": \
          ['Idle']
        + (["Hue"            ] if self.cfg_scene_color_led or self.cfg_scene_color_lamp else [])
        + (["Sleep Mode",
            "Night Mode",
            "Dark Night Mode"] if self.cfg_custom_scene else[])
        + (["Lamp LED White" ] if len(self.lamps) > 0 else [])  
        + (["LED White"      ] if len(self.leds)  > 0 else [])  
        #+ (["Ceiling Light White with Curtain Open"] if len(self.curtains)  > 0 else [])  
        + [ "All White",
            "Ceiling Light White",
            "All Off"
          ]
        #+ ["States when bright morning",
        #   "States when bright afternoon",
        #   "States when dark"
        #  ]

        }
      }
      
      self.input_select_dict |= {
        self.getPostfix(self.room_occupancy) : {
          "name" :  self.getName(self.room_occupancy),
          "options":[
            "Outside",
            "Just Entered",
            "Stayed Inside",
            "In Sleep"
          ],
          "configured": self.cfg_occupancy
        }
      }
    
      self.input_boolean_dict |= {
        #self.getPostfix(self.force_stay_inside) : {
        #  "name" :  self.getName(self.force_stay_inside),
        #  "initial": "off",
        #  "configured": self.cfg_occupancy
        #},
        self.getPostfix(self.room_heating_override) : {
          "name" :  self.getName(self.room_heating_override),
          "initial": "off",
          "configured": self.cfg_temp_control
        }
      } 
      
      if self.room_type == 'bedroom':
        self.input_boolean_dict |= {
          self.getPostfix(self.sleep_time) : {
            "name" :  self.getName(self.sleep_time),
            "configured": self.cfg_occupancy
          }
        }

      self.input_datetime_dict |= {
        self.getPostfix(self.morning_start_time) : {
          "name" :  self.getName(self.morning_start_time),
          "has_date": False,
          "has_time": True,
          #"initial": "07:00:00",
          "configured": True
        },

        self.getPostfix(self.morning_end_time) : {
          "name" :  self.getName(self.morning_end_time),
          "has_date": False,
          "has_time": True,
          #"initial": "13:00:00",
          "configured": True
        },

        self.getPostfix(self.afternoon_start_time) : {
          "name" :  self.getName(self.afternoon_start_time),
          "has_date": False,
          "has_time": True,
          #"initial": "13:00:00",
          "configured": True
        },

        self.getPostfix(self.afternoon_end_time) : {
          "name" :  self.getName(self.afternoon_end_time),
          "has_date": False,
          "has_time": True,
          #"initial": "17:00:00",
          "configured": True
        },

      }

      self.input_boolean_dict |= {
        self.getPostfix(self.curtain_control_when['States when left']) : {
          "name" :  self.getName(self.curtain_control_when['States when left']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.curtains) == 0 else {}),
        self.getPostfix(self.ceiling_light_control_when['States when bright morning']) : {
          "name" :  self.getName(self.ceiling_light_control_when['States when bright morning']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.ceiling_lights) == 0 or len(self.curtains) == 0 else {}),
        self.getPostfix(self.lamp_control_when['States when bright morning']) : {
          "name" :  self.getName(self.lamp_control_when['States when bright morning']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.lamps) == 0 or len(self.curtains) == 0 else {}), 
        self.getPostfix(self.led_control_when['States when bright morning']) : {
          "name" :  self.getName(self.led_control_when['States when bright morning']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.leds) == 0 or len(self.curtains) == 0 else {}),
        self.getPostfix(self.curtain_control_when['States when bright morning']) : {
          "name" :  self.getName(self.curtain_control_when['States when bright morning']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.curtains) == 0 else {}),
        self.getPostfix(self.ceiling_light_control_when['States when bright afternoon']) : {
          "name" :  self.getName(self.ceiling_light_control_when['States when bright afternoon']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.ceiling_lights) == 0 else {}),
        self.getPostfix(self.lamp_control_when['States when bright afternoon']) : {
          "name" :  self.getName(self.lamp_control_when['States when bright afternoon']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.lamps) == 0 else {}),
        self.getPostfix(self.led_control_when['States when bright afternoon']) : {
          "name" :  self.getName(self.led_control_when['States when bright afternoon']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.leds) == 0 else {}),
        self.getPostfix(self.curtain_control_when['States when bright afternoon']) : {
          "name" :  self.getName(self.curtain_control_when['States when bright afternoon']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.curtains) == 0 else {}),
        self.getPostfix(self.ceiling_light_control_when['States when dark']) : {
          "name" :  self.getName(self.ceiling_light_control_when['States when dark']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.ceiling_lights) == 0 else {}),
        self.getPostfix(self.lamp_control_when['States when dark']) : {
          "name" :  self.getName(self.lamp_control_when['States when dark']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.lamps) == 0 else {}),
        self.getPostfix(self.led_control_when['States when dark']) : {
          "name" :  self.getName(self.led_control_when['States when dark']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.leds) == 0 else {}),
        self.getPostfix(self.curtain_control_when['States when dark']) : {
          "name" :  self.getName(self.curtain_control_when['States when dark']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.curtains) == 0 else {}),
      }

#      self.input_boolean_dict |= {
#        self.light_in_daytime_postfix : {
#          "name" : self.room_name + " Light in Daytime Enable",
#          "configured": True
#            # Initialized it to 'off' if auto curtain control is not supported  
#        } | ({} if self.cfg_auto_curtain_ctl else {"initial": "off"}), 
#
#        self.curtain_in_nighttime_postfix : {
#          "name" : self.room_name + " Curtain In Nighttime Enable",
#          "configured": True
#        } | ({} if self.cfg_auto_curtain_ctl else {"initial": "off"}), 
#      }

      self.input_boolean_dict |= {
        self.getPostfix(self.room_heating_override): {
          "name" : self.getName(self.room_heating_override),
          "initial": "off",
          "configured": self.cfg_temp_control
        }
      }

      self.sensor_list += [
        self.get_occupancy_ratio_sensor_config('1x'),
        self.get_occupancy_ratio_sensor_config('2x')
      ]

      # Group is special for "configured" as we need to remove disabled 
      # automations for generating groups
      if self.cfg_occupancy:
        self.group_dict |= {
          self.getPostfix(self.occupancy_group) : {
            "name": self.getName(self.occupancy_group), 
            "entities": [self.room_occupancy, self.motion_group] + self.all_motion_sensors + [self.automation_occupancy['id']]
          }  
        }
      
      self.group_dict |= {
        self.getPostfix(self.motion_group) : {
          "name": self.getName(self.motion_group), 
          "entities": self.all_motion_sensors
        }          
      }  

      self.group_dict |= {
        self.getPostfix(self.light_group): {
          "name" : self.getName(self.light_group),
          "entities": self.lights
        }          
      }  

      self.group_dict |= {
        self.getPostfix(self.window_group): {
          "name" : self.getName(self.window_group),
          "entities": self.windows
        }          
      }  

      self.group_dict |= {
        self.getPostfix(self.curtain_group): {
          "name" : self.getName(self.curtain_group),
          "entities": self.curtains
        }          
      }  


      # --------------------
      #  Main Card
      # --------------------

      # Add dashboard cards
      # Entertainment
      if self.tvs is not None and self.tvs != []:
        self.main_card_list.append(self.hccl.getEntityCard(entity=self.tvs[0],     card_name='TV'))

      if self.thermostat is not None:      
        self.main_card_list.append(self.hccl.getEntityCard(entity=self.thermostat, card_name='Raditor'))

      # Light and curtains
      for light in self.lights:
        self.main_card_list.append(self.hccl.getEntityCard(entity=light))

      for curtain in self.curtains:
        self.main_card_list.append(self.hccl.getEntityCard(entity=curtain))
      
      # Climate Control
      if self.cfg_temp_control:
        self.main_card_list.append(self.hccl.getEntityCard(entity=self.room_heating_override, card_name='Heating Override'))

      if self.temperature_sensor is not None:
        self.main_card_list.append(self.hccl.getEntityCard(entity=self.temperature_sensor, card_name='Temperature'))

      # --------------------
      #  Tail Card
      # --------------------
      if self.cfg_temp_control:
        self.tail_card_list.append(self.hccl.getEntityCard(entity=[self.thermostat], entity_name='', card_name='Schedule', card_type='custom:scheduler-card'))

      # Motion 
      if self.cfg_occupancy:
        self.tail_card_list.append(self.hccl.getEntityCard(entity=self.occupancy_group, card_name='Occupancy'))

      # Room Automation Control
      if self.cfg_group_auto:      
        self.tail_card_list.append(self.hccl.getEntityCard(entity=self.room_auto_gen_automations, card_name='Automation Control'))
      


  def get_script_dict(self):
    pass

  # Lighting Automations
  def get_automation_declarations(self):
    self.gen_motion_light_automations()
    self.gen_temp_control_automations()
    self.gen_xiaomi_button_automations()
    self.gen_curtain_button_automations()
    self.gen_wall_button_single_automations()
    self.gen_wall_button_double_automations()
    self.gen_adaptive_lighting_automations()
    self.gen_mirror_light_automations()
    self.gen_occupancy_automations()
    self.gen_tv_automations()
    self.gen_room_specific_automations()
    self.gen_window_automations()



    for self.automation in self.automations:
      #print ("@@ " + self.automation['alias'])
      self.automation['id'] = self.getIDFromAlias(self.automation['alias'])
  
    self.entity_declarations |= {'automation' : self.automations}

  def gen_room_specific_automations(self):
    pass
    
  def get_automation_group_declarations(self):    

    self.automation_entity_list = []

    # TODO rename this method because it includes other controls
    # Including auto curtain controls
    self.automation_entity_list = [] + \
      ([self.curtain_control_when['States when left']                    ] if len(self.curtains) > 0       else []) + \
      ([self.ceiling_light_control_when['States when bright morning']    ] if len(self.ceiling_lights) > 0 else []) + \
      ([self.lamp_control_when['States when bright morning']             ] if len(self.lamps) > 0          else []) + \
      ([self.led_control_when['States when bright morning']              ] if len(self.leds) > 0           else []) + \
      ([self.curtain_control_when['States when bright morning']          ] if len(self.curtains) > 0       else []) + \
      ([self.ceiling_light_control_when['States when bright afternoon']  ] if len(self.ceiling_lights) > 0 else []) + \
      ([self.lamp_control_when['States when bright afternoon']           ] if len(self.lamps) > 0          else []) + \
      ([self.led_control_when['States when bright afternoon']            ] if len(self.leds) > 0           else []) + \
      ([self.curtain_control_when['States when bright afternoon']        ] if len(self.curtains) > 0       else []) + \
      ([self.ceiling_light_control_when['States when dark']              ] if len(self.ceiling_lights) > 0 else []) + \
      ([self.lamp_control_when['States when dark']                       ] if len(self.lamps) > 0          else []) + \
      ([self.led_control_when['States when dark']                        ] if len(self.leds) > 0           else []) + \
      ([self.curtain_control_when['States when dark']                    ] if len(self.curtains) > 0       else [])

    # Generate automations group 
    for automation in self.entity_declarations['automation']:
      self.automation_entity_list += [automation['id']]
    
    # added wall switch control
    self.automation_entity_list += self.wall_switches
    self.automation_entity_list += self.decouple_wall_switches
    #self.automation_entity_list += [self.force_stay_inside]
    
    # added adaptive light control
    if self.cfg_adaptive_lighting == True:
      self.automation_entity_list += ["switch.adaptive_lighting_sleep_mode_" + self.room_entity]

    self.automation_entity_list += self.datetimes

    if self.cfg_group_auto:
      self.group_dict |= {
        self.getPostfix(self.room_auto_gen_automations) : {
          "name": self.getName(self.room_auto_gen_automations), 
          "entities": self.automation_entity_list 
        }  
      }      

    self.entity_declarations |= {
      "group":  self.group_dict
    }



  def populate_entities_into_database(self):
      self.entity_declarations |= {
        "input_select":      self.input_select_dict,
        "sensor":            self.sensor_list,
        "input_boolean":     self.input_boolean_dict,
        "input_datetime":    self.input_datetime_dict,
        "switch":            self.switch_list,
        "cover":             self.cover_list,
        "template":          self.template_list,
        "binary_sensor":     self.binary_sensor_list,
        "light":             self.light_list,
        "adaptive_lighting": self.al_light_list
      }

  def gen_motion_light_automations(self):
    self.automation_lights_on = {"alias":"ZL-" + self.automation_room_name + "Ceiling Lights On Or Open Curtains If Entering to Room" + "-" + self.room_name }
    self.automation_lights_on['id'] = self.getIDFromAlias(self.automation_lights_on['alias'])
    self.automations += [self.automation_lights_on | {
        # Lights on automation are initially off until it is automatically turned on when no present detected
        "configured" : self.cfg_motion_light,
        "trigger" : 
        {
            "entity_id": self.entrance_motion_sensors,
            "platform": "state",
            "to": "on"
        },        
        "action": [
          {
            "service": "automation.turn_off",
            "entity_id": self.automation_lights_on['id'],
            "data": { "stop_actions": False }
          },
          self.setNewSceneState("Idle"),
          {
            "alias": 'If it is bright morning', "if": self.condition_list_is('Bright morning'), "then": self.callSceneService('States when bright morning'),
            "else": {
              "alias": 'If it is bright afternoon', "if": self.condition_list_is('Bright afternoon'), "then": self.callSceneService('States when bright afternoon'),
              "alias": 'If it is dark',             "else": self.callSceneService('States when dark')
            }
          }
        ]          
    }]              

    self.automation_lights_off = {"alias":"ZL-" + self.automation_room_name + "Lights Off If No Person" + "-" + self.room_name}
    self.automation_lights_off['id'] = self.getIDFromAlias(self.automation_lights_off['alias'])
    self.automations += [self.automation_lights_off | {
        "configured": self.cfg_motion_light,
        "trigger": [
          { "platform": "state",
            "entity_id": self.room_occupancy,
            "to": "Outside"
          },
          {
            "minutes": "/5",
            "platform": "time_pattern"
          }
        ],
        "condition": [
          { "condition": "state",
            "entity_id": self.room_occupancy,
            "state": "Outside"
          }] + (
          # For non-pure occupancy sensor room (that has PIR sensors)
          # Make sure that if room_occupany is forced to Outside because of manual override (by button for example)
          # and people are going back to the room, the lights should not be turned off
          [{ "condition": "state",
            "entity_id": self.motion_group,
            "state": "off",
            "for": "00:01:00"
            }] if self.turn_to_outside_when_no_motion == 'no' else []),
        "action": { 
          'parallel': [
            # Re-enable lights on automation
            self.turn(self.automation_lights_on['id'], 'on'),
            # Turn off lights/curtains/tv
            {"if": self.continueIf(self.curtain_control_when["States when left"], "on"), "then": self.turn(self.curtains, "on"), "else": self.turn(self.curtains, "off")},
            self.turn(self.tvs, 'off'),
            self.callSceneService("All Off"),
            self.turn(self.extractor, 'off')          
          ]
        }    
      }
    ]
    
    self.automations += [
      { 
        "alias" : "ZL-" + self.automation_room_name + "Disable Entering Lights-on Automation If any People are in the Room" + "-" + self.room_name,
        "configured": self.cfg_motion_light,
        "trigger": [
          { "platform": "state",
            "entity_id": self.room_occupancy,
            "to": ["Just Entered", "In Sleep", "Stayed Inside"]
          }
        ],
        "action": [
            # Delay to lights still turning on for people that double press wall button and go back in the room again
            {"delay" : "00:00:10"},
            # Disable lights-on automation when people are inside the room but didn't move until now and accidentally detected as Outside
            {"service":      "automation.turn_off",
             "entity_id":    self.automation_lights_on['id'],
             "data": {"stop_actions": "false"}}
          ]
      }
    ]
    
    self.automations += [
      {
        "alias" : "ZL-" + self.automation_room_name + "LED On for 3 Min if Walking In the Dark" + "-" + self.room_name,
        "configured": self.cfg_motion_light and self.cfg_motion_bed_led,
        "mode": "restart",
        "trigger": [
          {
            "entity_id": self.non_bed_motion_sensors,
            "platform": "state",
            "to": "on"
          }
        ],
        "condition": [
          {
            "condition": "state",
            "entity_id": "input_select.indoor_brightness",
            "state": "dark"
          },
          {
            "condition": "not",
            "conditions": [{
                "condition": "state",
                "entity_id": self.leds + self.ceiling_lights + self.lamps if self.room_entity != 'guest_room' else \
                             self.leds + self.ceiling_lights,
                "state": "on",
                "match": "any"}]
          }
        ],
        "action": [
          self.callSceneService("Dark Night Mode") if self.room_entity == 'master_room' else self.turn(self.leds, 'on', light_brightness=40),
          #self.turn(self.leds, 'on', light_brightness=40),
          {
            "alias": "Wait for floor sensors to go off for 1 min to turn off LED. Stop waiting if it has wait for 1 hour.",
            "wait_for_trigger": 
              { "platform": "state",
                "entity_id": self.non_bed_motion_sensors,
                "to":  "off",
                "for": "00:01:00"
              },
            "timeout": "01:00:00"
          },
          {
            "alias": " Testing if other lights are manually turned on after the LED was on",  
            "condition": "not",
            "conditions": [{
                "condition": "state",
                "entity_id": self.leds + self.ceiling_lights + self.lamps if self.room_entity != 'guest_room' else \
                             self.leds + self.ceiling_lights,
                "state": "on",
                "match": "any"}]
          },          
          self.turn(self.leds, 'off') 
        ]
      }
    ]


  def gen_tv_automations(self):
    self.automations += [
      { 
        "alias" : "ZTV-" + self.automation_room_name + "Reset Picture Mode When Turning on TV" + "-" + self.room_name,
        "configured": len(self.tvs) > 0,
        "trigger": [
          { "platform": "state",
            "entity_id": self.tvs,
            "from": "off",
            "to": "on"
          }
        ],
        "action": [
            self.turn(self.tvs, tv_brightness=3)
          ]
      }
    ]

  def gen_window_automations(self):
    if len(self.windows) > 0:
      self.add_window_open_notification_when_leaving_zone_automations()
      self.add_window_open_notification_when_going_to_sleep_automations()
      self.add_window_open_notification_when_timeout_automations()

  def add_window_open_notification_when_leaving_zone_automations(self):
    self.automations += [{
      "alias": "ZN-" + self.automation_room_name + "Notify Window Left Open When Tai is Leaving Zone" + "-" + self.room_name,
      "configured": True,
      "trigger": [
        {
          "platform": "zone",
          "entity_id": "device_tracker.tais_iphone_13",
          "zone": "zone.home",
          "event": "leave"
        }
      ],
      "condition": [
        {
          "condition": "state",
          "entity_id": self.window_group,
          "state": "on"
        }
      ],
      "action": [
        {
          "service": "script.notify_alexa_speakers_and_phones",
          "data": {
            "tts_message": self.room_name + " windows are left open. But you have left home. Is that ok?",
            "notify_tai": "yes"
          }
        }
      ]
    }]

    self.automations += [{
      "alias": "ZN-" + self.automation_room_name + "Notify Window Left Open When Ke is Leaving Zone" + "-" + self.room_name,
      "configured": True,
      "trigger": [
        {
          "platform": "zone",
          "entity_id": "device_tracker.kes_iphone_14_pro_max",
          "zone": "zone.home",
          "event": "leave"
        }
      ],
      "condition": [
        {
          "condition": "state",
          "entity_id": self.window_group,
          "state": "on"
        }
      ],
      "action": [
        {
          "service": "script.notify_alexa_speakers_and_phones",
          "data": {
            "tts_message": self.room_name + " windows are left open. But you have left home. Is that ok?",
            "notify_ke": "yes"
          }
        }
      ]
    }]


  def add_window_open_notification_when_going_to_sleep_automations(self):
    self.automations += [{
      "alias": "ZN-" + self.automation_room_name + "Notify Window Left Open in Bedtime " + "-" + self.room_name,
      "configured": True,
      "trigger": [
        {
          "platform": "time",
          "at": [
                  "21:00:00",
                  "23:00:00",
                  "00:00:00",
                  "01:00:00",
                  "02:00:00",
                  "03:00:00"
                ]
        }
      ],
      "condition": [
        {
          "condition": "state",
          "entity_id": self.window_group,
          "state": "on"
        }
      ],
      "action": [
        {
          "service": "script.notify_alexa_speakers_and_phones",
          "data": {
            "tts_message": self.room_name + " windows are left open. But it's almost bedtime time. Is that ok?",
            "notify_tai": "yes",
            "notify_ke": "yes",
          } | ({
            "notify_guest_room_tenant": "yes",
            "notify_en_suite_room_tenant": "yes"            
          } if self.room_entity == 'kitchen' else {})
        }
      ]
    }]


  def add_window_open_notification_when_timeout_automations(self):
    self.automations += [{
      "alias": "ZN-" + self.automation_room_name + "Notify Window Left Open After Timeout"  + "-" + self.room_name,
      "configured": True,
      "trigger": [
        {
          "platform": "template",
          "value_template": "{{(now().timestamp() - states." + self.window_group + ".last_changed.timestamp()) > state_attr('input_datetime.qianjie_windows_open_timeout', 'timestamp')}}\n"
        }
      ],
      "condition": [
        {
          "condition": "state",
          "entity_id": self.window_group,
          "state": "on"
        }
      ],
      "action": [
        {
          "service": "script.notify_alexa_speakers_and_phones",
          "data": {
            "tts_message": self.room_name + " windows are left open for a while. Is that ok?",
            "notify_tai": "yes",
            "notify_ke": "yes"
          } | ({
            "notify_guest_room_tenant": "yes",
            "notify_en_suite_room_tenant": "yes"            
          } if self.room_entity == 'kitchen' else {})
        }
      ],
      "mode": "single"
    }]
 

  def gen_temp_control_automations(self):
    self.automation_heating_on = {"alias":"ZH-" + self.automation_room_name + "Heating Schedule On If Staying In the Room" + "-" + self.room_name}
    self.automation_heating_on['id'] = self.getIDFromAlias(self.automation_heating_on['alias'])
    self.automations += [self.automation_heating_on | {      
        "configured": self.cfg_temp_control and self.cfg_occupancy,
        "trigger": [
          { "platform": "state",
            "entity_id": self.room_occupancy,
            "from": [ "Just Entered",
                      "Outside"       ],
            "to": ["Stayed Inside", "In Sleep"]
          }
        ],
        "action": [
          {
            "if": [
              {
                "condition": "not",
                "conditions": [
                  { "condition": "state",
                    "entity_id": self.thermostat,
                    "state": "heat"
                  }
                ]
              }
            ],
            "then": self.turn('heating', 'on')
          }
        ]
      }      
    ]

    self.automation_heating_off = {"alias":"ZH-"+self.automation_room_name+"Heating Schedule Off If People Left the Room"+"-"+self.room_name}
    self.automation_heating_off['id'] = self.getIDFromAlias(self.automation_heating_off['alias'])
    self.automations += [self.automation_heating_off | {      
        "configured": self.cfg_temp_control and self.cfg_occupancy,
        "trigger": [
          { "platform": "state",
            "entity_id": self.room_occupancy,
            "to": "Outside"
          },
          {
            "minutes": "/5",
            "platform": "time_pattern"
          }          
        ],
        "action": 
            [
              { "condition": "state",
                "entity_id": self.room_occupancy,
                "state": "Outside"
              },
              ## Make sure that if room_occupany is forced to Outside because of people override (by button for example)
              ## and people are going back to the room, the lights should not be turned off
              #{ "condition": "state",
              #  "entity_id": self.motion_group,
              #  "state": "off",
              #  "for": "00:01:00"
              #},      
              # Won't turn off heating unless override is off
              { "condition": "state",
                "entity_id": self.room_heating_override,
                "state": "off"
              },
              self.turn('heating', 'off')
            ]
      }      
    ]

    self.automations += [
      {
        "alias" : "ZH-" + self.automation_room_name + "Heating Manual Override" + "-" + self.room_name,
        "configured": self.cfg_temp_control,
        "mode": "restart",
        "trigger": [
          { "platform": "state",
            "entity_id": self.room_heating_override
          }
        ],
        "action": [
          {
            "if": [
              {
                "condition": "state",
                "entity_id": self.room_heating_override,
                "state": "off"
              }
            ],
            "then": [
              { "service": "automation.trigger",
                "entity_id": [self.automation_heating_off['id']]
              }
            ],
            "else": [
              { "service": "automation.trigger",
                "entity_id": [self.automation_heating_on['id']]
              },
              { "delay": {"hours": 2}
              },
              {
                "service": "homeassistant.turn_off",
                "entity_id": self.room_heating_override
              },              
              { "service": "automation.trigger",
                "entity_id": [self.automation_heating_on['id']]
              }
            ]
          }
        ]
      }      
    ]

    self.automations += [
      {
        "alias" : "ZH-" + self.automation_room_name + "Valve Calibrate Temperature Using External Sensor" + "-" + self.room_name,
        "configured": self.cfg_temp_control and self.cfg_temp_calibration,
        "use_blueprint": {
          "path": "calibrate_valve_temperature.yaml",
          "input": {
            "tado_valve_entity": self.thermostat,
            "external_temperature_sensor_entity": self.temperature_sensor
          }
        }
      }
    ]

  # State Machine
  # "All Off"
  # -> "All White" ->  "Lamp LED White" -> "LED White"
  # -> "Hue" -> "Night Mode" ->  "Dark Night Mode"
  #
  # The code is essentially equivilent to the below, however, the code below 
  # is evaluated backwards - i.e. first evaluation is the last statement, so 
  # explicitly strictly order this evaluation can have the programme correctly run.
  #
  #     [self.setNewSceneFromOldScene(cur_scene="All Off", nxt_scene="All White"),
  #     self.setNewSceneFromOldScene(nxt_scene="Lamp LED White")] 
  # + ([self.setNewSceneFromOldScene(nxt_scene="Night Mode")]    if self.cfg_custom_scene else []) 
  # + ([self.setNewSceneFromOldScene(nxt_scene="LED White")])    if self.cfg_led_only_scene else [] 
  # + ([self.setNewSceneFromOldScene(nxt_scene="All Off")])
  #
  def get_scene_state_machine(self):
    cond_seq = []
    
    cond_seq += [ self.setNewSceneFromOldScene(cur_scene="All Off", nxt_scene="All White"),
                  self.setNewSceneFromOldScene(nxt_scene="Lamp LED White")] 

    if self.cfg_scene_color_led or self.cfg_scene_color_lamp:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Hue")]          
    if self.cfg_led_only_scene:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="LED White")]
    if self.cfg_custom_scene:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Sleep Mode")]
    if self.cfg_custom_scene:
      #cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Night Mode")] 
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Dark Night Mode")]
      
    cond_seq += [self.setNewSceneFromOldScene(nxt_scene="All Off")] 
      
    return cond_seq

  def add_offline_device_automations(self, device_type, offline_device, tts_message, gateway_power_switch='N/A'):
    self.automations += [{
      "alias": "ZN-" + self.automation_room_name + "Notify " + device_type + " Offline Devices " + "-" + self.room_name,
      "configured": True,
      "trigger": [
        {
          "platform": "state",
          "entity_id": offline_device,
          "to": "unavailable",
          "for": "00:03:00"
        }
      ],
      "action": [
        {
          "service": "script.notify_alexa_speakers_and_phones",
          "data": {
            "tts_message": tts_message + " Offline device: " + offline_device,
            "notify_tai": "yes"
          }
        }
        ] + ([
          self.turn(gateway_power_switch, "off"),
          {"delay": "00:00:02"},
          self.turn(gateway_power_switch, "on")
        ] if gateway_power_switch != 'N/A' else [])
    }]  

  # constant definition to make sure there is no typo to pass an undefined string
  TOGGLE_AL_SLEEP_MODE      = 'TOGGLE_AL_SLEEP_MODE'                  
  TOGGLE_CURTAINS           = 'TOGGLE_CURTAINS'        
  TOGGLE_CURTAIN_0          = 'TOGGLE_CURTAIN_0'        
  TOGGLE_CURTAIN_1          = 'TOGGLE_CURTAIN_1'        
  INCREMENT_CURTAINS        = 'INCREMENT_CURTAINS'
  DECREMENT_CURTAINS        = 'DECREMENT_CURTAINS'        
  INCREMENT_CURTAIN_0       = 'INCREMENT_CURTAIN_0'
  DECREMENT_CURTAIN_0       = 'DECREMENT_CURTAIN_0'        
  INCREMENT_CURTAIN_1       = 'INCREMENT_CURTAIN_1'
  DECREMENT_CURTAIN_1       = 'DECREMENT_CURTAIN_1'        
  TOGGLE_LAMP_0             = 'TOGGLE_LAMP_0'                 
  INCREMENT_LAMP_0          = 'INCREMENT_LAMP_0' 
  DECREMENT_LAMP_0          = 'DECREMENT_LAMP_0'  
  TOGGLE_LAMP_1             = 'TOGGLE_LAMP_1'                 
  INCREMENT_LAMP_1          = 'INCREMENT_LAMP_1' 
  DECREMENT_LAMP_1          = 'DECREMENT_LAMP_1'  
  TOGGLE_CEILING_LIGHTS     = 'TOGGLE_CEILING_LIGHTS'                 
  INCREMENT_CEILING_LIGHTS  = 'INCREMENT_CEILING_LIGHTS' 
  DECREMENT_CEILING_LIGHTS  = 'DECREMENT_CEILING_LIGHTS'  
  TOGGLE_SCREEN_LED         = 'TOGGLE_SCREEN_LED'
  TOGGLE_LEDS               = 'TOGGLE_LEDS'       
  INCREMENT_LEDS            = 'INCREMENT_LEDS' 
  DECREMENT_LEDS            = 'DECREMENT_LEDS'  
  CYCLE_SCENES              = 'CYCLE_SCENES'
  DO_NOTHING                = 'DO_NOTHING'
  CYCLE_TV_BRIGHTNESS       = 'CYCLE_TV_BRIGHTNESS'
  INCREMENT_TV_BRIGHTNESS   = 'INCREMENT_TV_BRIGHTNESS'
  DECREMENT_TV_BRIGHTNESS   = 'DECREMENT_TV_BRIGHTNESS'
  INCREMENT_TV_VOLUME       = 'INCREMENT_TV_VOLUME'
  DECREMENT_TV_VOLUME       = 'DECREMENT_TV_VOLUME'
  TOGGLE_TV_POWER           = 'TOGGLE_TV_POWER'
  TOGGLE_HEATING            = 'TOGGLE_HEATING'       
  INCREMENT_HEATING         = 'INCREMENT_HEATING'
  DECREMENT_HEATING         = 'DECREMENT_HEATING'

  def get_trigger_action_list(self):
    # initialize variables if it does not exisits
    if not hasattr(self, 'screen_leds'):
      self.screen_leds = []

    return {
      "choose": 
        ([{ "conditions":[{"condition": "trigger","id": self.CYCLE_SCENES            }], "sequence": {"choose": self.get_scene_state_machine(), "default": self.setNewSceneState("All White")}}])  + \
        ([{ "conditions":[{"condition": "trigger","id": self.DO_NOTHING              }], "sequence": [{"service": "script.do_nothing"}]}])                                                         + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_AL_SLEEP_MODE    }], "sequence": [self.turn(self.al_sleep_mode, 'toggle'                  )]}]                                              ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_CURTAINS         }], "sequence": [self.turn(self.curtains,      'toggle'                  )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_CURTAIN_0        }], "sequence": [self.turn(self.curtains[0],   'toggle'                  )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_CURTAIN_1        }], "sequence": [self.turn(self.curtains[1],   'toggle'                  )]}] if len(self.curtains)       >= 2 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_CURTAINS      }], "sequence": [self.turn(self.curtains,      'increment'               )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_CURTAINS      }], "sequence": [self.turn(self.curtains,      'decrement'               )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_CURTAIN_0     }], "sequence": [self.turn(self.curtains[0],   'increment'               )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_CURTAIN_0     }], "sequence": [self.turn(self.curtains[0],   'decrement'               )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_CURTAIN_1     }], "sequence": [self.turn(self.curtains[1],   'increment'               )]}] if len(self.curtains)       >= 2 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_CURTAIN_1     }], "sequence": [self.turn(self.curtains[1],   'decrement'               )]}] if len(self.curtains)       >= 2 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_LAMP_0           }], "sequence": [self.turn(self.lamps[0],      'toggle'   , step_value=25)]}] if len(self.lamps)          >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_LAMP_0        }], "sequence": [self.turn(self.lamps[0],      'increment', step_value=25)]}] if len(self.lamps)          >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_LAMP_0        }], "sequence": [self.turn(self.lamps[0],      'decrement', step_value=25)]}] if len(self.lamps)          >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_LAMP_1           }], "sequence": [self.turn(self.lamps[1],      'toggle'   , step_value=25)]}] if len(self.lamps)          >= 2 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_LAMP_1        }], "sequence": [self.turn(self.lamps[1],      'increment', step_value=25)]}] if len(self.lamps)          >= 2 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_LAMP_1        }], "sequence": [self.turn(self.lamps[1],      'decrement', step_value=25)]}] if len(self.lamps)          >= 2 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_CEILING_LIGHTS   }], "sequence": [self.turn(self.ceiling_lights,'toggle'   , step_value=25)]}] if len(self.ceiling_lights) >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_CEILING_LIGHTS}], "sequence": [self.turn(self.ceiling_lights,'increment', step_value=25)]}] if len(self.ceiling_lights) >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_CEILING_LIGHTS}], "sequence": [self.turn(self.ceiling_lights,'decrement', step_value=25)]}] if len(self.ceiling_lights) >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_SCREEN_LED       }], "sequence": [self.turn(self.screen_leds,   'toggle'                  )]}] if len(self.screen_leds)    >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_LEDS             }], "sequence": [self.turn(self.leds,          'toggle'                  )]}] if len(self.leds)           >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_LEDS          }], "sequence": [self.turn(self.leds,          'increment', step_value=25)]}] if len(self.leds)           >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_LEDS          }], "sequence": [self.turn(self.leds,          'decrement', step_value=25)]}] if len(self.leds)           >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_TV_POWER         }], "sequence": [self.turn(self.tvs,           'power_toggle'            )]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.CYCLE_TV_BRIGHTNESS     }], "sequence": [self.turn(self.tvs,            tv_brightness='cycle'    )]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_TV_BRIGHTNESS }], "sequence": [self.turn(self.tvs,            tv_brightness='increment')]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_TV_BRIGHTNESS }], "sequence": [self.turn(self.tvs,            tv_brightness='decrement')]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_TV_VOLUME     }], "sequence": [self.turn('tv_volumne',        'increment', step_value=3)]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_TV_VOLUME     }], "sequence": [self.turn('tv_volumne',        'decrement', step_value=3)]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.TOGGLE_HEATING          }], "sequence": [self.turn('heating',           'toggle'                 )]}] if len(self.thermostat)     >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.INCREMENT_HEATING       }], "sequence": [self.turn('heating',           'increment', step_value=1)]}] if len(self.thermostat)     >= 1 else []     ) + \
        ([{ "conditions":[{"condition": "trigger","id": self.DECREMENT_HEATING       }], "sequence": [self.turn('heating',           'decrement', step_value=1)]}] if len(self.thermostat)     >= 1 else []     ) + \
        ([])    
          } 

  def gen_xiaomi_button_automations(self):
    self.automations += [{
        "alias" : "ZLB-" + self.automation_room_name + "Single Button Button Control" + "-" + self.room_name,
        "configured": self.cfg_remote_light and (self.num_of_xiaomi_button > 0),
        "trigger": 
          ([{"platform": "state",  "entity_id": self.xiaomi_buttons,    "to": ["single", "1"], "id": self.CYCLE_SCENES     }]) + \
          ([{"platform": "state",  "entity_id": self.xiaomi_buttons,    "to": ["double", "2"], "id": self.TOGGLE_CURTAINS  }]) + \
          ([{"platform": "state",  "entity_id": self.xiaomi_buttons[0], "to": ["hold",      ], "id": self.TOGGLE_LAMP_0    }] if len(self.xiaomi_buttons) >= 1 else []) + \
          ([{"platform": "state",  "entity_id": self.xiaomi_buttons[1], "to": ["hold",      ], "id": self.TOGGLE_LAMP_1    }] if len(self.xiaomi_buttons) >= 2 else []) + \
          ([{"platform": "state",  "entity_id": self.xiaomi_buttons,    "to": ["triple", "3"], "id": self.DO_NOTHING       }]) + \
          ([{"platform": "state",  "entity_id": self.xiaomi_buttons,    "to": ["quadruple"  ], "id": self.DO_NOTHING       }]) + \
          ([{"platform": "state",  "entity_id": self.xiaomi_buttons,    "to": ["many"       ], "id": self.DO_NOTHING       }]) + \
          ([{"platform": "state",  "entity_id": self.xiaomi_buttons,    "to": ["release"    ], "id": self.DO_NOTHING       }]),
        "mode":"queued", # this has to be queued to make sure no button press is ignored
        "action": self.get_trigger_action_list()
    }]

    self.automations += [{
        "alias" : "ZLB-" + self.automation_room_name + "Eight Key Knob Control" + "-" + self.room_name,
        "configured": len(self.eight_key_knob_buttons) > 0,
        "trigger": [
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_1_single',                                      "id": self.TOGGLE_AL_SLEEP_MODE },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ['button_1_double','button_1_hold',
                                                                              "knob_clockwise_after_toggling_button_1",
                                                                              "knob_clockwise_after_toggling_button_1_and_knob",
                                                                              "knob_anticlockwise_after_toggling_button_1",
                                                                              "knob_anticlockwise_after_toggling_button_1_and_knob"],"id": self.CYCLE_SCENES },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_2_single',                                      "id": self.TOGGLE_CEILING_LIGHTS},
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ['button_2_double','button_2_hold'],                    "id": self.DO_NOTHING},
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_clockwise_after_toggling_button_2",
                                                                              "knob_clockwise_after_toggling_button_2_and_knob"],    "id": self.INCREMENT_CEILING_LIGHTS},
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_anticlockwise_after_toggling_button_2",
                                                                              "knob_anticlockwise_after_toggling_button_2_and_knob"],"id": self.DECREMENT_CEILING_LIGHTS},
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_3_single',                                      "id": self.TOGGLE_HEATING         },
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ['button_3_double','button_3_hold'],                    "id": self.DO_NOTHING},          
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_clockwise_after_toggling_button_3",
                                                                              "knob_clockwise_after_toggling_button_3_and_knob"],    "id": self.INCREMENT_HEATING},
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_anticlockwise_after_toggling_button_3",
                                                                              "knob_anticlockwise_after_toggling_button_3_and_knob"],"id": self.DECREMENT_HEATING},          
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_4_single',                                      "id": self.CYCLE_TV_BRIGHTNESS  },
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ['button_4_double'],                                   "id": self.DO_NOTHING},          
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_4_hold',                                        "id": self.TOGGLE_TV_POWER      },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_clockwise_after_toggling_button_4",
                                                                              "knob_clockwise_after_toggling_button_4_and_knob"],    "id": self.INCREMENT_TV_VOLUME  },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_anticlockwise_after_toggling_button_4",
                                                                              "knob_anticlockwise_after_toggling_button_4_and_knob"],"id": self.DECREMENT_TV_VOLUME  },
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_clockwise_after_toggling_button_4_and_knob"],    "id": self.INCREMENT_TV_BRIGHTNESS},
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_anticlockwise_after_toggling_button_4_and_knob"],"id": self.DECREMENT_TV_BRIGHTNESS},
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_5_single',                                      "id": self.TOGGLE_LEDS          },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_5_double',                                      "id": self.TOGGLE_SCREEN_LED    },          
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ['button_5_double','button_5_hold'],                    "id": self.DO_NOTHING},          
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_clockwise_after_toggling_button_5",
                                                                              "knob_clockwise_after_toggling_button_5_and_knob"],    "id": self.INCREMENT_LEDS       },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_anticlockwise_after_toggling_button_5",
                                                                              "knob_anticlockwise_after_toggling_button_5_and_knob"],"id": self.DECREMENT_LEDS       },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_6_single',                                      "id": self.TOGGLE_CURTAINS      },
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ['button_6_double','button_6_hold'],                    "id": self.DO_NOTHING},          
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_clockwise_after_toggling_button_6",
                                                                              "knob_clockwise_after_toggling_button_6_and_knob"],    "id": self.INCREMENT_CURTAINS},
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_anticlockwise_after_toggling_button_6",
                                                                              "knob_anticlockwise_after_toggling_button_6_and_knob"],"id": self.DECREMENT_CURTAINS},          
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_7_single',                                      "id": self.TOGGLE_LAMP_0        },
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ['button_7_double','button_7_hold'],                    "id": self.DO_NOTHING},          
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_clockwise_after_toggling_button_7",
                                                                              "knob_clockwise_after_toggling_button_7_and_knob"],    "id": self.INCREMENT_LAMP_0     },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_anticlockwise_after_toggling_button_7",
                                                                              "knob_anticlockwise_after_toggling_button_7_and_knob"],"id": self.DECREMENT_LAMP_0     },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_8_single',                                      "id": self.TOGGLE_LAMP_1        },
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ['button_8_double','button_8_hold'],                    "id": self.DO_NOTHING},          
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_clockwise_after_toggling_button_8",
                                                                              "knob_clockwise_after_toggling_button_8_and_knob"],    "id": self.INCREMENT_LAMP_1     },
          {"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_anticlockwise_after_toggling_button_8",
                                                                              "knob_anticlockwise_after_toggling_button_8_and_knob"],"id": self.DECREMENT_LAMP_1     },
        ],
        "mode":"parallel", 
        "action": self.get_trigger_action_list()
    }]



    self.automations += [{
        "alias" : "ZLB-" + self.automation_room_name + "Six Key Button Control" + "-" + self.room_name,
        "configured": len(self.six_key_buttons) > 0,
        "trigger": [
          {"platform": "state",  "entity_id": self.six_key_buttons, "to": 'button_1_single', "id": self.TOGGLE_AL_SLEEP_MODE },
          {"platform": "state",  "entity_id": self.six_key_buttons, "to": 'button_2_single', "id": self.TOGGLE_CURTAINS      },
          {"platform": "state",  "entity_id": self.six_key_buttons, "to": 'button_3_single', "id": self.TOGGLE_LAMP_0        },
          {"platform": "state",  "entity_id": self.six_key_buttons, "to": 'button_4_single', "id": self.TOGGLE_LAMP_1        },
          {"platform": "state",  "entity_id": self.six_key_buttons, "to": 'button_5_single', "id": self.TOGGLE_CEILING_LIGHTS},
          {"platform": "state",  "entity_id": self.six_key_buttons, "to": 'button_6_single', "id": self.TOGGLE_LEDS          }
        ],
        "mode":"parallel", 
        "action": self.get_trigger_action_list()
    }]

    self.automations += [{
        "alias" : "ZLB-" + self.automation_room_name + "Four Key Button Control" + "-" + self.room_name,
        "configured": len(self.four_key_buttons) > 0,
        "trigger": [
          {"platform": "state",  "entity_id": self.four_key_buttons,  "to": 'on',                "id": self.TOGGLE_CURTAINS     },
          {"platform": "state",  "entity_id": self.four_key_buttons,  "to": 'off',               "id": self.TOGGLE_AL_SLEEP_MODE},
          {"platform": "state",  "entity_id": self.four_key_buttons,  "to": 'arrow_left_click',  "id": self.TOGGLE_LAMP_0       },
          {"platform": "state",  "entity_id": self.four_key_buttons,  "to": 'arrow_right_click', "id": self.TOGGLE_LAMP_1       }
        ],
        "mode":"parallel", 
        "action": self.get_trigger_action_list()
    }]
    

    self.automations += [{
        "alias" : "ZL-" + self.automation_room_name + "Applies Different Scenes Based on Scene Selections (State Execution)" + "-" + self.room_name,
        "configured": self.cfg_scene,
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.room_scene_ctl,
          }
        ],
        "mode":"restart", # using restart to improve responsiveness of a scene execution
        "action": [
          {
            "choose": [
              self.callSceneServiceIfSelected("All White"),
              self.callSceneServiceIfSelected("Ceiling Light White"),
              self.callSceneServiceIfSelected("Lamp LED White"),
              self.callSceneServiceIfSelected("LED White"),
              self.callSceneServiceIfSelected("Hue"),
              self.callSceneServiceIfSelected("Night Mode"),
              self.callSceneServiceIfSelected("Dark Night Mode"),
              self.callSceneServiceIfSelected("Sleep Mode"),
              self.callSceneServiceIfSelected("All Off"),
              self.callSceneServiceIfSelected("States when bright morning"),
              self.callSceneServiceIfSelected("States when bright afternoon"),
              self.callSceneServiceIfSelected("States when dark")
            ]
          }
        ]
    }]


  def gen_curtain_button_automations(self):
    self.automations += [{
        "alias" : "ZLB-" + self.automation_room_name + "Remote Button-Single-Toggle Blind" + "-" + self.room_name,
        "configured": (len(self.curtain_buttons) > 0),
        "trigger": {"platform": "state",  "entity_id": self.curtain_buttons,    "to": ["single", "1"], "id": self.TOGGLE_CURTAINS },
        "mode":"restart", 
        "action": self.get_trigger_action_list()
    }]


  
  # Exceptions that will be written per room - most of them because the wall button have multiple keys and multiple lights
  # [TODO] Ground Corridor - double - turn off everything apart from en-suite room/toilet 
  # [TODO] First Corridor - double - turn off everything apart from en-suite room/toilet 
  # [TODO] Master Room - Left - Ceiling light
  # [TODO] Master Room - Middle - Lamps & LED
  # [TODO] Master Room - Right - Balcony Lights
  # [TODO] Master Room - Single - Scenes 
  # [TODO] Master Toilet Dressing Room 
  def gen_wall_button_single_automations(self):
    if self.cfg_flex_switch == False:
      self.gen_a_button_toggle_automation( button_state_list=[ "1", "single", "single_left", "single_right", "single_center", 
                                                              "button_1_single", "button_2_single", "button_3_single"],
                                           button_state_name='Single')

  def gen_a_button_toggle_automation(self,
                                     button_state_list, 
                                     button_state_name, 
                                     device_list=None, 
                                     device_name=None, 
                                     button_list=None,
                                     switch_type="Wall Switch"):
                                       

    if device_list is None:
      device_list = self.ceiling_lights

    if device_name is None:
      device_name = 'Ceiling Light'
      
    if button_list is None:
      button_list = self.wall_buttons
      
    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + switch_type + " - " + button_state_name + " Press - Toggle " + device_name + "-" + self.room_name,
        "configured": self.cfg_remote_light,
        "trigger": [
          {
            "platform": "state",
            "entity_id": button_list,
            "to": button_state_list
          }
        ],
        "action": [self.turn(device_list, "toggle")]
      }
    ]


  def gen_flex_wall_switch_automations(self, flex_wall_switch_index, flex_wall_switch_entity):
    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Flex Wall Switch On Postion " + str(flex_wall_switch_index)  + "- Automatically Turn on the Wall Switch Back When Turned Off -" + self.room_name,
        "configured": True,
        "trigger": [
          {
            "platform": "state",
            "entity_id": flex_wall_switch_entity,
            "to": "off"
          }
        ],
        "action": [self.turn(flex_wall_switch_entity, "on")]
      }
    ]    

  def gen_wall_button_double_automations(self):
    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Wall Switch - Double Press - Leave Room and Turn Off Everything" + "-" + self.room_name,
        "configured": self.cfg_remote_light,
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.wall_buttons,
            "to":  ["2", "double", "double_left", "double_right", "double_center", "button_1_double", "button_2_double", "button_3_double"]
          }
        ],
        "action": [
          { "service": "automation.trigger",
            "entity_id": [self.automation_lights_off['id'],
                          self.automation_heating_off['id']]
          },
          # set occupancy to Outside eariler to make sure if we enter the room shortly again, the auto-heating can be configured
          { "service": "input_select.select_option",
            "target":  {"entity_id": self.room_occupancy},
            "data":    {"option": "Outside"}
          }
        ]        
      }
    ]
  def gen_adaptive_lighting_automations(self):
    pass
  # Use scheduler card instead
  
  #  self.automations += [
  #    {
  #      "alias":"ZL-" + self.automation_room_name + "Turns On Sleep Mode In The Night" + "-" + self.room_name,
  #      "configured": self.cfg_adaptive_lighting,
  #      "trigger": [
  #        {
  #          "platform": "time",
  #          "at": self.start_of_sleep_time
  #        }
  #      ],
  #      "action": [self.turn(self.al_sleep_mode, 'on')]
  #    }
  #  ]
  #
  #  self.automations += [
  #    {
  #      "alias":"ZL-" + self.automation_room_name + "Turns Off Sleep Mode In The Morning" + "-" + self.room_name,
  #      "configured": self.cfg_adaptive_lighting,
  #      "trigger": [
  #        {
  #          "platform": "time",
  #          "at": self.end_of_sleep_time
  #        }
  #      ],
  #      "action": [self.turn(self.al_sleep_mode, 'off')]
  #    }
  #  ]


  def gen_mirror_light_automations(self):
    self.automations += [
      {
        "alias":"ZLM-" + self.automation_room_name + "Mirror Sensor On Turns On Ceiling Light With Cool Temperature" + "-" + self.room_name,
        "configured": len(self.mirror_sensors) > 0,
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.mirror_sensors,
            "from": "off",
            "to":  "on"
          }
        ],
        "action": [
          {
            "condition": "state",
            "entity_id": self.mirror_sensors,
            "state":  "on"
          },
          { "service": "light.turn_on",
            "target":  {"entity_id": self.ceiling_lights},
            "data":    {"brightness_pct": 100,
                        "kelvin": 6500}
          }
        ]        
      }
    ]

    self.automations += [
      {
        "alias":"ZLM-" + self.automation_room_name + "Mirror Sensor Off Turns Ceiling Light With Adaptive Lighting Unless it's off" + "-" + self.room_name,
        "configured": len(self.mirror_sensors) > 0,
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.mirror_sensors,
            "from": "on",
            "to":  "off"
          }
        ],
        "action": [
          {
            "condition": "state",
            "entity_id": self.mirror_sensors,
            "state":  "off"
          },
          { "service": "adaptive_lighting.apply",
            "data":    {"entity_id": self.al_adapt_brightness}
          }
        ]        
      }
    ]


  def gen_occupancy_automations(self):
    
    self.automations += [self.automation_occupancy | 
      {
        #"alias":"ZOc-" + self.automation_room_name + "Occupancy Update" + "-" + self.room_name,
        "configured": self.cfg_occupancy,
        "trigger": [
          {
            "entity_id": self.motion_group,
            "platform": "state",
            "to": "on"
          },
          {
            "entity_id": self.motion_group,
            "platform": "state",
            "to": "off",
          },
          {
            "minutes": "/5",
            "platform": "time_pattern"
          }
        ],
        "action": {
                      "service" : "pyscript.room_occupancy_state_machine",
                      "data":{
                              "occupancy_entity_str":           self.room_occupancy,
                              "motion_str":                     self.motion_group,                                 
                              "motion_on_ratio_for_x_min_str":  self.occupancy_on_x_min_ratio_sensor,
                              "motion_on_ratio_for_2x_min_str": self.occupancy_on_2x_min_ratio_sensor,
                              "sleep_time":                     self.sleep_time,
                              'turn_to_outside_when_no_motion': self.turn_to_outside_when_no_motion,
                              "inside_to_outside_timeout":      self.inside_to_outside_timeout,
                              "sleep_to_outside_timesout":      self.sleep_to_outside_timesout,
                              "inside_to_sleep_timeout":        self.inside_to_sleep_timeout,
                              }
            }
      }
    ]
    
#    self.automations += [{
#        "alias":"ZoC-N-" + self.automation_room_name + "History Stat Reload On Timeout" + "-" + self.room_name,
#        "configured": self.cfg_occupancy,
#        "trigger": [
#          {
#            "minutes": "/5",
#            "platform": "time_pattern"
#          }
#        ],
#        "action": [
#          {
#            "condition": "and",
#            "conditions": [
#              {
#                "condition": "state",
#                "entity_id": self.motion_group,
#                "for": {
#                  "hours": 0,
#                  "minutes": 6,
#                  "seconds": 0
#                }
#              },
#              {
#                "condition": "not",
#                "conditions": [
#                  {
#                    "condition": "numeric_state",
#                    "entity_id": self.occupancy_on_x_min_ratio_sensor,
#                    "above": 0,
#                    "below": 100
#                  }
#                ]
#              }
#            ]
#          },
#          {
#            "service": "history_stats.reload"
#          },
#          {
#            "service": "script.notify_alexa_speakers_and_phones",
#            "data": {
#              "tts_message": self.room_entity + " timed out, reload history stat.",
#              "notify_tai": "yes"
#            }
#          }
#        ]
#      }]


  # Generate automation ID/entity_name based on alias name
  def getIDFromName(self, name):
    id = name.lower()
    id = re.sub("-", "_", id)
    id = re.sub("'", "_", id)
    id = re.sub('"', "_", id)
    id = re.sub("\.", "_", id)
    id = re.sub("/", "_", id)
    id = re.sub("\s", "_", id)
    id = re.sub("\(", "_", id)
    id = re.sub("\)", "_", id)
    id = re.sub("_+$", "", id)
    id = re.sub("(_+)", "_", id)
    return id

  def getIDFromAlias (self, alias):
    id = self.getIDFromName(alias)
    id = "automation." + id
    return id

  # Create service call for turn on/off entities
  def turn(self, entity_list, state=None, light_brightness=None, tv_brightness=None, inc_unavail=True, step_value=34):
    assert state in ['on', 'off', 'toggle', 'increment', 'decrement', 'power_toggle', 'single_device_volume_inc', 'single_device_volume_dec', None], "State has to be one of legal states, but it is " + state
    #assert type(entity_list) is list , "entity_list has to be a list, but it is " + entity_list

    if state in ['increment', 'decrement']:
      step_value = -1 * step_value if state == 'decrement' else step_value

    is_light_list = True
    if type(entity_list) is list:
      for entity in entity_list :
        is_light_list = is_light_list if entity.startswith('light.') else False
    else:
        is_light_list = is_light_list if entity_list.startswith('light.') else False

    if state == 'power_toggle':
      action_service = {"if": self.continueIf(entity_list, "off"), 
                        "then": self.turn(entity_list, 'on'), 
                        "else": self.turn(entity_list, 'off')}
    elif light_brightness != None:
      action_service = {"service" : "light.turn_on",
                        "entity_id" : entity_list,
                        "data": {"brightness_pct": light_brightness}}
    elif tv_brightness != None:
      if tv_brightness == 'cycle':
        action_service =    {"choose": 
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Movie"   ), "sequence": self.turn(self.tvs, tv_brightness=4)}])  + \
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Natural" ), "sequence": self.turn(self.tvs, tv_brightness=1)}])  + \
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Standard"), "sequence": self.turn(self.tvs, tv_brightness=2)}])  + \
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Dynamic" ), "sequence": self.turn(self.tvs, tv_brightness=3)}])  + \
          ([])    
          } 
      elif tv_brightness == 'increment':
        action_service =    {"choose": 
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Movie"   ), "sequence": self.turn(self.tvs, tv_brightness=2)}])  + \
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Natural" ), "sequence": self.turn(self.tvs, tv_brightness=3)}])  + \
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Standard"), "sequence": self.turn(self.tvs, tv_brightness=4)}])  + \
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Dynamic" ), "sequence": self.turn(self.tvs, tv_brightness=4)}])  + \
          ([])    
          } 
      elif tv_brightness == 'decrement':
        action_service =    {"choose": 
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Movie"   ), "sequence": self.turn(self.tvs, tv_brightness=1)}])  + \
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Natural" ), "sequence": self.turn(self.tvs, tv_brightness=1)}])  + \
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Standard"), "sequence": self.turn(self.tvs, tv_brightness=2)}])  + \
          ([{ "conditions":self.continueIf(self.tv_picture_mode, "Dynamic" ), "sequence": self.turn(self.tvs, tv_brightness=3)}])  + \
          ([])    
          }           
      elif tv_brightness in [1,2,3,4,5,6,7,8,9,10]:
        action_service =    {
                            "if": [
                              {
                                'alias': 'Set TV brightness when it is on',
                                "condition": "state",
                                "entity_id": entity_list,
                                "state": "on"
                              }
                            ],
                            "then":  { "service" : "input_select.select_option",
                                        "data": { "entity_id" : self.tv_picture_mode,
                                                  "option": "Movie"    if tv_brightness in [1, '1'] else \
                                                            "Natural"  if tv_brightness in [2, '2'] else \
                                                            "Standard" if tv_brightness in [3, '3'] else \
                                                            "Dynamic"}}
                          }
                          #  "then":  {"service" : "samsungtv_smart.select_picture_mode",
                          #              "data": { "entity_id" : entity_list,
                          #                        "picture_mode": "Movie"    if tv_brightness in [1, '1'] else \
                          #                                        "Natural"  if tv_brightness in [2, '2'] else \
                          #                                        "Standard" if tv_brightness in [3, '3'] else \
                          #                                        "Dynamic"}}
      else:
        self.error(f"turn({entity_list}, tv_brightness={tv_brightness}) is not supported")
    elif entity_list == 'tv_volumne':
      if state in ['increment', 'decrement']:
        single_device_state = "single_device_volume_inc" if state == 'increment' else "single_device_volume_dec"
        if len(self.tv_soundbars) > 0:
          action_service = {"if":   self.continueIf(self.tv_soundbars, "playing"), 
                            "then": self.turn(self.tv_soundbars, single_device_state, step_value=step_value),
                            "else": self.turn(self.tvs,          single_device_state, step_value=step_value)}
        else:
          action_service = self.turn(self.tvs, single_device_state)
      else:
        self.error(f"turn({entity_list}, {state}) is not supported.")

    elif state in ['single_device_volume_inc', "single_device_volume_dec"] :
        action_service = {"service": "media_player.volume_set",
                          "entity_id": entity_list,
                          "data_template":
                            {"volume_level": "{{ (state_attr('" + entity_list[0] + "', 'volume_level')) + " + str(step_value/100) +" }}"}
                          }

    elif entity_list == self.curtains:
      
      if state in ['increment', 'decrement']:
        action_service = {"service": "cover.set_cover_position",
                          "target":{"entity_id": self.curtains},
                          # making sure the final value saturated to range [0,100]
                          "data":  {"position": "{{ [[ (state_attr('" + self.curtains[0] + "', 'current_position')) + " + str(step_value) + " ,0]|max,100]|min}}"}}        
      # Shutter blind
      elif self.aqara_shutter_blind == True and state in ['on', 'off']:        
        if state == 'on': 
          if self.room_entity == 'study':
            # open full blind for study
            action_service = {"service": "cover.set_cover_position",
                              "data":    {"position": 100},
                              "entity_id": self.curtains}
          else:
            # open shutter for master toilet
            # Set to 0 position to open the shutter, blind full down
            action_service = {"service": "cover.set_cover_position",
                              "data":    {"position": 0},
                              "entity_id": self.curtains}
        elif state == 'off':
          # Set to 2 position to close the shutter, blind full down
          action_service = {"service": "cover.set_cover_position",
                            "data":    {"position": 2},
                            "entity_id": self.curtains}
        else:
          action_service = {"service":   "cover.toggle",
                            "entity_id": entity_list}      
      # Normal blind or curtains
      elif state in ['on', 'off', 'toggle']:
        action_service = {"service":  "cover.open_cover"       if state == 'on'     else \
                                      "cover.close_cover"      if state == 'off'    else \
                                      "cover.toggle"           if state == 'toggle' else None,
                          "entity_id": entity_list}
      else:
        self.error(f"turn({entity_list}, state={state}) is not supported")                          

      # stop the curtain before any curtain actions - make sure the previous action is stopped
      action_service = self.convertToSingleService(
                      [{"service":  "cover.stop_cover",
                        "entity_id": entity_list},   
                        action_service])    

    # TODO make sure that it only turns a directory or a list.
    # use a different way to handle this case                    
    elif entity_list == self.thermostat:
      hvac_mode = "off" if state == 'off' else "heat"
      
      if state in ['on', 'off']:
        action_service = { "service": "climate.set_hvac_mode",
                          "data": {"hvac_mode": hvac_mode},
                          "entity_id": self.thermostat
                        }
      else:
        self.error(f"turn({entity_list}, state={state}) is not supported")                          

    #--------------------------------------------------------------------------                       
    # No need to do this as long as adaptive light setting is with enough delay                   
    #--------------------------------------------------------------------------                       
    # Turn on lamps and also reset to white if set to rgb/hs mode                       
    #elif entity_list == self.lamps and state == 'on':
    #  action_service = self.setLightsToWhite(self.lamps)
    
    elif entity_list == 'heating':
      if state in ['toggle']:
        action_service = {"if": self.continueIf(self.thermostat, "off"), 
                          "then": self.turn(entity_list, 'on'), 
                          "else": self.turn(entity_list, 'off')}      
      elif state in ['on', 'off']:
        action_service = self.convertToSingleService(
                        [self.turn(self.thermostat,          state),
                          self.turn(self.thermostat_schedule, state)] + \
                          ([] if self.room_entity != 'kitchen' else \
                          [self.turn('switch.kitchen_hot_water', state)]))
      elif state in ['increment', 'decrement']:
        action_service = {"service": "climate.set_temperature",
                          "target":{"entity_id": self.thermostat},
                          "data":  {"temperature": "{{ (state_attr('" + self.thermostat + "', 'temperature')) + " + str(step_value) + "}}"}}
      else:
        self.error(f"turn({entity_list}, state={state}) is not supported")

    #--------------------------------------------------------------------------                       
    # This does not work very well as hue integeration lights are never unavailable, even without power                   
    #--------------------------------------------------------------------------                       
    # If ceiling lights are offline, use wall switch for controls instead
    #elif entity_list == self.ceiling_lights and inc_unavail == True:
    #  action_service =  {
    #                      "if": [
    #                        {
    #                          'alias': 'any ceiling lights is unavailable, using wall switches to control instead',
    #                          "condition": "state",
    #                          "entity_id": entity_list,
    #                          "state": "unavailable",
    #                          "match": 'any'
    #                        }
    #                      ],
    #                      "then": self.turn(self.wall_switches,  state),
    #                      "else": self.turn(self.ceiling_lights, state, inc_unavail=False)
    #                    }

    elif entity_list == self.wall_switches and state == 'on':
      action_service = self.convertToSingleService(
                        [{"service":"homeassistant.turn_off", "entity_id": entity_list},
                         {"delay": {"milliseconds": 200}},
                         {"service":"homeassistant.turn_on",  "entity_id": entity_list}],
                          alias='Everytime to turn on a wall switch, make sure to turn off it first to make sure the smart lights will be back on')
    # Adaptive light only applies when lights are turned on by light.turn_on instead of homeassistant.turn_on
    # that's not true..... 
    elif is_light_list and (state == 'on' or state == 'off'):
      action_service = {"service":"light.turn_on"  if state == 'on'     else \
                                  "light.turn_off" if state == 'off'    else None,
                        "entity_id": entity_list}

    elif is_light_list and (state == 'increment' or state == 'decrement'):
      action_service = {"service":"light.turn_on",
                        "target":{"entity_id":entity_list},
                        "data":{"brightness_step_pct":step_value}}

    # does not work if light list has swtich entity
    elif is_light_list == False and (state == 'increment' or state == 'decrement'):
      action_service =  {"service": "script.do_nothing"}

    elif state == 'on' or state == 'off':
      action_service = {"service":"homeassistant.turn_on"  if state == 'on'     else \
                                  "homeassistant.turn_off" if state == 'off'    else None,
                        "entity_id": entity_list}
    
    elif state == 'toggle':
      action_service =  {
                          "if": [
                            {
                              'alias': 'toggle everything all together: if any entity is on, turn off all entities, otherwise turn on all entities',
                              "condition": "state",
                              "entity_id": entity_list,
                              "state": "on",
                              "match": 'any'
                            }
                          ],
                          "then": self.turn(entity_list, 'off'),
                          "else": self.turn(entity_list, 'on')
                        }

    if entity_list != None and entity_list != []:
      return self.convertToSingleService( action_service, 
                                          alias =  ('Turn'  + \
                                                    (' nothing'        if entity_list==[]              else \
                                                    ' ' + entity_list  if isinstance(entity_list, str) else " " + " ".join(entity_list)) + \
                                                    (''                if state==None                  else ' state=' + state) + \
                                                    (''                if light_brightness==None       else ' light_brightness=' + str(light_brightness))))
    else:
      return {"service": "script.do_nothing"}


  def setLightsToWhite(self, entity_list):
    
    alias =   'Turn on lamps first and check if light color is white. ' + \
              'Reset color lamps to white and apply adaptive lighting.'

    lights_only_entity_list = []
    # Remove non-light entities, such as switch
    for entity in entity_list:
      lights_only_entity_list += [entity] if entity.startswith('light') else []

    service_list = [
       {"service": "homeassistant.turn_on", "entity_id": self.lamps}, # turn on switches in the first instance
       {"delay" : "00:00:02"},
       {"if": self.continueIf(lights_only_entity_list, 'color_temp', attribute='color_mode'), 
         "then": {"service": "script.do_nothing"},
         "else":[ 
             {"service": "light.turn_on",  "entity_id": lights_only_entity_list, "data": {"kelvin": "3000"}},
             {"delay"  : "00:00:02"},
             {"service": "light.turn_off", "entity_id": lights_only_entity_list},
             {"delay"  : "00:00:02"},
             {"service": "light.turn_on",  "entity_id": lights_only_entity_list}
         ]
       }
    ]

    return self.convertToSingleService(service_list, alias)

  def convertToSingleService(self, service_list, alias=''):
    # "sequence" cannot be used in automation generally
    #return {"sequence": service_list}
    
    return {"alias": alias, "if": self.alwaysOnIf(True), "then": service_list}

  def callSceneService(self, scene_name):  
      parallel_enable = True  
      scene_service = []  
      if   scene_name == 'All White':
          scene_service += [self.turn(self.lamps, "on"),
                            self.turn(self.ceiling_lights, "on"),
                            self.turn(self.leds, "on"),
                            self.turn(self.tvs, tv_brightness=3)]
      elif scene_name == 'Ceiling Light White':
          scene_service += [self.turn(self.lamps, "off"),
                            self.turn(self.leds, "off"),
                            self.turn(self.ceiling_lights, "on"),
                            self.turn(self.tvs, tv_brightness=3)]   
      #elif scene_name == 'Ceiling Light White with Curtain Open':
      #    scene_service += [self.turn(self.leds + self.lamps, "off"),
      #                      self.turn(self.ceiling_lights, "on"),
      #                      self.turn(self.tvs, tv_brightness=3),
      #                      self.turn(self.curtains, 'on')]   
      elif scene_name == 'Lamp LED White':
          scene_service += [self.turn(self.ceiling_lights, "off"),
                            self.turn(self.lamps, "on"),
                            self.turn(self.leds, "on")]
      elif scene_name == 'LED White':
          scene_service += [self.turn(self.leds, "on")]
      elif scene_name == 'Hue': 
          parallel_enable = False
          scene_service += [# turn off non rgb lights
                            { "service" : "pyscript.turn_rgb_light",
                              "data": {"light_list": self.lamps + self.ceiling_lights+ self.leds, 
                              "state": 'off', 
                              "rgb" : 'non_rgb_only'}},
                            # set hue colors
                            { "service" : "pyscript.turn_rgb_light",
                              "data": {"light_list": self.lamps + self.ceiling_lights+ self.leds}},
                            self.turn(self.tvs, tv_brightness=2)]
      elif scene_name == 'Night Mode': 
          scene_service += [{ "service": "homeassistant.turn_on",
                              "entity_id": "scene." + self.room_entity + "_night_mode" },
                            self.turn(self.tvs, tv_brightness=2)]
      elif scene_name == 'Dark Night Mode': 
          scene_service += [{ "service": "homeassistant.turn_on",
                              "entity_id": "scene." + self.room_entity + "_dark_night_mode" },
                            self.turn(self.tvs, tv_brightness=1)]
      elif scene_name == "Sleep Mode": 
          scene_service += [{ "service": "homeassistant.turn_on",
                              "entity_id": "scene." + self.room_entity + "_sleep_mode"}]
      elif scene_name == 'All Off':
          scene_service += [self.turn(self.ceiling_lights, "off"),
                            self.turn(self.lamps, "off"),
                            self.turn(self.leds, "off"),
                            self.turn(self.tvs, tv_brightness=3)] # reset TV brightness for bright room in the day time
                                                                  # considering turn it to 1 for night
      elif scene_name in ['States when bright morning',
                          'States when bright afternoon',
                          'States when dark']:
        
        scene_service += [{"parallel":[
          {"if": self.continueIf(self.ceiling_light_control_when[scene_name], "on"), "then": self.turn(self.ceiling_lights, "on"), "else": self.turn(self.ceiling_lights, "off")},
          {"if": self.continueIf(self.lamp_control_when[scene_name]         , "on"), "then": self.turn(self.lamps,          "on"), "else": self.turn(self.lamps,          "off")},
          {"if": self.continueIf(self.led_control_when[scene_name]          , "on"), "then": self.turn(self.leds,           "on"), "else": self.turn(self.leds,           "off")},
          {"if": self.continueIf(self.curtain_control_when[scene_name]      , "on"), "then": self.turn(self.curtains,       "on"), "else": self.turn(self.curtains,       "off")}
          ]}]

      else:
        raise TypeError( "\n" +\
                         "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                         "Scene " + scene_name + " is not supported." + "\n" + \
                         "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
      
      if parallel_enable == True:
        scene_service = [{"parallel":scene_service}] 
        
      # Convert to a single service/entry instead of a list  
      return self.convertToSingleService(scene_service, alias=scene_name)  

  def setNewScene(self, new_scene):
    # Instead of calling the input_select control, directly calling services of the scene
    return self.callSceneService(new_scene)
    
    
  def setNewSceneState(self, new_scene):
    seq = {
      "service": "script.call_room_scene",
      "data":{
        "room_scene_select": self.room_scene_ctl,
        "scene": new_scene
      }
    }
    return seq
    
  def ifOldSceneSetNewSceneState(self, old_scene, new_scene):
    cond_seq = {
        "conditions": 
          { "condition": "state",
            "entity_id": self.room_scene_ctl,
            "state": old_scene
          },
        "sequence": self.setNewSceneState(new_scene)
      }
    return cond_seq
  
  
  def setNewSceneFromOldScene(self, nxt_scene, cur_scene=None):
    if cur_scene != None:
      self.cur_scene = cur_scene
    
    #if self.room_name == "Living Room":
    #  print ("INFO: This is in " + self.room_name + ". nxt_scene=" + nxt_scene + ", cur_scene=" + str(cur_scene) + ", self.cur_scene=" + str(self.cur_scene) +".")
    
    if self.cur_scene == 'unintialized_cur_scene':
      exit ("ERROR: self.cur_scene is unintialized. This is in " + self.room_name + ". nxt_scene=" + nxt_scene + ", cur_scene=" + str(cur_scene) + ".")
    else:
      cond_seq = self.ifOldSceneSetNewSceneState(self.cur_scene, nxt_scene)
      self.cur_scene = nxt_scene

    return cond_seq


  def alwaysOnIf(self, cond):
    return  { "condition": "state",
              "entity_id": "input_boolean.always_on_constant" if cond else "input_boolean.always_off_constant",
              "state": "on"
            }

  def entity_is_on(self, entity):
    return  { "condition": "state",
              "entity_id": entity,
              "state": "on"
            }
  
  def callSceneServiceIfSelected(self, scene_name):
    cond_seq = {
        "conditions": [
          {
            "condition": "state",
            "entity_id": self.room_scene_ctl,
            "state": scene_name
          }
        ],
        "sequence": self.callSceneService(scene_name) 
      }
    return cond_seq


  def triggerIf(self, entity_id, toState=None, fromState=None, attribute=None, lastFor=None):
    trigger = { "platform": "state",
                "entity_id": entity_id,
              }
    trigger |= {"to":        toState  } if toState    != None else {}
    trigger |= {"from":      fromState} if fromState  != None else {}
    trigger |= {"attribute": attribute} if attribute  != None else {}
    trigger |= {"for":       lastFor}   if lastFor    != None else {}
    return trigger    


  def continueIf(self, entity_id, state, attribute=None, lastFor=None):
    cond =  { "condition": "state",
              "entity_id": entity_id,
              "state":     state
            }
    cond |= {"attribute": attribute} if attribute  != None else {}
    cond |= {"for":       lastFor}   if lastFor    != None else {}
    return cond


  def condition_list_is(self, condition_name):
    if condition_name == 'Bright morning':
      return [{ 'alias': condition_name,
                "condition": "and",
                "conditions": [
                  { "condition": "or",
                    "conditions": [
                      {"condition": "numeric_state",
                        "entity_id": "sensor.living_room_light_sensor",
                        "above": 100},
                      { "condition": "state",
                        "entity_id": "sensor.living_room_light_sensor",
                        "state": [
                          "unavailable",
                          "unknown"]}
                    ]
                  },
                  {
                    "condition": "or",
                    "conditions": [
                      { "condition": "state",
                        "entity_id": "sun.sun",
                        "state": "above_horizon"},
                      { "condition": "state",
                        "entity_id": "sun.sun",
                        "state": [
                          "unavailable",
                          "unknown"]}
                    ]
                  },
                  {
                    "condition": "time",
                    "after": self.morning_start_time,
                    "before": self.morning_end_time,
                  },               
                ]
              }]
    elif condition_name == 'Bright afternoon':
      return [{ 'alias': condition_name,
                "condition": "and",
                "conditions": [
                  { "condition": "or",
                    "conditions": [
                      {"condition": "numeric_state",
                        "entity_id": "sensor.living_room_light_sensor",
                        "above": 100},
                      { "condition": "state",
                        "entity_id": "sensor.living_room_light_sensor",
                        "state": [
                          "unavailable",
                          "unknown"]}
                    ]
                  },
                  {
                    "condition": "or",
                    "conditions": [
                      { "condition": "state",
                        "entity_id": "sun.sun",
                        "state": "above_horizon"},
                      { "condition": "state",
                        "entity_id": "sun.sun",
                        "state": [
                          "unavailable",
                          "unknown"]}
                    ]
                  },
                  {
                    "condition": "time",
                    "after": self.afternoon_start_time,
                    "before": self.afternoon_end_time,
                  },               
                ]
              }]              
#    elif condition_name == 'Hot sunshine':
#      return  [
#                # Outdoor temp above certain temperature
#                {
#                  "condition": "numeric_state",
#                  "entity_id": self.outside_temperature,
#                  "above": "15" if self.west_face_windows else "18"
#                },
#                # In the period that there might be a direct sunshine
#                {
#                  "condition": "time",
#                  "after":  "13:00:00"           if self.west_face_windows else self.daytime_start,
#                  "before": self.daytime_end     if self.west_face_windows else "16:00:00"
#                },
#                # Summer
#                {
#                  "condition": "template",
#                  "value_template": "{{ now().month > 4 and now().month < 9 }}"
#                },
#                # Room has curtain
#                self.alwaysOnIf(len(self.curtains) > 0)
#              ]
    else:
      raise TypeError( "\n" +\
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                       "Condition " + condition_name + "is not supported." + "\n" + \
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
      


  def getDashboardSettings(self):
    self.dashboard_default_root = '/Uninitliazed_dashboard_root'
    self.dashboard_view_name = 'Uninitliazed_dashboard_view_name'
    self.room_icon           = 'Uninitliazed_room_icon'

    import random

    ios_themes = [
    'ios-dark-mode-blue-red',
    'ios-dark-mode-dark-blue',
    'ios-dark-mode-dark-green',
    'ios-dark-mode-light-blue',
    'ios-dark-mode-light-green',
    'ios-dark-mode-orange',
    'ios-dark-mode-red'  
    ]

    self.room_theme          = ios_themes[random.randint(0,6)]

  def addView(self, viewPath='',
                    cards=[], 
                    theme="Mushroom Shadow",
                    title=''):
                      
    self.views += [{
                  "theme": theme,
                  "title": title,
                  "path":  viewPath,
                  #"icon": "",
                  "subview": True,
                  "badges": [],
                  "cards": cards
                 }]

  def getRoomViews(self):
    # Add room header navagation cards (back card + scene card)
    self.header_card_list += self.getHeaderCardList()
    
    all_cards = self.getLayoutWrapperCardList(self.header_card_list) + \
                self.getLayoutWrapperCardList(self.main_card_list)   + \
                self.tail_card_list
    
    #if self.room_name == 'Guest Room':
    #  print (self.main_card_list)
    self.addView(title=self.room_name, theme=self.room_theme, viewPath=self.room_navi_path, cards=all_cards)
    return self.views


  def getLayoutWrapperCardList(self, cards=None):
    
    if self.dashboard_type in ['mobile', 'default']:
      grid_cards = [{
          "square": False,
          "columns": 2,
          "type": "grid",
          "cards": cards}]          
    elif self.dashboard_type == 'tablet':
      grid_cards = cards
    else: 
        raise TypeError( "\n" +\
          "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
          "getLayoutWrapperCardList does not support dashboard_type" + dashboard_type + \
          "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

    return grid_cards
  
  def getHeaderCardList(self,navigate_path=None):
    # Navigation header
    return ([
        {
          "type": "custom:mushroom-template-card",
          "entity": "input_boolean.placeholder",
          "icon": "mdi:keyboard-return",
          "icon_color": "yellow",
          "primary": "HOME",
          "secondary": "",
          "layout": "vertical",
          "hold_action": {
            "action": "toggle"
          },
          "tap_action":{
            "action": "navigate",
            "navigation_path": (self.dashboard_root+"/"+"home") if navigate_path == None else navigate_path
          },
          "card_mod": {
            "style": {
              "mushroom-state-info$": ".primary {\n  font-size: 16px !important;\n  position: relative;\n  top: 0px;\n  left: 0px;\n  overflow: visible !important;\n  white-space:  \n}\n",
              "mushroom-shape-icon$": ".shape {\n  position: relative;\n  left: 0px;\n  top: 0px;\n}\n",
              ".": ":host {\n  --mush-icon-size: 80px;\n}\n"
            }
          }
        },
        self.hccl.getEntityCard(entity=self.room_scene_ctl, secondary_info='none')
#        {
#          "type": "entities",
#          "entities": [
#            {
#              "entity": self.room_scene_ctl,
#              "name": "Scene"
#            }
#          ],
#          "state_color": True,
#          "title": "Run a Scene",
#        }
    ])
  
  def getNavigationRoomCard (self):
    type = 'mushroom'

    # e.g. output can be states.sensor.corridor_temperature_sensor.state
    temperature_sensor_template_reference = "states." + self.temperature_sensor + ".state"
  
    if type == 'mushroom':
      room_card = {    
        "type": "custom:stack-in-card",
        "mode": "vertical",
        "cards": [
          self.getTemplateCard(
            icon       = self.room_icon,
            icon_color = "blue",
            primary    = self.room_name,
            secondary  = "{% if "+temperature_sensor_template_reference+" is defined %} {{ "+temperature_sensor_template_reference+" }}\u00b0C {% endif %}" + \
                         "{% set motion_postfix     = '"+self.getPostfix(self.motion_group)+"' %}\n" + \
                         "{% set motion = '"+self.motion_group+"' %}\n{% if is_state(motion, 'on') %}\n  🙋🏻\n{% else %}\n  🦶🏻\n{% endif %}{{\n (as_timestamp(now()) -\n as_timestamp(states.group[motion_postfix].last_changed)) |\n timestamp_custom(\"%H:%M\", false) }} ",
            tap_action = 'navigate'             
          ),
          # Make the bottom stack-in-card transparent
          self.getCardModColor("transparent") | {
            "type": "custom:stack-in-card",
            "mode": "horizontal",
            "cards": [
              #self.getTemplateCard(
              #  icon       = "{% set motion = '"+self.motion_group+"' %}  \n{% if is_state(motion, 'on') %}\n  mdi:run-fast\n{% else %}\n  mdi:shoe-print\n{% endif %}",
              #  icon_color = "{% set motion = '"+self.motion_group+"' %}  \n{% if is_state(motion, 'on') %}\n  blue\n{% endif %}",
              #),
            ] + ([] if self.cfg_occupancy == False else [
              self.getTemplateCard(
                icon       = "{% if   is_state(entity, 'Outside') %}\n  mdi:door-closed\n{% elif is_state(entity, 'Just Entered') %}\n  mdi:arrow-right-circle\n{% elif is_state(entity, 'In Sleep') %}\n  mdi:sleep\n{% else %}\n  mdi:account-multiple\n{% endif %}",
                icon_color = "{% if   is_state(entity, 'Outside') %} {% elif is_state(entity, 'Just Entered')%}\n  green\n{% elif is_state(entity, 'In Sleep') %}\n  blue            \n{% else %}\n  purple\n{% endif %}",
                tap_entity = self.room_occupancy
                #condition_state_not  = 'Outside',
                #condition_entity     = self.room_occupancy
              )
            ]) + ([] if self.cfg_temp_control == False else [
              self.getTemplateCard(
                icon       = "{% if is_state(entity, 'heat') %}\n  mdi:heating-coil\n{% else %}\n  mdi:snowflake\n{% endif %}",
                icon_color = "{% if is_state(entity, 'heat') %}\n  {% if state_attr(entity, 'temperature') > state_attr(entity, 'current_temperature') %}\n  red\n {% else %}\n blue\n  {% endif %}\n {% endif %}\n",
                condition_state  = 'heat',
                condition_entity = self.thermostat
              )
            ]) + ([] if self.lights == [] else [
              self.getTemplateCard(
                icon       = "{% if is_state(entity, 'on') %}\n  mdi:floor-lamp\n{% else %}\n  mdi:floor-lamp-outline\n{% endif %}",
                icon_color = "{% if is_state(entity, 'on') %}\n  amber\n{% endif %}",
                tap_entity = self.light_group
              )
            ]) + ([] if self.windows == [] else [
              self.getTemplateCard(
                icon       = "{% if is_state(entity, 'on') %}\n  mdi:window-open-variant\n{% else %}\n  mdi:window-closed-variant\n{% endif %}",
                icon_color = "{% if is_state(entity, 'on') %}\n  lime\n{% endif %}",
                condition_entity = self.window_group
              )
            ]) + ([] if self.tvs == [] else [
              self.getTemplateCard(
                icon       = "mdi:television-classic",
                icon_color = "{% if is_state(entity, 'on') %}\n  deep-orange\n{% endif %}",
                tap_entity = self.tvs[0]
                #condition_entity = self.tvs[0],
                #condition_state  = 'on'
              )
            ]) + ([] if self.curtains == [] else [
              self.getTemplateCard(
                icon       = "{% if is_state(entity, 'open') %}\n  mdi:curtains\n{% else %}\n  mdi:curtains-closed\n{% endif %}",
                icon_color = "{% if is_state(entity, 'open') %}\n  green       \n{% endif %}",
                condition_state  = 'open',
                condition_entity = self.curtain_group
              )
            ])
          }
        ]
      }    
    elif type == 'button':
      room_card =  {
        "type": "custom:button-card",
        "aspect_ratio": "1/1",
        "tap_action": {
          "action": "navigate",
          "navigation_path": self.dashboard_view_path
        },
        "entity": "input_boolean.placeholder",
        "show_state": False,
        "name": self.room_name,
        "icon": self.room_icon,
        "show_icon": True,
        "show_name": True
      }

    return self.getRestricedAccess('us', room_card)

  def getRestricedAccess(self, user, inner_card):
    if user not in ['us', 'en_suite_room_user', 'guest_room_user']:
      raise TypeError( "\n" +\
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                       "User " + user + "is not supported for restriction card" + "\n" + \
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

    
    return {
      "type": "custom:restriction-card",
      "restrictions": {
        "hide": {
          "exemptions": [
            {"user": "72e8e305715145febff1ba701fd78954"},
            {"user": "60652445f3d14a8f822054569404b643"},
            {"user": "317c743e4c8348b8a70d671db917dbe8"}
          ]
        }
      },
      "exemptions": [
        {"user": "72e8e305715145febff1ba701fd78954"},
        {"user": "60652445f3d14a8f822054569404b643"},
        {"user": "317c743e4c8348b8a70d671db917dbe8"}
      ],
      "card": inner_card
    }


  # Create a new yaml and write to it
  def writeConfig (self):
    
      yaml.Dumper.ignore_aliases = lambda *args : True
    
    #if type not in ['package', 'overall_dashboard']:
    #  raise TypeError("Yaml type " + type + " is not supported.")

    #if type == 'package':
      # File Path
      self.script_dir         = os.path.dirname(os.path.realpath(__file__))
      self.auto_gen_dir       = self.script_dir + "/../packages/_auto_generated_packages/"
      self.auto_gen_config_path = self.auto_gen_dir + "/auto_gen_" + self.room_entity + ".yaml"

      # Open a new file and write automation
      f = open(self.auto_gen_config_path, "w")

      f.write("#############################################################################\n")
      f.write("# DO NOT MODIFY. This is an automatically generated file.                   # \n")      
      f.write("# Please modify the python source code under python_templates directory.    #\n")      
      f.write("#############################################################################\n")
      
      yaml.Dumper.ignore_aliases = lambda *args : True

      f.write(yaml.dump(self.entity_declarations, sort_keys=False, width=float("inf")))
      #for category_name in self.entity_declarations:
      #  category_entities = self.entity_declarations[category_name]
      #  f.write(category_name + ":" + "\n")
      #  
      #  if type(category_entities) == list:
      #    
      #    for entity in category_entities:
      #      f.write(yaml.dump(entity, sort_keys=False, width=float("inf")))
      #      f.write("\n")
      #      
      #  elif type(category_entities) == dict:
      #    
      #    for entity_name in category_entities:
      #      entity = category_entities[entity_name]
      #      f.write(yaml.dump({entity_name : entity}, sort_keys=False, width=float("inf")))
      #      f.write("\n")
      #      
      f.close()



  def remove_disabed_entities(self):
    filtered_entities = {}

    for category_name in self.entity_declarations:
      category_entities = self.entity_declarations[category_name]
      
      # If this entity category declare each instance using list
      if type(category_entities) == list:
        filtered_entities[category_name] = []
        for entity in category_entities:
          #print(entity)
          if entity["configured"] == True:
            # remove 'configured' key
            entity.pop('configured')
            filtered_entity = entity
            filtered_entities[category_name] += [filtered_entity]
          #print(filtered_entity)
          #print(filtered_entities[category_name])
    
      # else this entity category declare each instance using dict
      elif type(category_entities) == dict:
        filtered_entities[category_name] = {}
        for entity_name in category_entities:
          entity = category_entities[entity_name]
          #print(entity)
          if entity["configured"] == True:
            # remove 'configured' key
            entity.pop('configured')
            filtered_entity = entity
            filtered_entities[category_name] |= {entity_name : filtered_entity}
            #print(filtered_entity)
            #print(filtered_entities[category_name])

      else:
        print ('ERORR: entity_declarations[' + category_name + '] is not either a dictionary or a list')
        
    self.entity_declarations = filtered_entities

#########################################################################
# Instantiate all the rooms with custom entities/automation override    #
#########################################################################
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
    self.cfg_scene_color_led   = True
    self.cfg_scene_color_lamp  = True
    self.cfg_custom_scene       = True
    self.cfg_motion_bed_led     = True
    self.cfg_auto_curtain_ctl   = True
    self.cfg_adaptive_lighting  = True

  def get_entity_declarations(self):
    super().get_entity_declarations()    
    self.add_mac_device("582d34376b04",                      self.room_name,                          'Temperature Sensor', "Qingping Temperature Sensor", postfix='new_1')
    self.add_mac_device("582d343b6a27",                      self.room_name,                          'Temperature Sensor', "Qingping Temperature Sensor", postfix='new_2')
  # self.add_mac_device('0x54ef441000792d09',                self.room_name + ' Bed',                 'Pressure Sensor',    'Aqara Pressure Sensor')    
#    self.add_mac_device('e4aaec755efa',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='1')    
#    self.add_mac_device('e4aaec755cbc',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='2')    
#    self.add_mac_device('e4aaec755ef9',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='3')    

    self.add_mac_device("a4c1383dc01d",                      self.room_name + ' Bed',                 'Motion Sensor',      "Linptech Occupancy Sensor")

#    self.add_mac_device("dced830908fb",                      self.room_name,                          'Motion Sensor',      "Ziqing Occupancy Sensor")
    self.add_mac_device("0x00158d0005228ba8",                self.room_name + " TV",                  'Motion Sensor',      "Aqara Motion and Illuminance Sensor")
    self.add_mac_device('50ec50df3056',                      self.room_name + " Bed Ceiling Light",   'Light',              'Mijia BLE Lights')
    self.add_mac_device("master_room_drawer_ceiling_light_xiaomi",self.room_name + " Drawer Ceiling Light",'Light',"Generic Lights")
    self.add_mac_device("hue_color_lamp_5",                  self.room_name + " Lamp 1",              'Light',              "Generic Lights")
    self.add_mac_device("hue_color_lamp_6",                  self.room_name + " Lamp 2",              'Light',              "Generic Lights")
    self.add_mac_device("master_room_bed_led_magic_home",    self.room_name + " Bed LED",             'Light',              "Generic Lights")
    self.add_mac_device("master_room_tv_led_magic_home",     self.room_name + " TV LED",              'Light',              "Generic Lights")
    self.add_mac_device("master_room_drawer_led_magic_home", self.room_name + " Drawer LED",          'Light',              "Generic Lights")
    self.add_mac_device("0x04cf8cdf3c73a19b",                self.room_name + " Curtain",             'Curtain',            "Aqara B1 curtain motor")
    #self.add_mac_device('18c23c24681a',                      self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='1')
    self.add_mac_device('18c23c25a26c',                      self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='1')
    self.add_mac_device('18c23c25960b',                      self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='2')
    self.add_mac_device("0x04cf8cdf3c7ad638",                self.room_name,                          'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Triple Rocker)", flex_switch=[2,3])
    self.add_mac_device('sonoff_1001e49ec4_1',               self.room_name + ' Dressing Table Light','Switch',             'Generic Switches')
    self.add_mac_device("sonoff_1001e4a0a0_1",               self.room_name + ' Gateway Power',       'Switch',             "Generic Switches")

#    self.add_mac_device('e0798dba988e',                      self.room_name + ' Bed',                 'Motion Sensor',      'Mijia Motion Sensor 2s')

    # New unused button
    #self.add_mac_device('18c23c25a26c',              self.room_name,                           'Button',             'MiJia Wireless Switch 2', postfix='3')

    #self.add_mac_device('50ec50df0a79',       'Master Room Ceiling Light Bulb 2',  'Light',              'Mijia BLE Lights')

    #self.add_mac_device("54ef44e58958",             self.room_name + " Bed",                 'Motion Sensor',      "Mijia Motion Sensor 2")
    #self.add_mac_device("lumi_hagl04_a19b_curtain", self.room_name + " Curtain",            'Curtain',            "Generic Curtains")
    #self.add_mac_device('mss210_d3bd_outlet',       self.room_name + ' Dressing Table Light', 'Switch',             'Generic Switches')

    self.add_average_temperature_sensor(sensor_1='sensor.master_room_temperature_sensor_new_1', 
                                        sensor_2='sensor.master_room_temperature_sensor_new_2', 
                                        name='Master Room Temperature Sensor')
    
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

  #def get_remote_entities(self):  
  #  super().get_remote_entities()    
  #  self.wall_buttons            = ["sensor." + self.room_entity + "_wall_button_2"]

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
      "binary_sensor.master_room_bed_motion_sensor_motion",
      "binary_sensor.master_room_bed_occupancy_sensor_occupancy",
      #"binary_sensor.master_room_bed_pressure_sensor_1",
      #"binary_sensor.master_room_bed_pressure_sensor_2",
      #"binary_sensor.master_room_bed_pressure_sensor_3",
      #"binary_sensor.master_room_bed_pressure_sensor",
      #"binary_sensor.master_room_occupancy_sensor_occupancy",
      #"binary_sensor.master_room_drawer_occupancy_sensor_occupancy"
    ]
    
    self.all_motion_sensors = self.non_bed_motion_sensors + self.bed_motion_sensors
    
    self.inside_to_outside_timeout = 2*60
    self.sleep_to_outside_timesout = 5*60
    self.inside_to_sleep_timeout   = 5*60 

  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.leds                    = ["light.master_room_drawer_led",
                                    "light.master_room_tv_led",
                                    "light.master_room_bed_led"] 
    
    self.other_lights            = ["switch.master_room_entrance_wall_switch",
                                    "switch.master_room_dressing_table_light"]
    
    self.ceiling_lights          = ["light.master_room_bed_ceiling_light",
                                    "light.master_room_drawer_ceiling_light"]
                                    
    self.lights                  = self.ceiling_lights + self.lamps + self.leds + self.other_lights
    
    # Adaptive lighting
    if self.cfg_adaptive_lighting:
      self.al_light_list[0]["lights"] += self.ceiling_lights + self.lamps

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
    

  # Overwrite scene 'All off' to include turning off blinds
  def callSceneService(self, scene_name):
    scene_service = super().callSceneService(scene_name)

    if scene_name == 'All Off':
      scene_service = [scene_service, self.turn('cover.master_room_blind', "off")]        
      return self.convertToSingleService(scene_service, alias=scene_name)  
    else:
      return scene_service

  def get_remote_entities(self):  
    super().get_remote_entities()
    self.wall_buttons            = ["sensor." + self.room_entity + "_entrance_wall_button"]
    self.buttons                 = self.wall_buttons + self.xiaomi_buttons

    # button states do not work well (not responsive) with template sensor renaming
    # and this usage pressing buttons quickly a lot of time
    self.four_key_buttons        = ['sensor.0x842e14fffe60b64a_action']
    self.eight_key_knob_buttons  = ['sensor.f0a3033b201b_action',
                                    'sensor.cf0c1f9b4dbc_action']

  def gen_room_specific_automations(self):
    self.add_offline_device_automations(
      device_type          = 'Zigbee',
      offline_device       = 'switch.master_toilet_wall_switch',
      gateway_power_switch = 'switch.master_room_gateway_power',
      tts_message          = self.automation_room_name + "2F gateway zigbee devices are offline - Restarting gateway -"
      )

    self.add_offline_device_automations(
      device_type          = 'Wifi',
      offline_device       = 'cover.master_room_blind_1',
      tts_message          = self.automation_room_name + "2F wifi devices are offline. You may want to manual restart 2.4Ghz Wifi."
      )

  def gen_window_automations(self):
    if len(self.windows) > 0:
      self.add_window_open_notification_when_leaving_zone_automations()

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
    self.add_mac_device('0x00158d00047d69be',               self.room_name,                     'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
    self.add_mac_device("a4c1381d6ddb",                     self.room_name,                     'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device('e4aaec80bc19',                     self.room_name + ' Door',           'Door Sensor',        'Mijia2 Contact')
    self.add_mac_device('0x00158d00057b2b4c',               self.room_name + ' Basin',          'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('0x00158d000460247b',               self.room_name + ' Dressing Room',  'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('0x00158d00054750ca',               self.room_name + ' Shower',         'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('mss210_cebd_outlet',               self.room_name + ' Floor LED',      'Switch',             'Generic Switches')
    self.add_mac_device('0x04cf8cdf3c7cc9c4',               self.room_name + ' Mirror Sensor',  'Light Sensor',       'Xiaomi Light Detection Sensor To Mirror Sensor')
    self.add_mac_device("master_toilet_ceiling_light_hue",  self.room_name + " Ceiling Light",  'Light',              "Generic Lights")
    #self.add_mac_device('0x00158d000424f98c',               self.room_name + ' Blind',          'Button',             'MiJia Wireless Switch', integration='Z2M')


    #self.add_mac_device('0x00158d000171756e',      self.room_name + ' Floor LED',             'Switch',             'Mi Power Plug ZigBee')
    # Dressing Room
    self.add_mac_device("0x00158d00042d4092",      self.room_name + " Dressing Room",         'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Single Rocker)")
    self.add_mac_device("28d1272057d5",            self.room_name + " Dressing Room Light",   'Light',              "Mijia BLE Lights")
    self.add_mac_device("0x00158d00070b2f2a",      self.room_name + " Dressing Room Blind",   'Blind',              "Aqara roller shade motor")

  def get_remote_entities(self):  
    super().get_remote_entities()
    # N.B. Xiaomi zigbee button rename using template does not sample very well
    # and this usage pressing buttons quickly a lot of time
    # Use manual rename on the native entity itself
    self.curtain_buttons = ["sensor.master_toilet_blind_button_action"]

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.master_toilet_basin_motion_sensor_motion",
      "binary_sensor.master_toilet_shower_motion_sensor_motion"
    ]

  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.leds                    = ["switch.master_toilet_floor_led"]
    self.lights                  = self.leds + self.lamps + self.ceiling_lights

    # Adaptive lighting
    if self.cfg_adaptive_lighting:
      self.al_light_list[0]["lights"] += self.ceiling_lights + ["light.master_toilet_dressing_room_light"]

  def get_mirror_sensor_entities(self):
    super().get_mirror_sensor_entities()
    self.mirror_sensors          = ["binary_sensor.master_toilet_mirror_sensor"]

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
      f"binary_sensor.{self.room_entity}_table_occupancy_sensor_occupancy",
      f"binary_sensor.{self.room_entity}_worktop_motion_sensor_motion",
      f"binary_sensor.{self.room_entity}_dining_motion_sensor_motion",
      f"binary_sensor.{self.room_entity}_dining_table_motion_sensor_motion",
    ]


  def get_entity_declarations(self):
    super().get_entity_declarations()
    
    self.add_mac_device("582d34828f85",                               self.room_name,                   'Temperature Sensor', "Qingping Lite Temperature Sensor")
    #self.add_mac_device("a4c1380e91a7",                               self.room_name,                   'Temperature Sensor', "Mijia2 Temperature Sensor")     
    self.add_mac_device("curtain_e521",                               self.room_name + " Curtain",      'Curtain',            "Generic Curtains")     
    self.add_mac_device('0x00158d0005210fa9',                         self.room_name + ' Extractor',    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)', switch_rename_dir={2: 'Kitchen Extractor'})
    self.add_mac_device('0x04cf8cdf3c7ad647',                         self.room_name,                   'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Triple Rocker)', flex_switch=[2], switch_rename_dir={3: 'Kitchen Floor LED'})
    self.add_mac_device('mss210_c944_outlet',                         self.room_name + ' Plate Warmer', 'Switch',             'Generic Switches')
    self.add_mac_device('560a_measure_mss310_main_channel',           self.room_name + ' Hot Water',    'Switch',             'Generic Switches')
    self.add_mac_device('52b1_measure_mss310_power_w_main_channel',   'Washing Machine Power',          'Power',              'Generic Power Measurement Switch', power_on_threshold=4)
    #self.add_mac_device('560a_measure_mss310_power_w_main_channel',   'Rice Cooker Power',              'Power',              'Generic Power Measurement Switch', power_on_threshold=4)
    self.add_mac_device('0x00158d00057acaac',                         self.room_name + ' Dining',       'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x00158d0004660308',                         self.room_name + ' Worktop',      'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('54ef44e559c6',                               self.room_name + ' Dining Table', 'Motion Sensor',      'Mijia Motion Sensor 2')
    self.add_mac_device("e4aaec4500e4",                               self.room_name + " Window",       'Window',             "Mijia2 Contact") # belong_to_group=self.windows)
    self.add_mac_device("a4c1381a4361",                               self.room_name + ' Table',        'Motion Sensor',      "Linptech Occupancy Sensor")
    self.add_mac_device("kitchen_ceiling_light_hue",                  self.room_name + " Ceiling Light",'Light',              "Generic Lights")
    self.add_mac_device("kitchen_dining_light_yeelight",              self.room_name + " Dining Light", 'Light',              "Generic Lights")
    self.add_mac_device("kitchen_tv_led_magic_home",                  self.room_name + " TV LED",       'Light',              "Generic Lights")
    self.add_mac_device("34053207483fda906b54",                       self.room_name + " Worktop LED",  'Light',              "Generic Lights")
    self.add_mac_device("18c23c2caa33_water_leak",                    self.room_name + " Water Sensor", 'Binary Sensor',      "Generic Binary Sensor")

    # MCCGQ02HL
    #self.add_mac_device("0x158d00023e6015",       self.room_name + " Worktop",             "Aqara Wireless Switch")     

  def get_window_entities(self):
    super().get_window_entities()
    self.windows                 = [f"binary_sensor.{self.room_entity}_window"]

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

    self.extractor               = ['switch.' + self.room_entity + '_extractor']


  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains               = ["cover." + self.room_entity + "_curtain"] 

  def get_tv_entities(self):
    super().get_tv_entities()
    self.tvs                     = [f"media_player.{self.room_entity}_tv"]
    self.tv_picture_mode         = [f"input_select.{self.room_entity}_tv_picture_mode"]
    self.fire_tvs                = [f"media_player.{self.room_entity}_fire_tv"]      
 

  def gen_wall_button_single_automations(self):
    self.gen_a_button_toggle_automation(      button_state_list=["single_left", "button_1_single"],
                                              button_state_name='Single Left',
                                              device_list="light." + self.room_entity + "_ceiling_light",
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
    room_card['card']['cards'][0]['secondary'] += "{% set vaccum = 'vacuum.x1' %} {% if   is_state(vaccum, 'docked') %}\n 🔋 \n{% elif is_state(vaccum, 'cleaning') %}\n 🧹 \n{% elif is_state(vaccum, 'unavailable') %}\n 🌐 \n{% else %}\n {{states('vacuum.x1')}} \n{% endif %}"
    # Add additional cards
    room_card['card']['cards'][1]['cards']     += ([
      self.getTemplateCard(
        icon       = "mdi:rice",
        icon_color = "{% if is_state(entity, 'on') %}\n  red       \n{% endif %}",
        condition_entity = 'binary_sensor.rice_cooker_power'
      )
    ]) + ([
      self.getTemplateCard(
        icon       = "mdi:washing-machine",
        icon_color = "{% if is_state(entity, 'on') %}\n  blue       \n{% endif %}",
        condition_entity = 'binary_sensor.washing_machine_power'
      )
    ]) + ([
      self.getTemplateCard(
        icon       = "mdi:ice-cream",
        icon_color = "{% if is_state(entity, 'on') %}\n  yellow       \n{% endif %}",
        condition_entity = 'switch.kitchen_ice_maker'
      )
    ]) + ([
      self.getTemplateCard(
        icon       = "hass:fan",
        icon_color = "{% if is_state(entity, 'on') %}\n  cyan       \n{% endif %}",
        condition_entity = 'switch.kitchen_extractor'
      )
    ]) + ([
      self.getTemplateCard(
        icon       = "hass:fan",
        icon_color = "{% if is_state(entity, 'cleaning') %}\n  cyan       \n{% endif %}",
        condition_entity = 'vacuum.x1',
        condition_state  = 'cleaning'
      )
    ])
    
    return room_card


#class BoilerRoom(RoomBase):
#  def get_room_config(self):
#    super().get_room_config()
#    self.room_name             = 'Boiler Room'    
#    self.room_short_name       = 'BR'
#    # Enables
#    self.cfg_scene                  = True            
#    self.cfg_group_auto             = True       
#    self.cfg_motion_light           = True
#
#
#    
#

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

    self.add_average_temperature_sensor(sensor_1='sensor.living_room_temperature_sensor_1', 
                                        sensor_2='sensor.living_room_temperature_sensor_1', 
                                        name='Living Room Temperature Sensor')


    self.add_mac_device("a4c138c69e9f",                       self.room_name + ' TV',            'Motion Sensor',      "Linptech Occupancy Sensor")
    self.add_mac_device("a4c1381b8035",                       self.room_name + ' Sofa',          'Motion Sensor',      "Linptech Occupancy Sensor")

    self.add_mac_device('0x00158d0003140ea8',                 self.room_name + ' Entrance',      'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device("dced8308e951",                       self.room_name,                    'Motion Sensor',      "Ziqing Occupancy Sensor")
  # self.add_mac_device('0x54ef441000792d1d',                 self.room_name + ' Sofa',          'Pressure Sensor 1',  'Aqara Pressure Sensor')    
    self.add_mac_device("2ab7",                               self.room_name,                    'Temperature Sensor', "Mijia2 Temperature Clock",  postfix='1', integration='Passive BLE Monitor')
    #self.add_mac_device("a4c13864aca3",                       self.room_name,                    'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device('0x00158d0008d8ead8',                 self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', flex_switch=True)
    self.add_mac_device("0x54ef441000452fd8",                 self.room_name + ' Curtain',       'Curtain',            "Aqara B1 curtain motor",    postfix='1')
    self.add_mac_device("0x54ef4410001f409c",                 self.room_name + ' Curtain',       'Curtain',            "Aqara B1 curtain motor",    postfix='2')
    self.add_mac_device('0x04cf8cdf3c7b560f',                 self.room_name,                    'Light Sensor',       'Xiaomi Light Detection Sensor')
    self.add_mac_device('0x00158d000424f995',                 self.room_name,                    'Button',             'MiJia Wireless Switch')
    self.add_mac_device("sonoff_1001e49906_1",                self.room_name + ' Gateway Power', 'Switch',             "Generic Switches")
    self.add_mac_device("e4aaec80beca",                       self.room_name + " Window",        'Window',             "Mijia2 Contact") 
    self.add_mac_device("e4aaec80bedb",                       self.room_name + " Sliding Door",  'Door',               "Mijia2 Contact") 
    #self.add_mac_device('0x00158d000451f90b',                 self.room_name + ' Desk',          'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('d44867b89dd3',                       self.room_name + ' Desk',          'Motion Sensor',      'Xiaomi Occupancy Sensor')
    self.add_mac_device('sonoff_1001e49dd9_1',                self.room_name + ' Desk Screen LED', 'Switch',           'Generic Switches')
    self.add_mac_device('0x00158d00054d83df',                 'Boiler Room',                     'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('28d127202ef6',                       'Boiler Room Light',               'Light',              'Mijia BLE Lights')
    #self.add_mac_device("living_room_ceiling_light_yeelight",  self.room_name + ' Ceiling Light','Light',              "Generic Lights") # Yeelight integration
    self.add_mac_device("yeelink_ceil30_3a4b_light",           self.room_name + ' Ceiling Light','Light',              "Generic Lights")  # MiIoT Auto integration
    self.add_mac_device("hue_color_lamp_1",                    self.room_name + " Floor Light 1",'Light',              "Generic Lights")
    self.add_mac_device("hue_color_lamp_2",                    self.room_name + " 3 Head Lamp 1",'Light',              "Generic Lights")
    self.add_mac_device("hue_color_lamp_3",                    self.room_name + " 3 Head Lamp 2",'Light',              "Generic Lights")
    self.add_mac_device("hue_color_lamp_4",                    self.room_name + " 3 Head Lamp 3",'Light',              "Generic Lights")
    self.add_mac_device('ef0f_29831979_mss210_main_channel',   self.room_name + ' Floor Light 3','Switch',             'Generic Switches')

#('0x00158d0004501b0a', 'Living Room Sofa',           'Aqara Motion and Illuminance Sensor')
#('0x00158d0001212747', 'Boiler Room',                'Aqara Door & Window Sensor')

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.other_motion_sensors = [
      f"binary_sensor.{self.room_entity}_desk_occupancy_sensor_occupancy",
      f"binary_sensor.{self.room_entity}_tv_occupancy_sensor_occupancy",
      f"binary_sensor.{self.room_entity}_sofa_occupancy_sensor_occupancy",
      f"binary_sensor.{self.room_entity}_entrance_motion_sensor_motion", 
    ]

    self.entrance_motion_sensors = [
      f"binary_sensor.{self.room_entity}_entrance_motion_sensor_motion",
      f"binary_sensor.{self.room_entity}_sliding_door"
    ]

    self.all_motion_sensors = self.other_motion_sensors + self.entrance_motion_sensors

  def get_window_entities(self):
    super().get_window_entities()
    self.windows                 = [#f"binary_sensor.{self.room_entity}_sliding_door",
                                    f"binary_sensor.{self.room_entity}_window"]

  def get_tv_entities(self):
    super().get_tv_entities()
    self.tvs                     = [f"media_player.{self.room_entity}_tv"]
    self.tv_picture_mode         = [f"input_select.{self.room_entity}_tv_picture_mode"]
    self.tv_soundbars            = [f"media_player.{self.room_entity}_sonos"]
    self.fire_tvs                = [f"media_player.{self.room_entity}_fire_tv"]      

  def get_remote_entities(self):  
    super().get_remote_entities()
    self.eight_key_knob_buttons  = ['sensor.df8c562a81a6_action']

  def get_light_entities(self):
    super().get_light_entities()
    self.leds                    = [#"light.living_room_tv_led", 
                                    #"light.living_room_sofa_led",
                                    f"switch.{self.room_entity}_floor_light_3"] 
    self.lamps                   = [f"light.{ self.room_entity}_floor_light_1", 
                                    f"light.{ self.room_entity}_floor_light_2"]

    self.lights                  = self.leds + self.lamps + self.ceiling_lights
    # Adaptive lighting
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
                        self.turn(self.tvs, tv_brightness=2)]      
      return self.convertToSingleService(scene_service, alias=scene_name)                          
    else:
      return super().callSceneService(scene_name)
    

  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains               = [ f"cover.{self.room_entity}_curtain_1",
                                    f"cover.{self.room_entity}_curtain_2"] 

  def gen_room_specific_automations(self):
    self.add_offline_device_automations(
      device_type          = 'Zigbee',
      offline_device       = f'switch.{self.room_entity}_wall_switch',
      gateway_power_switch = f'switch.{self.room_entity}_gateway_power',
      tts_message          = self.automation_room_name + "0F gateway zigbee devices are offline. Restarting gateway."
      )

    self.add_offline_device_automations(
      device_type          = 'Wifi',
      offline_device       = 'light.kitchen_worktop_led',
      tts_message          = self.automation_room_name + "0F wifi devices are offline. You may want to manual restart 2.4Ghz Wifi."
      )

  def gen_window_automations(self):
    if len(self.windows) > 0:
      self.add_window_open_notification_when_leaving_zone_automations()
      self.add_window_open_notification_when_going_to_sleep_automations()

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_default_root = 'living-room'
    self.dashboard_view_name = 'living-room'
    self.room_icon           = 'mdi:youtube-tv'


class Garden(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name              = 'Garden'    
    self.room_short_name        = 'GD'
    self.cfg_occupancy          = True       
    self.cfg_group_auto         = True
    self.cfg_scene              = True            
    self.cfg_motion_light       = True

  def get_room_name_and_property(self):  
    super().get_room_name_and_property()
    self.room_type              = 'landing'

  def get_light_entities(self):
    super().get_light_entities()
    self.ceiling_lights          = ["switch.garden_ceiling_light"]

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
    self.add_mac_device('54ef44e34c16',           self.room_name + ' Bike Shed',      'Motion Sensor', 'Mijia Motion Sensor 2s')
    self.add_mac_device('0x00158d000548b8a5',     self.room_name + ' Sliding Door',   'Motion Sensor', 'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x00158d000522e00e',     self.room_name,                     'Wall Switch',   'Aqara D1 Wall Switch (With Neutral, Double Rocker)', switch_rename_dir={2: 'Garden Ceiling Light'})
    self.add_mac_device('mss425e_5df5_outlet_1',  self.room_name + ' Spotlight 1',    'Switch',        'Generic Switches')
    #self.add_mac_device('mss425e_5df5_outlet_2',  self.room_name + ' Spotlight 2',    'Switch',        'Generic Switches')
    #self.add_mac_device('mss425e_5df5_outlet_3',  self.room_name + ' Spotlight 3',    'Switch',        'Generic Switches')
    self.add_mac_device('a4c1386b73af_water_leak',self.room_name + ' Rain Sensor',    'Sensor',        'Generic Binary Sensor')



  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_default_root = 'lovelace-garden'
    self.dashboard_view_name = 'garden'
    self.room_icon           = 'mdi:beach'


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
    #self.add_mac_device('0x00158d000403d6c0',              self.room_name,                       'Button',              'MiJia Wireless Switch')
    self.add_mac_device("0x04cf8cdf3c797717",              self.room_name + " Six Key Button 1", 'Button',              "Aqara Opple switch 3 bands", integration='Z2M')
    self.add_mac_device('0x00158d00047d69e6',              self.room_name,                       'Wall Switch',         'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
    self.add_mac_device("dced8308f496",                    self.room_name,                       'Motion Sensor',       "Ziqing Occupancy Sensor")
    self.add_mac_device('0x00158d00057b37be',              self.room_name + ' Entrance',         'Motion Sensor',       'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x00158d000423319f',              self.room_name + ' Floor 1',          'Motion Sensor',       'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('54ef44e58108',                    self.room_name + ' Floor 2',          'Motion Sensor',       'Mijia Motion Sensor 2')
    #self.add_mac_device('54ef44e559c6',                    self.room_name + ' Bed',              'Motion Sensor',       'Mijia Motion Sensor 2')
    self.add_mac_device('54ef44e58345',                    self.room_name + ' Bed',              'Motion Sensor',       'Mijia Motion Sensor 2')
    self.add_mac_device("a4c138b0eb53",                    self.room_name,                       'Temperature Sensor',  "Mijia2 Temperature Sensor")
    self.add_mac_device("curtain_d29a",                    self.room_name + " Curtain",          'Curtain',             "Generic Curtains")     
    self.add_mac_device("e27w_1_hue",                      self.room_name + " Lamp 1",           'Light',               "Generic Lights")
    self.add_mac_device("e27w_2_hue",                      self.room_name + " Lamp 2",           'Light',               "Generic Lights")
    self.add_mac_device("en_suite_room_ceiling_light_hue", self.room_name + " Ceiling Light", 'Light',               "Generic Lights")


  def get_tv_entities(self):
    super().get_tv_entities()
    self.tv_room_entity          = 'portable'
    self.tvs                     = [f"media_player.{self.tv_room_entity}_tv"]
    self.tv_picture_mode         = [f"input_select.{self.tv_room_entity}_tv_picture_mode"]
    self.fire_tvs                = [f"media_player.{self.tv_room_entity}_fire_tv"]      


  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.en_suite_room_bed_motion_sensor_motion",
      "binary_sensor.en_suite_room_entrance_motion_sensor_motion",
      'binary_sensor.en_suite_room_floor_1_motion_sensor_motion',
      'binary_sensor.en_suite_room_floor_2_motion_sensor_motion',
      "binary_sensor.en_suite_room_occupancy_sensor_occupancy"
    ]
    
    self.non_bed_motion_sensors = ['binary_sensor.en_suite_room_floor_1_motion_sensor_motion',
                                   'binary_sensor.en_suite_room_floor_2_motion_sensor_motion']

  def get_remote_entities(self):  
    super().get_remote_entities()
    # button states do not work well (not responsive) with template sensor renaming
    # and this usage pressing buttons quickly a lot of time
    #self.six_key_buttons = ['sensor.0x04cf8cdf3c797717_0x04cf8cdf3c797717_action',
    #                        'sensor.0x04cf8cdf3c7976f8_0x04cf8cdf3c7976f8_action']
    self.eight_key_knob_buttons  = ['sensor.d5154864a1bb_action',
                                    'sensor.ce327cd55cd0_action']
  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
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

  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("0x158d00053fdaba",   self.room_name + ' Door',  'Door',               "Aqara Door & Window Sensor")
    self.add_mac_device('0x158d000572839f',   self.room_name,            'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x158d000522d90c',   self.room_name,            'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
    self.add_mac_device("582d34828cc6",       self.room_name,            'Temperature Sensor', "Qingping Lite Temperature Sensor")

  def get_light_entities(self):
    super().get_light_entities()

    # Adaptive lighting
    self.al_light_list[0]["lights"] += self.ceiling_lights

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.en_suite_toilet_motion_sensor_motion"
    ]


  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_default_root = 'en-suite-room'
    self.dashboard_view_name = 'en-suite-toilet'
    self.room_icon           = 'mdi:shower-head'

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


  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("582d343483e9",       self.room_name,                    'Temperature Sensor', "Qingping Temperature Sensor")
    self.add_mac_device('0x00158d00047b69d2', self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', flex_switch=True)
    #self.add_mac_device("50ec50dd67be",       self.room_name + " Lamp",          'Light',              "Generic Lights")
    self.add_mac_device("28d12735ea1e",       self.room_name + " Ceiling Light", 'Light',              "Mijia BLE Lights")
    self.add_mac_device("hue_ambiance_lamp_2",self.room_name + " Lamp 1",        'Light',              "Generic Lights")
    self.add_mac_device("hue_ambiance_lamp_3",self.room_name + " Lamp 2",        'Light',              "Generic Lights")
    self.add_mac_device('18c23c27fc55',       self.room_name + ' Entrance',      'Motion Sensor',      'Mijia Motion Sensor 2')
    self.add_mac_device("dced8308f596",       self.room_name,                    'Motion Sensor',      "Ziqing Occupancy Sensor")    
    self.add_mac_device('e0798dba9ae1',       self.room_name + ' Bed',           'Motion Sensor',      'Mijia Motion Sensor 2')
    # This Ziqing Occupancy Sensor is Out of Order
    #self.add_mac_device("dced8309090d",       self.room_name,                    'Motion Sensor',      "Ziqing Occupancy Sensor")
    #self.add_mac_device('18c23c25a26c',       self.room_name,                    'Button',             'MiJia Wireless Switch 2', postfix='1')
    #self.add_mac_device('18c23c246426',       self.room_name,                    'Button',             'MiJia Wireless Switch 2', postfix='1')
    #self.add_mac_device('18c23c2826fc',       self.room_name,                    'Button',             'MiJia Wireless Switch 2', postfix='2')
    self.add_mac_device("curtain_1050",       self.room_name + " Curtain",       'Curtain',            "Generic Curtains")     

  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains               = [ "cover.guest_room_curtain"] 

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.guest_room_entrance_motion_sensor_motion",
      "binary_sensor.guest_room_bed_motion_sensor_motion",
      "binary_sensor.guest_room_occupancy_sensor_occupancy"
    ]


  def get_remote_entities(self):  
    super().get_remote_entities()
    # button states do not work well (not responsive) with template sensor renaming
    # and this usage pressing buttons quickly a lot of time
    self.eight_key_knob_buttons  = ['sensor.ca6e1b6a8f89_action']


  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    #self.leds                    = ["light.guest_room_bed_led"]
    self.lamps                   = ["light.guest_room_lamp_1",
                                    "light.guest_room_lamp_2"]
    self.lights                  = self.leds + self.lamps + self.ceiling_lights

    # Adaptive lighting
    self.al_light_list[0]["lights"] += self.ceiling_lights + self.lamps


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
      "binary_sensor.guest_toilet_motion_sensor_motion",
      "binary_sensor.guest_toilet_shower_motion_sensor_motion",
    ]

  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.leds                    = ["switch.guest_toilet_floor_led"]
    self.lights                  = self.leds + self.lamps + self.ceiling_lights
    self.extractor               = ['switch.' + self.room_entity + '_extractor']

    # Adaptive lighting
    self.al_light_list[0]["lights"] += self.ceiling_lights 


  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("a4c1387a7b78",                   self.room_name,                    'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device('0x00158d000487851a',             self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)', integration='Z2M')
    self.add_mac_device("guest_toilet_ceiling_light_hue", self.room_name + " Ceiling Light", 'Light',              "Generic Lights")
    self.add_mac_device('0x00158d0008d94c10',             self.room_name + ' Extractor',     'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', switch_rename_dir={1: 'Guest Toilet Extractor'})
    self.add_mac_device('54ef44e3237b',                   self.room_name + ' Shower',        'Motion Sensor',      'Mijia Motion Sensor 2')
    # guest toilet mirrormirror deminister sensor    a4c138cfc701 
    #    - en-suite toilet mirror

#('0x00158d00052b35f7', 'Guest Toilet',               'Aqara Motion and Illuminance Sensor')
#('0x00158d00053e96ae', 'Guest Toilet',               'Aqara Door & Window Sensor')


  # Guest Toilet - Left key - Ceiling light
  # Guest Toilet - Right key - Floor LED
  def gen_wall_button_single_automations(self):
    self.gen_a_button_toggle_automation(      button_state_list=["single_left"],
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

  def get_light_entities(self):
    super().get_light_entities()
    #self.leds                   =  ["switch.study_screen_light"] 
    #self.lamps                   = ["switch.study_studio_lamp"] 
    self.lights                  = self.leds + self.lamps + self.ceiling_lights

    # Adaptive lighting
    if self.cfg_adaptive_lighting:
      self.al_light_list[0]["lights"] += self.ceiling_lights 

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.study_motion_sensor_motion",
      "binary_sensor.study_desk_motion_sensor_motion"
    ]

  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains            = [ "cover.study_blind"] 

  def get_remote_entities(self):  
    super().get_remote_entities()
    # N.B. Xiaomi zigbee button rename using template does not sample very well
    # Use manual rename on the native entity itself
    self.curtain_buttons = ["sensor.study_button"]

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_default_root = 'lovelace-misc'
    self.dashboard_view_name = 'study'
    self.room_icon           = 'mdi:desk'

  def get_entity_declarations(self):
    super().get_entity_declarations()
    
    #self.add_mac_device("a4c138cfc701",               self.room_name,                     'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device("582d34828cc1",               self.room_name,                     'Temperature Sensor', "Qingping Lite Temperature Sensor")
    self.add_mac_device('0x00158d00045245be',         self.room_name,                     'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', integration='Z2M', flex_switch=True)
    self.add_mac_device("0x00158d00070b2f26",         self.room_name + ' Blind',          'Curtain',            "Aqara roller shade motor")
    self.add_mac_device("mss210_b083_outlet",         self.room_name + ' Studio Lamp 1',  'Switch',             "Generic Switches")
    self.add_mac_device('18c23c282711',               self.room_name,                     'Button',             'MiJia Wireless Switch 2')
    self.add_mac_device('18c23c26ea40',               self.room_name + ' Desk',           'Motion Sensor',      'Mijia Motion Sensor 2')
    self.add_mac_device('sonoff_10020aa912_1',        self.room_name + ' Screen Light',   'Switch',             'Generic Switches')
    self.add_mac_device('0x00158d000171756e_power',   'Feeding Bottle Warmer',            'Power',              'Generic Power Measurement Switch', power_on_threshold=1.5)
    self.add_mac_device("0x00158d000171756e_plug",    'Feeding Bottle Warmer',            'Switch',             "Generic Switches")
    self.add_mac_device("sonoff_1001e49ade_1",         self.room_name + ' Gateway Power', 'Switch',            "Generic Switches")

    # This Meross switch is Out-of-Order
    #self.add_mac_device("mss210_ce70_outlet", self.room_name + ' Studio Lamp 2',   'Switch',            "Generic Switches")
  

  def gen_room_specific_automations(self):
    self.add_offline_device_automations(
      device_type          = 'Zigbee',
      offline_device       = 'switch.guest_room_wall_switch',
      gateway_power_switch = 'switch.study_gateway_power',
      tts_message          = self.automation_room_name + "1F gateway zigbee devices are offline. Restarting gateway."
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
    self.cfg_occupancy          = True       
    self.cfg_group_auto         = True
    self.cfg_temp_control       = True
    self.cfg_remote_light       = True
    self.cfg_adaptive_lighting  = True

  def get_room_name_and_property(self):  
    super().get_room_name_and_property()
    self.room_type              = 'landing'
    
  def get_entity_declarations(self):
    super().get_entity_declarations()

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.ground_corridor_motion_sensor_motion",
      "binary_sensor.first_corridor_motion_sensor_motion",
      "binary_sensor.en_suite_room_entrance_motion_sensor_motion",
      "binary_sensor.living_room_entrance_motion_sensor_motion",
      "binary_sensor.master_room_entrance_motion_sensor_motion"
    ]

  def get_light_entities(self):
    super().get_light_entities()
    # Adaptive lighting
    self.al_light_list[0]["lights"] += self.ceiling_lights


  def get_remote_entities(self):  
    super().get_remote_entities()
    self.wall_buttons            = ["sensor.ground_corridor_wall_button",
                                    "sensor.first_corridor_wall_button"]
    self.buttons                 = self.wall_buttons


  def get_entity_declarations(self):
    super().get_entity_declarations()
    #self.add_mac_device("xxxxxxxxxxxx",       self.room_name,               'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device('50ec50ded70f',       'First Corridor BLE Light',    'Light',              'Mijia BLE Lights')
    self.add_mac_device('50ec50df9323',       'Ground Corridor BLE Light',   'Light',              'Mijia BLE Lights')
    self.add_mac_device('0x00158d00045019fd', 'Ground Corridor',             'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x00158d0004525183', 'First Corridor',              'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x00158d00048783e5', 'Ground Corridor',             'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)', flex_switch=[1])
    self.add_mac_device('0x00158d0005210fcf', 'First Corridor',              'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)', flex_switch=[2])
    
#('0x00158d00045f640a', 'Upstairs Heating',           'Aqara Single Key Wired Wall Switch Without Neutral Wire')
#('0x00158d0005227632', 'Downstairs Heating',         'Aqara D1 Wall Switch (With Neutral, Double Rocker)')

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_default_root = 'lovelace-misc'
    self.dashboard_view_name = 'corridors'
    self.room_icon           = 'mdi:toilet'

  # Customize card information
  def getNavigationRoomCard (self):
    room_card = super().getNavigationRoomCard()
    # Add vaccum info
    room_card['card']['cards'][0]['secondary'] = "🔔 {{states.sensor.front_door_battery.state}}%" +  room_card['card']['cards'][0]['secondary']
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
    self.all_motion_sensors = [
      "binary_sensor.ground_toilet_occupancy_sensor_occupancy"
    ]
    # Linptech ES3 is good enough to detect if people is out
    self.turn_to_outside_when_no_motion = 'yes'

  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("a4c1387c09bd",                    self.room_name,                                'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device("a4c1385ab801",                    self.room_name,                                'Motion Sensor',      "Linptech Occupancy Sensor")
    #self.add_mac_device('0x00158d0004667569',              self.room_name,                                'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device("0x00158d0005435643",              self.room_name,                                'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Double Rocker)")
    self.add_mac_device('0x00158d00053fdaa8',              self.room_name + ' Door',                      'Door',               'Aqara Door & Window Sensor')
  # self.add_mac_device("0x90fd9ffffe8e24b6",              self.room_name + " Ceiling Light Spotlight 1", 'Light',              "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum", integration='Z2M')
  # self.add_mac_device("0x000b57fffee8e6b4",              self.room_name + " Ceiling Light Spotlight 2", 'Light',              "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum", integration='Z2M')
    self.add_mac_device("ground_toilet_ceiling_light_z2m", self.room_name + " Ceiling Light",             'Light',              "Generic Lights")

  def get_light_entities(self):
    super().get_light_entities()
    # Adaptive lighting
    self.al_light_list[0]["lights"] += self.ceiling_lights 


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
    type = 'mushroom'

    if type == 'mushroom':
       room_card = { 
        "type": "custom:stack-in-card",
        "mode": "vertical",
        "cards": [
          {
            "type": "custom:mushroom-template-card",
            "icon": "mdi:server",
            "icon_color": "blue",
            "layout": "horizontal",
            "entity": "input_boolean.placeholder",
            "fill_container": True,
            "primary": "System",
            "secondary": "{{states('sensor.processor_use_percent')}}% | {{states('sensor.load_1m')}} | {{(states('sensor.memory_use') | float/1000) | round(1) }}GB ",
            "tap_action": {
              "action": "navigate",
              "navigation_path": "/lovelace-system/system"
            }
          },
          self.getCardModColor("transparent") | {
            "type": "custom:stack-in-card",
            "mode": "horizontal",
            "cards": [
              self.getTemplateCard(
                icon       = "mdi:desktop-classic",
                icon_color = "{% if   is_state(entity, 'on') %} amber {% endif %}",
                tap_entity = 'switch.gaming_pc',
                tap_action = 'more-info'
              ),
              #self.getTemplateCard(
              #  icon       = "mdi:television-box",
              #  icon_color = "{% if   is_state(entity, 'on') %} deep-orange {% endif %}",
              #  tap_entity = 'binary_sensor.fire_tv_streaming_pc_contents',                
              #  tap_action = 'more-info'
              #),
              self.getTemplateCard(
                icon       = "mdi:car",
                icon_color = "{% if   is_state(entity, 'on') %} green {% endif %}",
                tap_entity = 'binary_sensor.car_s_unlocked',
                tap_action = 'more-info'
              ),
              self.getTemplateCard(
                icon       = "mdi:home-floor-l",
                icon_color = "red",
                condition_state  = 'on',
                condition_entity = 'switch.downstairs_heating'
              ),
              self.getTemplateCard(
                icon       = "mdi:home-floor-1",
                icon_color = "red",
                condition_state  = 'on',
                condition_entity = 'switch.upstairs_heating'
              ),
              self.getTemplateCard(
                icon       = "mdi:water-boiler",
                icon_color = "red",
                condition_state  = 'on',
                condition_entity = 'switch.water_heater'
              )
              #{
              #  "type": "custom:mushroom-entity-card",
              #  "entity": "switch.gaming_pc",
              #  "icon": "mdi:desktop-classic",
              #  "icon_color": "amber",
              #  "primary_info": "state",
              #  "secondary_info": "none",
              #  "tap_action": {
              #    "action": "more-info"
              #  }
              #},
              #{
              #  "type": "custom:mushroom-entity-card",
              #  "entity": "binary_sensor.fire_tv_streaming_pc_contents",
              #  "icon": "mdi:television-box",
              #  "icon_color": "deep-orange",
              #  "primary_info": "state",
              #  "secondary_info": "none",
              #  "tap_action": {
              #    "action": "more-info"
              #  }
              #}
            ]
          }
        ]
      }
      
    elif type == 'button':
      room_card =  {
        "type": "custom:button-card",
        "aspect_ratio": "1/1",
        "tap_action": {
          "action": "navigate",
          "navigation_path": self.dashboard_view_path
        },
        "entity": "input_boolean.placeholder",
        "show_state": False,
        "name": self.room_name,
        "icon": self.room_icon,
        "show_icon": True,
        "show_name": True
      }

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
    self.add_mac_device("582d34376b04",                      self.room_name,                          'Temperature Sensor', "Qingping Temperature Sensor", postfix='new_1')
    self.add_mac_device("582d343b6a27",                      self.room_name,                          'Temperature Sensor', "Qingping Temperature Sensor", postfix='new_2')
  # self.add_mac_device('0x54ef441000792d09',                self.room_name + ' Bed',                 'Pressure Sensor',    'Aqara Pressure Sensor')    
  # self.add_mac_device('e4aaec755efa',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='1')    
  # self.add_mac_device('e4aaec755f4b',                      self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='2')    
    self.add_mac_device("dced830908fb",                      self.room_name,                          'Motion Sensor',      "Ziqing Occupancy Sensor")
    self.add_mac_device("0x00158d0005228ba8",                self.room_name + " TV",                  'Motion Sensor',      "Aqara Motion and Illuminance Sensor")
    self.add_mac_device('50ec50df3056',                      self.room_name + " Bed Ceiling Light",   'Light',              'Mijia BLE Lights')
    self.add_mac_device("master_room_drawer_ceiling_light_xiaomi",self.room_name + " Drawer Ceiling Light",'Light',"Generic Lights")
    self.add_mac_device("hue_color_lamp_5",                  self.room_name + " Lamp 1",              'Light',              "Generic Lights")
    self.add_mac_device("hue_color_lamp_6",                  self.room_name + " Lamp 2",              'Light',              "Generic Lights")
    self.add_mac_device("master_room_bed_led_magic_home",    self.room_name + " Bed LED",             'Light',              "Generic Lights")
    self.add_mac_device("master_room_tv_led_magic_home",     self.room_name + " TV LED",              'Light',              "Generic Lights")
    self.add_mac_device("master_room_drawer_led_magic_home", self.room_name + " Drawer LED",          'Light',              "Generic Lights")
    self.add_mac_device("0x04cf8cdf3c73a19b",                self.room_name + " Curtain",             'Curtain',            "Aqara B1 curtain motor")
    #self.add_mac_device('18c23c24681a',                      self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='1')
    self.add_mac_device('18c23c25a26c',                      self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='1')
    self.add_mac_device('18c23c25960b',                      self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='2')
    self.add_mac_device("0x04cf8cdf3c7ad638",                self.room_name,                          'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Triple Rocker)", flex_switch=[2,3])
    self.add_mac_device('sonoff_1001e49ec4_1',               self.room_name + ' Dressing Table Light','Switch',             'Generic Switches')
    self.add_mac_device("sonoff_1001e4a0a0_1",               self.room_name + ' Gateway Power',       'Switch',             "Generic Switches")

    self.add_mac_device('e0798dba988e',                      self.room_name + ' Bed',                 'Motion Sensor',      'Mijia Motion Sensor 2')

    # New unused button
    #self.add_mac_device('18c23c25a26c',              self.room_name,                           'Button',             'MiJia Wireless Switch 2', postfix='3')

    #self.add_mac_device('50ec50df0a79',       'Master Room Ceiling Light Bulb 2',  'Light',              'Mijia BLE Lights')

    #self.add_mac_device("54ef44e58958",             self.room_name + " Bed",                 'Motion Sensor',      "Mijia Motion Sensor 2")
    #self.add_mac_device("lumi_hagl04_a19b_curtain", self.room_name + " Curtain",            'Curtain',            "Generic Curtains")
    #self.add_mac_device('mss210_d3bd_outlet',       self.room_name + ' Dressing Table Light', 'Switch',             'Generic Switches')

    self.add_average_temperature_sensor(sensor_1='sensor.master_room_temperature_sensor_new_1', 
                                        sensor_2='sensor.master_room_temperature_sensor_new_2', 
                                        name='Master Room Temperature Sensor')
    
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


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
#    Shared Lovelace                      
#
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@





class Dashboard(RoomBase):
  def __init__ (self, format=None, dashboard_type=None, dashboard_language=None):
    print ("-------------------------------------")
    print ("** Generating Overall Lovelace Configs. **")
    self.format             = 'yaml'   if format         == None else format
    self.dashboard_type     = 'mobile' if dashboard_type == None else dashboard_type
    self.room_nav_cards = []
    self.dashboard = {}
    self.views = []
    self.rooms = [ 
              LivingRoom(      dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              Kitchen(         dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              MasterRoom(      dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              MasterToilet(    dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              Study(           dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              System(          dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              GroundToilet(    dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              Corridor(        dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              Garden(          dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              EnSuiteRoom(     dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              EnSuiteToilet(   dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              GuestRoom(       dashboard_type=dashboard_type, dashboard_language=dashboard_language),
              GuestToilet(     dashboard_type=dashboard_type, dashboard_language=dashboard_language)]
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
    
    yaml.Dumper.ignore_aliases = lambda *args : True
    
    # File Path
    self.script_dir         = os.path.dirname(os.path.realpath(__file__))
    if self.format == 'yaml':
      self.auto_gen_config_path = self.script_dir + "/../lovelace/auto_gen_overall_dashboard.yaml"
    else: # json
      # this does not work. have to use GUI to copy the yaml dashboard
      self.auto_gen_config_path = self.script_dir + "/../.storage/lovelace.dashboard_mobile"


    # Open a new file and write automation
    f = open(self.auto_gen_config_path, "w")
    if self.format == 'yaml':
      f.write(yaml.dump(self.dashboard, sort_keys=False, width=float("inf")))
    else: # json
      json.dump(self.dashboard, f, sort_keys=False, indent=2)
    f.close()



##################################################################
#   Check core.entity_entries duplicated automation entities
##################################################################
orig_core_entities_dict    = {}
updated_core_entities_dict = {}

def read_core_entity_entries_json ():
  global orig_core_entities_dict
  global updated_core_entities_dict
  
  # File Path 
  script_dir         = os.path.dirname(os.path.realpath(__file__))
  core_entities_path = script_dir + "/../.storage/core.entity_registry"

  # Open a new file and write automation
  f = open(core_entities_path)

  # returns JSON object as 
  # a dictionary
  orig_core_entities_dict    = json.load(f)
  # Copy - not just a shallow copy of the top most dictory but a deep copy
  updated_core_entities_dict = copy.deepcopy(orig_core_entities_dict)
  
  f.close()
  

def check_core_entity_unexpected_entities():
  global orig_core_entities_dict
  global updated_core_entities_dict

  # Check if core.entity_entires have unexpected entities
  for entity in orig_core_entities_dict['data']['entities']:
    # Check if entity has duplicated automations
    if entity['entity_id'].startswith('automation.z') and entity['entity_id'].endswith('_2'):      
      print (entity['entity_id'])
    # Check if entity has duplicated entities
    if args.check_auto_system_config:
        if entity['entity_id'].endswith('_2'):      
          print (entity['entity_id'])
    

def remove_core_entity_unexpected_entities():
  global orig_core_entities_dict
  global updated_core_entities_dict

  # Reset entities list
  updated_core_entities_dict['data']['entities'] = []
  #print (updated_core_entities_dict['data']['entities'])

  # Copy all entities other than auto generated automation
  for entity in orig_core_entities_dict['data']['entities']:
    if not entity['entity_id'].startswith('automation.z'):
      #print (entity['entity_id'])
      updated_core_entities_dict['data']['entities'] += [entity]


def write_core_entity_entries_json():
  global orig_core_entities_dict
  global updated_core_entities_dict
  
  # File Path 
  script_dir         = os.path.dirname(os.path.realpath(__file__))
  core_entities_path = script_dir + "/core.entity_registry"

  # Dump json database
  with open(core_entities_path, 'w') as json_file:
      json.dump(updated_core_entities_dict, json_file, indent=2)
  print ("A updated core.entity_registry with no duplicated automation is generated at: " + core_entities_path)
  print ("Please manually run cp " + core_entities_path + ' ~/config/.storage')

##################################################################
#  Add command line options and run based on options
##################################################################

parser = argparse.ArgumentParser()
parser.add_argument('-R', dest ='render_auto_config', default=True, 
                    action ='store_false', help ='Skip rendering auto-generated yaml config')
parser.add_argument('-C', dest ='check_auto_system_config', default=True, 
                    action ='store_false', help ='Skip checking on unexpected entities in the system file core.entity_entries')
parser.add_argument('-c', dest ='create_system_config', default=False, 
                    action ='store_true', help ='Create a system file core.entity_entries that removes unexpected entities')
parser.add_argument('-d', '-dy', '-dyaml', dest ='render_dashboard_yaml', default=False, 
                    action ='store_true', help ='Render lovelace config files to YAML format. Default to false as it takes extra time and lovelace are not updated often')
parser.add_argument('-dj', '-djson', dest ='render_dashboard_json', default=False, 
                    action ='store_true', help ='Render lovelace config files to JSON format. Default to false as it takes extra time and lovelace are not updated often')
parser.add_argument('-dm', '-dmobile', dest ='render_dashboard_mobile', default=False, 
                    action ='store_true', help ='Render mobile dashboard. Default to false as it takes extra time and lovelace are not updated often')
parser.add_argument('-dt', '-dtablet', dest ='render_dashboard_tablet', default=False, 
                    action ='store_true', help ='Render tablet dashboard. Default to false as it takes extra time and lovelace are not updated often')
parser.add_argument('-lc', '-language-chinese', dest='dashboard_language_chinese', default=False,
                    action ='store_true', help ='Render dashboard in Chinese. Default to false as it takes extra time and lovelace are not updated often')

args = parser.parse_args()

if args.render_auto_config :
  render_package_for_rooms = [ 
            LivingRoom(),
            Kitchen(),
            GuestRoom(),
            Study(),
            GuestToilet(),
            Garden(),
            Corridor(),
            EnSuiteToilet(),
            EnSuiteRoom(),
            GroundToilet(),
            MasterRoom(),
            MasterToilet(),
            WholeHome()
            ]         
  
  #for room in render_package_for_rooms:
  #  room.writeConfig()

read_core_entity_entries_json()
check_core_entity_unexpected_entities()

if args.create_system_config:
  read_core_entity_entries_json()
  remove_auto_gen_automation_entities()
  write_core_entity_entries_json()

# Instantiate and render dashboard into yaml
# Default to disable it as the dashboard does not need to be updated
dashboard_type = 'tablet' if args.render_dashboard_tablet is True else \
                 'mobile' if args.render_dashboard_mobile is True else \
                 'default'

dashboard_language = 'Chinese' if args.dashboard_language_chinese is True else \
                     'English' 

if args.render_dashboard_yaml:
  dashboard = Dashboard(format='yaml', dashboard_type=dashboard_type, dashboard_language=dashboard_language)
elif args.render_dashboard_json:
  dashboard = Dashboard(format='json', dashboard_type=dashboard_type, dashboard_language=dashboard_language)


# All Zigbee devices mac-name mapping













#('0x001788010c4c1cc8', 'E27',  'HUE W Z2M 4')
#('0x001788010c45edfc', 'E27',  'HUE W Z2M 3')
#('0x001788010c45f13e', 'E27',  'HUE W Z2M 1')
#('0x001788010c45f2d5', 'E27',  'HUE W Z2M 2')



#
  # vaccum_idle
# elif people_have_cooked_in_kitchen_and_left & vacuum_idle
  # vaccum_start
# elif people_in_the_kitchen & vaccum_start
  # vacuum_paused
# elif people_left_the_kitchen & vacuum_paused
  # vaccum_resume(or start)



print ("Done.")
##translation = translator.translate("This is a pen.")
#print (translation)















