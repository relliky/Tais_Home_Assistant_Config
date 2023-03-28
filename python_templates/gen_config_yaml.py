import re
import yaml
import os
import json
import copy
import argparse

##################################################################
#  Room Yaml Configurations
##################################################################

class RoomBase:
  def __init__ (self):

    # Create Empty JSON Database
    self.reset_json_environment()
    
    # Basic Parameter
    self.get_room_config()
    self.get_room_name_and_property()
    self.get_motion_sensor_entities()
    self.get_remote_entities()
    self.get_wall_switches()
    self.get_light_entities()
    self.get_lighting_control_entities()
    self.get_tv_entities()
    self.get_time_setup()
    self.get_cover_entities()
    self.get_temperature_control_entities()
    self.get_post_room_config()
    

    # Populate entities into database
    self.get_entity_declarations()
    self.get_automation_declarations()
    self.populate_entnties_into_database()
    
    # Remove disabled entities
    self.remove_disabed_entities()
    # Generate user control group including automations and other controls
    self.get_automation_group_declarations()

    # Get dashboard settings
    self.getDashboardSettings()

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
    self.cfg_tv                 = False
    self.cfg_flex_wall_switch   = False

    # Adavanced Enables
    self.cfg_scene_colour_led   = False
    self.cfg_scene_colour_lamp  = False
    self.cfg_custom_scene       = False
    self.cfg_led_only_scene     = False
    self.cfg_motion_bed_led     = False
    self.cfg_auto_curtain_ctl   = False
    
    self.room_entity           = 'uninitialized_room_entity'
    self.room_name             = 'Uninitialized_room_name'    
    self.room_short_name       = 'uninitialized_room_short_name'

  def get_room_name_and_property(self):  
    self.room_entity          = self.getIDFromName(self.room_name)
    self.automation_room_name = self.room_short_name + " " 

    self.room_type =  'bedroom'       if (('_room' in self.room_entity) and ('living_room' != self.room_entity)) else \
                      'toilet'        if '_toilet' in self.room_entity else \
                      'common_area'

    self.west_face_windows = True     if self.room_entity in ['en_suite_room', 'master_room', 'kitchen'] else False
    
  def get_motion_sensor_entities(self):  
    # Motion sensor entities
    self.bed_motion_sensors      =  ["binary_sensor." + self.room_entity + "_bed_motion_sensor_motion"] if self.room_type == 'bedroom' else []
    self.non_bed_motion_sensors  =  []
    self.room_motion_sensor      =   "group."         + self.room_entity + "_motion"
    self.all_motion_sensors      =  ["uninitialized_all_motion_sensors"]
    self.entrance_motion_sensors =  ["binary_sensor." + self.room_entity + "_entrance_motion_sensor_motion"] if self.room_type == 'bedroom' else \
                                    [self.room_motion_sensor]
    self.room_occupancy          = "input_select."  + self.room_entity + "_occupancy"               
    self.occupancy_state_duration= 4 # Minutes
    self.occupancy_on_x_min_ratio_sensor  = "unitialized_ratio_sensor"
    self.occupancy_on_2x_min_ratio_sensor = "unitialized_ratio_sensor"

  def get_remote_entities(self):  
    # Button (sensor) entities
    self.xiaomi_buttons          = []
    for i in range(self.num_of_xiaomi_button):
      self.xiaomi_buttons       += ["sensor." + self.room_entity + "_button"] 
      if self.num_of_xiaomi_button != 1:
        self.xiaomi_buttons[i]  += "_" + str(i+1)
    self.wall_buttons            = ["sensor." + self.room_entity + "_wall_button"]
    self.buttons                 = self.wall_buttons + self.xiaomi_buttons
    
  def get_wall_switches(self):
    self.wall_switches       = []
    self.raw_wall_switches   = []
    self.alias_wall_switches = []

    
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
    self.room_lights_and_tvs =  'group.' + self.room_entity + '_lights_and_tvs'


  def get_lighting_control_entities(self):
    
    self.ceiling_light_control_when = {}
    self.ceiling_light_control_when['Lights on in hot sunshine']     = "input_boolean.ceiling_light_control_" + "in_hot_sunshine_"     + self.room_entity
    self.ceiling_light_control_when['Lights on when bright outdoor'] = "input_boolean.ceiling_light_control_" + "when_bright_outdoor_" + self.room_entity
    self.ceiling_light_control_when['Lights on when dark outdoor']   = "input_boolean.ceiling_light_control_" + "when_dark_outdoor_"   + self.room_entity

    self.lamp_control_when = {}
    self.lamp_control_when['Lights on in hot sunshine']              = "input_boolean.lamp_control_" +          "in_hot_sunshine_"     + self.room_entity
    self.lamp_control_when['Lights on when bright outdoor']          = "input_boolean.lamp_control_" +          "when_bright_outdoor_" + self.room_entity
    self.lamp_control_when['Lights on when dark outdoor']            = "input_boolean.lamp_control_" +          "when_dark_outdoor_"   + self.room_entity
                
    self.led_control_when = {}                
    self.led_control_when['Lights on in hot sunshine']               = "input_boolean.led_control_" +           "in_hot_sunshine_"     + self.room_entity
    self.led_control_when['Lights on when bright outdoor']           = "input_boolean.led_control_" +           "when_bright_outdoor_" + self.room_entity
    self.led_control_when['Lights on when dark outdoor']             = "input_boolean.led_control_" +           "when_dark_outdoor_"   + self.room_entity
      
    self.curtain_control_when = {}      
    self.curtain_control_when['Lights on in hot sunshine']           = "input_boolean.curtain_control_" +       "in_hot_sunshine_"     + self.room_entity
    self.curtain_control_when['Lights on when bright outdoor']       = "input_boolean.curtain_control_" +       "when_bright_outdoor_" + self.room_entity
    self.curtain_control_when['Lights on when dark outdoor']         = "input_boolean.curtain_control_" +       "when_dark_outdoor_"   + self.room_entity


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
    if self.cfg_tv:
      # TV entities
      self.tv_room_entity          = self.room_entity
      self.tvs                     = ["media_player." + self.tv_room_entity + "_tv"]
      self.fire_tvs                = ["media_player." + self.tv_room_entity + "_fire_tv"]
    else:
      self.tv_room_entity          = None
      self.tvs                     = []
      self.fire_tvs                = []
      
  def get_time_setup(self):
    # Time setup
    self.daytime_lights_off_timeout   = "00:15:00"
    self.nighttime_lights_off_timeout = "02:00:00" if self.room_type == "bedroom" else \
                                        self.daytime_lights_off_timeout
    self.daytime_start                = "10:00:00"
    self.afternoon_start              = "13:00:00"
    self.daytime_end                  = "22:00:00"

  def get_cover_entities(self):
    # Cover entities
    self.curtains                      = []
    # Cover extra controls
#    self.light_in_daytime_postfix      = self.room_entity + "_light_in_daytime" 
#    self.light_in_daytime              = "input_boolean." + self.room_entity + "_light_in_daytime" 
#    self.curtain_in_nighttime_postfix = self.room_entity + "_curtain_in_nighttime" 
#    self.curtain_in_nighttime          = "input_boolean." + self.room_entity + "_curtain_in_nighttime" 

  def get_temperature_control_entities(self):
    # Temperature sensor entities
    self.outside_temperature              = "sensor.met_office_cambridge_city_airport_temperature_3_hourly"
    self.room_default_temperature         = "input_number."    + self.room_entity + "_default_temperature" 
    self.thermostat                       = "climate."         + self.room_entity
    self.thermostat_schedule              = "switch.schedule_" + self.room_entity + "_temperature"
    self.temperature_sensor               = "sensor."          + self.room_entity + "_temperature_sensor"
    self.room_heating_override            = "input_boolean."   + self.room_entity + "_heating_override"
    
  def get_post_room_config(self):

    # Scene 
    self.room_scene_ctl          = "input_select." + self.room_entity + "_scene"
    
    # Scene automation internal variable
    self.cur_scene           = 'unintialized_cur_scene'
    
    #self.config = { nameof(self.room_entity              ) : self.room_entity               ,
    #                nameof(self.room_name                     ) : self.room_name                      ,
    #                nameof(self.room_type                ) : self.room_type                 ,
    #                nameof(self.bed_motion_sensors       ) : self.bed_motion_sensors        ,
    #                nameof(self.entrance_motion_sensors  ) : self.entrance_motion_sensors   ,
    #                nameof(self.buttons                  ) : self.buttons                   ,
    #                nameof(self.xiaomi_buttons           ) : self.xiaomi_buttons            ,
    #                nameof(self.bed_leds                 ) : self.bed_leds                  ,
    #                nameof(self.leds                     ) : self.leds                      ,
    #                nameof(self.ceiling_lights           ) : self.ceiling_lights            ,
    #                nameof(self.lamps                    ) : self.lamps                     ,
    #                nameof(self.room_entity              ) : self.room_entity       ,
    #                nameof(self.room_entity              ) : self.room_entity       ,
    #                nameof(self.room_entity              ) : self.room_entity       ,
    #                nameof(self.room_entity              ) : self.room_entity       }

  def reset_json_environment(self):
    self.automations         = []
    self.entity_declarations = {}
    self.input_select_dict   = {}
    self.sensor_list         = []
    self.group_dict          = {}
    self.input_boolean_dict  = {}
    self.script_dict         = {}
    self.switch_list         = []
    self.cover_list          = []
    self.template_list       = []
    self.binary_sensor_list  = []
    self.light_list          = []

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
        "entity_id": self.room_motion_sensor,
        "state": "on",
        "type": "ratio",
        "duration": {
          "minutes": str(x_minutes_total)
        },
        "end": "{{ (now() | as_timestamp) | as_datetime | as_local }}",
        "configured": self.cfg_occupancy
      }
    return ratio_sensor_config


  def add_mac_device(self, mac, name, comment, model, postfix=None, integration='Xiaomi Gateway 3', flex_switch=None):
    
    name_postfix   = ' ' + postfix if postfix != None else ''

    # 0 padding mac address to 64-bit for Zigbee device
    if mac.startswith('0x'):
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
      for i in range(1,key_num+1):
        
        
        if integration == 'Xiaomi Gateway 3':
          # single switch is with different postfix
          i = '' if key_num == 1 else i
          alias_switch_name = name + " Wall Switch " + str(i) + name_postfix
          raw_switch_entity = "switch." + mac + ('_switch' if key_num == 1 else '_channel_' + str(i))
        elif integration == 'Z2M':
          # Hack Z2M renamed devices to standard name
          postfix = ''          if key_num == 1            else \
                    '_left'     if i == 1                  else \
                    '_center'   if i == 2 and key_num == 3 else \
                    '_right'    if i == 3 and key_num == 3 or i == 2 and key_num == 2 else ''
                    
          alias_switch_name = name + " Wall Switch " + str(i) + name_postfix
          raw_switch_entity = "switch." + self.room_entity + '_wall_switch' + postfix
        else:
          raise TypeError( "\n" +\
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
        
        # added wall switches
        self.wall_switches += [raw_switch_entity]
        
        # added Yeelight Flex automation
        if flex_switch != None:
          if flex_switch == True:
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
      

      self.binary_sensor_list += [
        {
          "platform": "group",
          "name": name + " Door" + name_postfix,
          "entities": "binary_sensor." + mac + '_contact',
          "configured": True 
        }        
      ]      
    ###################################################################################################
    # Buttons
    # Aqara Wireless Switch, WXKG11LM  ZigbeeID: ["lumi.sensor_switch.aq2"]
    # MiJia Wireless Switch, WXKG01LM  ZigbeeID: ["lumi.sensor_switch"]
    ###################################################################################################
    elif((model == "Aqara Wireless Switch") or \
         (model == "MiJia Wireless Switch")): 

      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Button" + name_postfix,
              "state": '{{states.sensor["' + mac + '_action"].state}}'
            }
          ],
          "configured": True 
        }        
      ]
    ###################################################################################################
    # Light Sensors
    # Xiaomi Mi Light Detection Sensor GZCGQ01LM ZigbeeID: ["lumi.sen_ill.mgl01"]
    ###################################################################################################


    ###################################################################################################
    # Motion Sensors, Occupancy Sensor
    #
    # Aqara Motion and Illuminance Sensor, RTCGQ11LM ZigbeeID: ["lumi.sensor_motion.aq2"]
    # MiJia Human Body Movement Sensor, RTCGQ01LM
    # Mijia2 Motion Sensor,   RTCGQ02LM
    # Ziqing Occupancy Sensor, Mesh model: "mesh IZQ-24"
    ###################################################################################################
    elif((model == "Aqara Motion and Illuminance Sensor"                                           ) or \
         (model == "MiJia Human Body Movement Sensor"                                              ) or \
         (model == "Mijia2 Motion Sensor"                    and integration == 'Xiaomi Gateway 3')): 
      
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

    elif model == "Ziqing Occupancy Sensor" and integration == 'Xiaomi Gateway 3': 

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
    # Temperature Sensor in Xiaomi Gateway 3
    # Qingping Temperature Sensor, id: "ble LYWSDCGQ/01ZM"
    # Mijia2 Temperature Sensor,   id: "ble LYWSD03MMC"
    #
    # Temperature Sensor in Passive BLE 
    # "Mijia2 Temperature Clock", id:"ble LYWSD02MMC"
    ###################################################################################################
    elif((model == "Qingping Temperature Sensor"  and integration == 'Xiaomi Gateway 3') or \
         (model == "Mijia2 Temperature Sensor"    and integration == 'Xiaomi Gateway 3')): 


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
    elif((model == "Generic Switches"     ) or \
         (model == "Mi Power Plug ZigBee" )): 

      switch_entity_postfix = '_plug' if model == "Mi Power Plug ZigBee" else ''
      
      self.switch_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "switch." + mac + switch_entity_postfix,
          "configured": True 
        }        
      ]   
    ###################################################################################################
    # Generic covers/Generic curtains
    # 
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
        + (["Hue"            ] if self.cfg_scene_colour_led or self.cfg_scene_colour_lamp else [])  
        + (["Night Mode",
            "Dark Night Mode"] if self.cfg_custom_scene else[])
        + (["Lamp LED White" ] if len(self.lamps) > 0 else [])  
        + (["LED White"      ] if len(self.leds)  > 0 else [])  
        #+ (["Ceiling Light White with Curtain Open"] if len(self.curtains)  > 0 else [])  
        + [ "All White",
            "Ceiling Light White",
            "All Off"
          ]
        #+ ["Lights on in hot sunshine",
        #   "Lights on when bright outdoor",
        #   "Lights on when dark outdoor"
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
        self.getPostfix(self.room_heating_override) : {
          "name" :  self.getName(self.room_heating_override),
          "initial": "off",
          "configured": self.cfg_temp_control
        }
      }

      self.input_boolean_dict |= {
        self.getPostfix(self.ceiling_light_control_when['Lights on in hot sunshine']) : {
          "name" :  self.getName(self.ceiling_light_control_when['Lights on in hot sunshine']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.ceiling_lights) == 0 or len(self.curtains) == 0 else {}),
        self.getPostfix(self.lamp_control_when['Lights on in hot sunshine']) : {
          "name" :  self.getName(self.lamp_control_when['Lights on in hot sunshine']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.lamps) == 0 or len(self.curtains) == 0 else {}), 
        self.getPostfix(self.led_control_when['Lights on in hot sunshine']) : {
          "name" :  self.getName(self.led_control_when['Lights on in hot sunshine']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.leds) == 0 or len(self.curtains) == 0 else {}),
        self.getPostfix(self.curtain_control_when['Lights on in hot sunshine']) : {
          "name" :  self.getName(self.curtain_control_when['Lights on in hot sunshine']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.curtains) == 0 else {}),
        self.getPostfix(self.ceiling_light_control_when['Lights on when bright outdoor']) : {
          "name" :  self.getName(self.ceiling_light_control_when['Lights on when bright outdoor']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.ceiling_lights) == 0 else {}),
        self.getPostfix(self.lamp_control_when['Lights on when bright outdoor']) : {
          "name" :  self.getName(self.lamp_control_when['Lights on when bright outdoor']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.lamps) == 0 else {}),
        self.getPostfix(self.led_control_when['Lights on when bright outdoor']) : {
          "name" :  self.getName(self.led_control_when['Lights on when bright outdoor']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.leds) == 0 else {}),
        self.getPostfix(self.curtain_control_when['Lights on when bright outdoor']) : {
          "name" :  self.getName(self.curtain_control_when['Lights on when bright outdoor']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.curtains) == 0 else {}),
        self.getPostfix(self.ceiling_light_control_when['Lights on when dark outdoor']) : {
          "name" :  self.getName(self.ceiling_light_control_when['Lights on when dark outdoor']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.ceiling_lights) == 0 else {}),
        self.getPostfix(self.lamp_control_when['Lights on when dark outdoor']) : {
          "name" :  self.getName(self.lamp_control_when['Lights on when dark outdoor']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.lamps) == 0 else {}),
        self.getPostfix(self.led_control_when['Lights on when dark outdoor']) : {
          "name" :  self.getName(self.led_control_when['Lights on when dark outdoor']),
          #"initial": "on",
          "configured": True
        } | ({"initial": "off"} if len(self.leds) == 0 else {}),
        self.getPostfix(self.curtain_control_when['Lights on when dark outdoor']) : {
          "name" :  self.getName(self.curtain_control_when['Lights on when dark outdoor']),
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
          self.room_entity + "_occupancy_group" : {
            "name": self.room_name + " Occuapancy Group",
            "entities": [self.room_occupancy, self.room_motion_sensor] + self.all_motion_sensors 
          }  
        }
      
      self.group_dict |= {
        self.room_entity + "_motion" : {
          "name": self.room_name + " Motion",
          "entities": self.all_motion_sensors
        }          
      }  

      self.group_dict |= {
        self.getPostfix(self.room_lights_and_tvs): {
          "name" : self.getName(self.room_lights_and_tvs),
          "entities": self.lights + self.tvs
        }          
      }  

  def get_script_dict(self):
    pass

  # Lighting Automations
  def get_automation_declarations(self):
    self.gen_motion_light_automations()
    self.gen_temp_control_automations()
    self.gen_xiaomi_button_automations()
    self.gen_wall_button_single_automations()
    self.gen_wall_button_double_automations()
    self.gen_occupancy_automations()
    
    for self.automation in self.automations:
      self.automation['id'] = self.getIDFromAlias(self.automation['alias'])
  
    self.entity_declarations |= {'automation' : self.automations}

    
  def get_automation_group_declarations(self):    

    self.automation_entity_list = []

    # TODO rename this method because it includes other controls
    # Including auto curtain controls
    self.automation_entity_list = [] + \
      ([self.ceiling_light_control_when['Lights on in hot sunshine']    ] if len(self.ceiling_lights) > 0 and len(self.curtains) > 0 else []) + \
      ([self.lamp_control_when['Lights on in hot sunshine']             ] if len(self.lamps) > 0          and len(self.curtains) > 0 else []) + \
      ([self.led_control_when['Lights on in hot sunshine']              ] if len(self.leds) > 0           and len(self.curtains) > 0 else []) + \
      ([self.curtain_control_when['Lights on in hot sunshine']          ] if len(self.curtains) > 0       and len(self.curtains) > 0 else []) + \
      ([self.ceiling_light_control_when['Lights on when bright outdoor']] if len(self.ceiling_lights) > 0 else [])                            + \
      ([self.lamp_control_when['Lights on when bright outdoor']         ] if len(self.lamps) > 0          else [])                            + \
      ([self.led_control_when['Lights on when bright outdoor']          ] if len(self.leds) > 0           else [])                            + \
      ([self.curtain_control_when['Lights on when bright outdoor']      ] if len(self.curtains) > 0       else [])                            + \
      ([self.ceiling_light_control_when['Lights on when dark outdoor']  ] if len(self.ceiling_lights) > 0 else [])                            + \
      ([self.lamp_control_when['Lights on when dark outdoor']           ] if len(self.lamps) > 0          else [])                            + \
      ([self.led_control_when['Lights on when dark outdoor']            ] if len(self.leds) > 0           else [])                            + \
      ([self.curtain_control_when['Lights on when dark outdoor']        ] if len(self.curtains) > 0       else [])                        

    # Generate automations group 
    for automation in self.entity_declarations['automation']:
      self.automation_entity_list += [automation['id']]
    
    # added wall switch control
    self.automation_entity_list += self.wall_switches

    
    if self.cfg_group_auto:
      self.group_dict |= {
          self.room_entity + "_auto_gen_automations" : {
            "name": self.room_name + " Auto-gen Automations",
            "entities": self.automation_entity_list ,
          } 
      }
      
    self.entity_declarations |= {
      "group":  self.group_dict
    }

  def populate_entnties_into_database(self):
      self.entity_declarations |= {
        "input_select":  self.input_select_dict,
        "sensor":        self.sensor_list,
        "input_boolean": self.input_boolean_dict,
        "switch":        self.switch_list,
        "cover":         self.cover_list,
        "template":      self.template_list,
        "binary_sensor": self.binary_sensor_list,
        "light":         self.light_list
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

          # if hot summer
            # turn on lights and open curtain based on control setting
          # else 
            # if bright (not hot summer)
              # turn on lights and open curtain based on control setting
            # else (if dark)
              # turn on lights and open curtain based on control setting
          self.setNewSceneState("Idle"),    
          {
            "if": self.condition_list_is('Hot sunshine'), "then": self.callSceneService('Lights on in hot sunshine'),
            "else": {
              "if": self.condition_list_is('Outdoor is bright'), "then": self.callSceneService('Lights on when bright outdoor'),
              "else": self.callSceneService('Lights on when dark outdoor')
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
          },
          # Make sure that if room_occupany is forced to Outside because of people override (by button for example)
          # and people are going back to the room, the lights should not be turned off
          { "condition": "state",
            "entity_id": self.room_motion_sensor,
            "state": "off",
            "for": "00:01:00"
          }],
        "action": { 
          'parallel': [
            # Re-enable lights on automation
            {
              "service": "homeassistant.turn_on",
              "entity_id": self.automation_lights_on['id']
            },
            # Turn off lights/curtains/tv
            self.turn(self.curtains, 'off'),
            self.turn(self.tvs, 'off'),
            self.callSceneService("All Off")          
          ]
        }    
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
            "entity_id":self.leds + self.ceiling_lights + self.lamps if self.room_entity != 'guest_room' else \
                        self.leds + self.ceiling_lights,
            "condition": "state",
            "state": "off"
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
            "entity_id": self.ceiling_lights + self.lamps if self.room_entity != 'guest_room' else \
                         self.ceiling_lights,
            "condition": "state",
            "state": "off"
          },
          self.turn(self.leds, 'off') 
        ]
      }
    ]


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
            "to": "Stayed Inside"
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
              #  "entity_id": self.room_motion_sensor,
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
                "state": "on"
              }
            ],
            "then": [
              #{ "service": "automation.turn_off",
              #  "entity_id": [self.automation_heating_on['id'],
              #                self.automation_heating_off['id']]
              #},
              { "service": "automation.trigger",
                "entity_id": [self.automation_heating_on['id']]
              }
            ],
            "else": [
              #{ "service": "automation.turn_on",
              #  "entity_id": [self.automation_heating_on['id'],
              #                self.automation_heating_off['id']]
              #},
              { "service": "automation.trigger",
                "entity_id": [self.automation_heating_off['id']]
              }
            ]
          }
        ]
      }      
    ]

    self.automations += [
      {
        "alias" : "ZH-" + self.automation_room_name + "Heating Manual Override Timeout in Few Hours" + "-" + self.room_name,
        "configured": self.cfg_temp_control,
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.room_heating_override,
            "from": "off",
            "to": "on"
          }
        ],
        "action": [
          {
            "delay": {
              "hours": 2,
              "minutes": 0,
              "seconds": 0,
              "milliseconds": 0
            }
          },
          {
            "service": "homeassistant.turn_off",
            "entity_id": self.room_heating_override
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

    if self.cfg_scene_colour_led or self.cfg_scene_colour_lamp:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Hue")]          
    if self.cfg_led_only_scene:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="LED White")]
    if self.cfg_custom_scene:
      #cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Night Mode")] 
      cond_seq+= [self.setNewSceneFromOldScene(nxt_scene="Dark Night Mode")]
      
    cond_seq += [self.setNewSceneFromOldScene(nxt_scene="All Off")] 
      
    return cond_seq

  
  def gen_xiaomi_button_automations(self):
    self.automations += [{
        "alias" : "ZLB-" + self.automation_room_name + "Remote Button - Single - Applies Different Scenes (State Machine)" + "-" + self.room_name,
        "configured": self.cfg_remote_light and (self.num_of_xiaomi_button > 0),
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.xiaomi_buttons,
            "to": ["single", "1"]
          }
        ],
        "mode":"queued", # this has to be queued to make sure no button press is ignored
        
        # Skip the starting Reset scene as this is used to trigger transition when calling a scene
        #"condition": [
        #  {
        #    "condition": "not",
        #    "conditions": [
        #      {
        #        "condition": "state",
        #        "entity_id": self.room_scene_ctl,
        #        "state": "Reset"
        #      }
        #    ]
        #  }
        #],
        
        "action": [
          {
            "choose": self.get_scene_state_machine(),
            # In the case no condition is matching, turn off everything
            "default": self.setNewSceneState("All White")
          }
        ]
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
              self.callSceneServiceIfSelected("All Off"),
              self.callSceneServiceIfSelected("Lights on in hot sunshine"),
              self.callSceneServiceIfSelected("Lights on when bright outdoor"),
              self.callSceneServiceIfSelected("Lights on when dark outdoor")
            ]
          }
        ]
    }]

    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Remote Button - Double - Toggle Lamps" + "-" + self.room_name,
        "configured": self.cfg_remote_light and (self.num_of_xiaomi_button > 0),
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.xiaomi_buttons,
            "to": ["double", "2"]
          }
        ],
        "action": [
            self.turn(self.lamps, "toggle"),
        ]
      }
    ]

    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Remote Button - Triple - Toggle Ceiling Lights" + "-" + self.room_name,
        "configured": self.cfg_remote_light and (self.num_of_xiaomi_button > 0),
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.xiaomi_buttons,
            "to": ["triple", "3"]
          }
        ],
        "action": [
            self.turn(self.ceiling_lights, "toggle"),
        ]
      }
    ]

    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Remote Button - Long - Toggle LEDs" + "-" + self.room_name,
        "configured": self.cfg_remote_light and (self.num_of_xiaomi_button > 0),
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.xiaomi_buttons,
            "to": "hold"
          }
        ],
        "action": [
            self.turn(self.leds, "toggle") 
        ]
      }
    ]


  # Exceptions that will be written per room - most of them because the wall button have multiple keys and multiple lights
  # [TODO] Ground Corridor - double - turn off everything apart from en-suite room/toilet 
  # [TODO] First Corridor - double - turn off everything apart from en-suite room/toilet 
  # [TODO] Master Room - Left - Ceiling light
  # [TODO] Master Room - Middle - Lamps & LED
  # [TODO] Master Room - Right - Balcony Lights
  # [TODO] Master Room - Single - Scenes 
  # [TODO] Master Toilet Dressing Room 
  def gen_wall_button_single_automations(self):
    self.gen_a_wall_button_toggle_automation( button_state_list=[ "1", "single", "single_left", "single_right", "single_center", 
                                                                  "button_1_single", "button_2_single", "button_3_single"],
                                              button_state_name='Single')

  def gen_a_wall_button_toggle_automation(self,
                                          button_state_list, 
                                          button_state_name, 
                                          switch_list=None, 
                                          light_list=None, 
                                          light_name=None, 
                                          button_list=None):
    if switch_list is None:
      switch_list = self.wall_switches

    if light_list is None:
      light_list = self.ceiling_lights

    if light_name is None:
      light_name = 'Ceiling Light'
      
    if button_list is None:
      button_list = self.wall_buttons
      
      
    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Wall Switch - " + button_state_name + " Press - Toggle " + light_name + "-" + self.room_name,
        "configured": self.cfg_remote_light,
        "trigger": [
          {
            "platform": "state",
            "entity_id": button_list,
            "to": button_state_list
          }
        ],
        "action": [self.turn(light_list, "toggle")]
      }
    ]


  def gen_flex_wall_switch_automations(self, flex_wall_switch_index, flex_wall_switch_entity):
    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Flex Wall Switch On Postion " + str(flex_wall_switch_index)  + "- Automatically Turn on the Wall Switch Back When Turned Off -" + self.room_name,
        "configured": self.cfg_flex_wall_switch,
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

  def gen_occupancy_automations(self):
    
    #print ("[OC] " + self.room_name + " occupancy_on_x_min_ratio_sensor is " + self.occupancy_on_x_min_ratio_sensor)
    
    self.automations += [
      {
        "alias":"ZOc-" + self.automation_room_name + "Occupancy Update" + "-" + self.room_name,
        "configured": self.cfg_occupancy,
        "trigger": [
          {
            "entity_id": self.room_motion_sensor,
            "platform": "state",
            "to": "on"
          },
          {
            "entity_id": self.room_motion_sensor,
            "platform": "state",
            "to": "off",
            "for": "05:00:00"
          },
          {
            "minutes": "/5",
            "platform": "time_pattern"
          }
        ],
        "action": [
          {
            "service" : "pyscript.room_occupancy_state_machine",
            "data":{"occupancy_entity_str":           self.room_occupancy,
                    "motion_str":                     self.room_motion_sensor,                                 
                    "motion_on_ratio_for_x_min_str":  self.occupancy_on_x_min_ratio_sensor,
                    "motion_on_ratio_for_2x_min_str": self.occupancy_on_2x_min_ratio_sensor,
                    "room_type":                      self.room_type 
                    },
          }
        ]
      }
    ]



  # Generate automation ID/entity_name based on alias name
  def getIDFromName (self, name):
    id = name.lower()
    id = re.sub("-", "_", id)
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
  def turn(self, entity_list, state=None, light_brightness=None, tv_brightness=None, inc_unavail=True):
    assert state in ['on', 'off', 'toggle', None], "State has to be one of 'on', 'off', 'toggle', None"

    if light_brightness != None:
      action_service = {"service" : "light.turn_on",
                        "entity_id" : entity_list,
                        "data": {"brightness_pct": light_brightness}}
    elif tv_brightness != None:
      action_service = {"service" : "samsungtv_smart.select_picture_mode",
                        "data": { "entity_id" : entity_list,
                                  "picture_mode": "Movie"    if tv_brightness in [1, '1'] else \
                                                  "Natural"  if tv_brightness in [2, '2'] else \
                                                  "Standard" if tv_brightness in [3, '3'] else \
                                                  "Dynamic"}}
    elif entity_list == self.curtains:
      action_service = {"service":  "cover.open_cover"       if state == 'on'     else \
                                    "cover.close_cover"      if state == 'off'    else \
                                    "cover.toggle"           if state == 'toggle' else None,
                        "entity_id": entity_list}

    # TODO make sure that it only turns a directory or a list.
    # use a different way to handle this case                    
    elif entity_list == self.thermostat:
      hvac_mode = "heat" if state == 'on' else "off"
      
      action_service = { "service": "climate.set_hvac_mode",
                         "data": {"hvac_mode": hvac_mode},
                         "entity_id": self.thermostat
                       }
                       
    # Turn on lamps and also reset to white if set to rgb/hs mode                       
    elif entity_list == self.lamps and state == 'on':
      action_service = self.setLightsToWhite(self.lamps)
    
    elif entity_list == 'heating':
      action_service = self.convertToSingleService(
                       [self.turn(self.thermostat,          state),
                        self.turn(self.thermostat_schedule, state)]  )

    # If ceiling lights are offline, use wall switch for controls instead
    elif entity_list == self.ceiling_lights and inc_unavail == True:
      action_service =  {
                          "if": [
                            {
                              'alias': 'any ceiling lights is unavailable, using wall switches to control instead',
                              "condition": "state",
                              "entity_id": entity_list,
                              "state": "unavailable",
                              "match": 'any'
                            }
                          ],
                          "then": self.turn(self.wall_switches,  state),
                          "else": self.turn(self.ceiling_lights, state, inc_unavail=False)
                        }

    elif entity_list == self.wall_switches and state == 'on':
      action_service = self.convertToSingleService(
                        [{"service":"homeassistant.turn_off", "entity_id": entity_list},
                         {"delay": {"milliseconds": 200}},
                         {"service":"homeassistant.turn_on",  "entity_id": entity_list}],
                        alias='Everytime to turn on a wall switch, make sure to turn off it first to make sure the smart lights will be back on')
                         
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


    if entity_list != None:
      return self.convertToSingleService(action_service, 
                                         alias =  ('Turn'  + \
                                                   (' nothing'        if entity_list==[]              else \
                                                    ' ' + entity_list if isinstance(entity_list, str) else " " + " ".join(entity_list)) + \
                                                   (''                if state==None                  else ' state=' + state) + \
                                                   (''                if light_brightness==None       else ' light_brightness=' + str(light_brightness))))
    else:
      return {"service": "script.do_nothing"}


  def setLightsToWhite(self, entity_list):
    
    alias =   'Turn on lamps first and check if light colour is white. ' + \
              'Reset colour lamps to white and apply adaptive lighting.'

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
          scene_service += [self.turn(self.leds + self.lamps, "off"),
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
                            self.turn(self.leds, "on"),
                            self.turn(self.tvs, tv_brightness=3)]
      elif scene_name == 'LED White':
          scene_service += [self.turn(self.ceiling_lights, "off"),
                            self.turn(self.lamps, "off"),
                            self.turn(self.leds, "on"),
                            self.turn(self.tvs, tv_brightness=2)]
      elif scene_name == 'Hue': 
          parallel_enable = False
          scene_service += [# turn on lights to let adaptive lighting run
                            self.turn(self.lamps + self.leds, "on"),
                            # overwrite adaptive lighting brightiness and set it to max
                            self.turn(self.lamps + self.leds, "on", light_brightness=100),
                            # apply colours
                            { "service" : "pyscript.set_rgb_light_list",
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
      elif scene_name == 'All Off':
          scene_service += [self.turn(self.ceiling_lights, "off"),
                            self.turn(self.lamps, "off"),
                            self.turn(self.leds, "off")]
      elif scene_name in ['Lights on in hot sunshine',
                          'Lights on when bright outdoor',
                          'Lights on when dark outdoor']:
        
        scene_service += [{"parallel":[
          {"if": self.continueIf(self.ceiling_light_control_when[scene_name], "on"), "then": self.turn(self.ceiling_lights, "on")},
          {"if": self.continueIf(self.lamp_control_when[scene_name]         , "on"), "then": self.turn(self.lamps,          "on")},
          {"if": self.continueIf(self.led_control_when[scene_name]          , "on"), "then": self.turn(self.leds,           "on")},
          {"if": self.continueIf(self.curtain_control_when[scene_name]      , "on"), "then": self.turn(self.curtains,       "on")}
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
    #  print ("INFO: This is in " + self.room_name + ". nxt_scene=" + nxt_scene + ", cur_scene=" + str(cur_scene) + ".")
    
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
                "state": state
            }
    cond |= {"attribute": attribute} if attribute  != None else {}
    cond |= {"for":       lastFor}   if lastFor    != None else {}
    return cond


  def condition_list_is(self, condition_name):
    if condition_name == 'Outdoor is bright':
      return [{
                "condition": "state",
                "entity_id": "sun.sun",
                "state": "above_horizon"
              }]
    elif condition_name == 'Room has curtains':
      return [self.alwaysOnIf(len(self.curtains) > 0)]
    elif condition_name == 'Hot sunshine':
      return  [
                # Outdoor temp above certain temperature
                {
                  "condition": "numeric_state",
                  "entity_id": self.outside_temperature,
                  "above": "20"
                },
                # In the morning/afternoon
                {
                  "condition": "time",
                  "after":  self.afternoon_start if self.west_face_windows else self.daytime_start,
                  "before": self.daytime_end     if self.west_face_windows else self.afternoon_start
                },
                # Summer
                {
                  "condition": "template",
                  "value_template": "{{ now().month > 4 and now().month < 9 }}"
                },
                # Room has curtain
                self.alwaysOnIf(len(self.curtains) > 0)
              ]
    elif condition_name == 'Enable ceiling light in the daytime':
      return [{
                "condition": "state",
                "entity_id": self.light_in_daytime,
                "state": "on"
              }]
    elif condition_name == 'Enable curtain open in the nighttime':  
      return [{
                "condition": "state",
                "entity_id": self.curtain_in_nighttime,
                "state": "on"
              }]
    else:
      raise TypeError( "\n" +\
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                       "Condition " + condition_name + "is not supported." + "\n" + \
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
      


  def getDashboardSettings(self):
    self.dashboard_root      = 'Uninitliazed_dashboard_root'
    self.dashboard_view_name = 'Uninitliazed_dashboard_view_name'
    self.room_icon           = 'Uninitliazed_room_icon'

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

  def getTemplateCard(self, icon='mdi:head-alert-outline', icon_color='blue', primary=None, secondary=None):
    
    self.dashboard_view_path = "/" + self.dashboard_root + "/" + self.dashboard_view_name

    return {
      "type": "custom:mushroom-template-card",
      "icon": icon,
      "icon_color": icon_color,
      "layout": "horizontal",
      "entity": "input_boolean.placeholder",
      "fill_container": True,
      "primary": primary,
      "secondary":  secondary,
      "tap_action": {
        "action": "navigate",
        "navigation_path": self.dashboard_view_path
      }      
    }

  def getRoomCard (self):
    type = 'mushroom'

    if type == 'mushroom':
      room_card = {    
        "type": "custom:stack-in-card",
        "mode": "vertical",
        "cards": [
          self.getTemplateCard(
            icon       = self.room_icon,
            icon_color = "blue",
            primary    = self.room_name,
            secondary  = "{% set temperature_sensor = '"+self.temperature_sensor+"' %}\n" + \
                         "{% set motion_postfix     = '"+self.getPostfix(self.room_motion_sensor)+"' %}\n{{ states(temperature_sensor) }}\u00b0C | {{\n (as_timestamp(now()) -\n as_timestamp(states.group[motion_postfix].last_changed)) |\n timestamp_custom(\"%H:%M\", false) }} "
          ),
          {
            "type": "custom:stack-in-card",
            "mode": "horizontal",
            "cards": [
              self.getTemplateCard(
                icon       = "{% set occupancy = '"+self.room_occupancy+"' %} {% if   is_state(occupancy, 'Outside') %}\n  mdi:door-closed\n{% elif is_state(occupancy, 'Just Entered') %}\n  mdi:arrow-right-circle\n{% elif is_state(occupancy, 'In Sleep') %}\n  mdi:sleep\n{% else %}\n  mdi:account-multiple\n{% endif %}",
                icon_color = "{% set occupancy = '"+self.room_occupancy+"' %}         {% if   is_state(occupancy, 'Outside') %} {% elif is_state(occupancy, 'Just Entered')%}\n  green\n{% elif is_state(occupancy, 'In Sleep') %}\n  blue            \n{% else %}\n  purple\n{% endif %}",
              ),
              self.getTemplateCard(
                icon       = "{% set motion = '"+self.room_motion_sensor+"' %}        \n{% if is_state(motion, 'on') %}\n  mdi:run-fast\n{% else %}\n  mdi:shoe-print\n{% endif %}",
                icon_color = "{% set motion = '"+self.room_motion_sensor+"' %}        \n{% if is_state(motion, 'on') %}\n  pink\n{% endif %}",
              ),
              self.getTemplateCard(
                icon       = "{% set thermostat = '"+self.thermostat+"' %}        \n{% if is_state(thermostat, 'heat') %}\n  mdi:heating-coil\n{% else %}\n  mdi:snowflake\n{% endif %}",
                icon_color = "{% set thermostat = '"+self.thermostat+"' %}        \n{% if is_state(thermostat, 'heat') %}\n  red\n{% endif %}",
              ),
              self.getTemplateCard(
                icon       = "{% set light = '"+self.room_lights_and_tvs+"' %}        \n{% if is_state(light, 'on') %}\n  mdi:floor-lamp\n{% else %}\n  mdi:floor-lamp-outline\n{% endif %}",
                icon_color = "{% set light = '"+self.room_lights_and_tvs+"' %}                \n{% if is_state(light, 'on') %}\n  yellow\n{% endif %}",
              )
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
    #return room_card
        
    #print (self.room_card)    
        
  # Create a new yaml and write to it
  def writeYaml (self):
    #if type not in ['package', 'overall_dashboard']:
    #  raise TypeError("Yaml type " + type + " is not supported.")

    #if type == 'package':
      # File Path
      self.script_dir         = os.path.dirname(os.path.realpath(__file__))
      self.auto_gen_dir       = self.script_dir + "/../packages/_auto_generated_packages/"
      self.auto_gen_yaml_path = self.auto_gen_dir + "/auto_gen_" + self.room_entity + ".yaml"

      # Open a new file and write automation
      f = open(self.auto_gen_yaml_path, "w")
      
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
    self.num_of_xiaomi_button  = 2
    self.num_of_lamps          = 2
    # Enables
    self.cfg_scene              = True            
    self.cfg_occupancy          = True        
    self.cfg_group_auto         = True       
    self.cfg_motion_light       = True
    self.cfg_remote_light       = True
    self.cfg_temp_control       = True
    self.cfg_temp_calibration   = True
    self.cfg_scene_colour_led   = True
    self.cfg_scene_colour_lamp  = True
    self.cfg_custom_scene       = True
    self.cfg_motion_bed_led     = True
    self.cfg_auto_curtain_ctl   = True
    self.cfg_tv                 = True
    self.cfg_flex_wall_switch   = True
    
  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("0x04cf8cdf3c7ad638", self.room_name,                      'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Triple Rocker)", flex_switch=[2,3])
    self.add_mac_device("582d343b6a27",       self.room_name,                      'Temperature Sesnor', "Mijia2 Temperature Sensor", postfix='new_1')
    self.add_mac_device("a4c138ecdbba",       self.room_name,                      'Temperature Sesnor', "Mijia2 Temperature Sensor", postfix='new_2')
    self.add_mac_device("dced830908fb",       self.room_name,                      'Motion Sensor',      "Ziqing Occupancy Sensor")
    self.add_mac_device("54ef44e58958",       self.room_name + " Bed",             'Motion Sensor',      "Mijia2 Motion Sensor")
    self.add_mac_device("0x00158d0005228ba8", self.room_name + " TV",              'Motion Sensor',      "Aqara Motion and Illuminance Sensor")
    self.add_mac_device('50ec50df3056',       'Master Room Ceiling Light Bulb 1',  'Light',              'Mijia BLE Lights')


    #self.add_mac_device('50ec50df0a79',       'Master Room Ceiling Light Bulb 2',  'Light',              'Mijia BLE Lights')
    #self.add_mac_device("0x04cf8cdf3c73a19b",       self.room_name,                      'Curtain', "Aqara Curtain B1 ZNCLDJ12LM (lumi.curtain.hagl04)')



    self.add_average_temperature_sensor(sensor_1='sensor.master_room_temperature_sensor_new_1', 
                                        sensor_2='sensor.master_room_temperature_sensor_new_2', 
                                        name='Master Room Temperature Sensor')





#('0x00158d0005228ba8', 'Master Room TV',             'Aqara Motion and Illuminance Sensor')
#('0x00158d00054a6f3a', 'Master Room Drawer',         'Aqara Motion and Illuminance Sensor')
#('0x00158d00054deda4', 'Master Room Stair',          'Aqara Motion and Illuminance Sensor')
#('0x00158d000122393b', 'Master Room Entrance',       'Motion Sensor')
#('0x00158d000171bd29', 'Master Room Dressing Table', 'Motion Sensor')
#('0x04cf8cdf3c7ad638', 'Master Room',                'Aqara D1 Wall Switch (With Neutral, Triple Rocker)')
#('0x00158d00052e2124', 'Master Room Entrance',       'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
#('0x04cf8cdf3c7b36b1', 'Master Room',                'Light Meter')
#('0x04cf8cdf3c73a19b', 'Master Room',                'Curtain')
#('0x00158d00053e95f6', 'Master Room Balcony',        'Aqara Door & Window Sensor')
#('0x00158d00012262a5', 'Master Room 1'               'MiJia Wireless Switch')
#('0x00158d000424f98c', 'Master Room 2'               'MiJia Wireless Switch')


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
      "binary_sensor.master_room_occupancy_sensor_occupancy"
    ]
    
    self.all_motion_sensors = self.non_bed_motion_sensors + self.bed_motion_sensors
    
  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.leds                    = ["light.master_room_drawer_led",
                                    "light.master_room_tv_led",
                                    "light.master_room_bed_led"] 
    self.lights                  = self.leds + self.lamps + self.ceiling_lights
    
  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains               = [ "cover.master_room_blind",
                                    "cover.master_room_curtain"] 

  def get_remote_entities(self):  
    super().get_remote_entities()
    self.wall_buttons            = ["sensor." + self.room_entity + "_entrance_wall_button"]
    self.buttons                 = self.wall_buttons + self.xiaomi_buttons

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'master-room'
    self.dashboard_view_name = 'master-room'
    self.room_icon           = 'mdi:bed-king-outline'


class MasterToilet(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Master Toilet'    
    self.room_short_name       = 'MT'
    self.cfg_occupancy          = True       
    self.cfg_group_auto         = True
    self.cfg_temp_control       = True
    self.cfg_temp_calibration   = True
    self.cfg_scene              = True            
    self.cfg_motion_light       = True
    self.cfg_remote_light       = True
    self.cfg_flex_wall_switch   = True

  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device('0x00158d00047d69be',      self.room_name,                            'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
    self.add_mac_device("a4c1381d6ddb",            self.room_name,                            'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device('0x00158d00053fdaa8',      self.room_name,                            'Door Sensor',        'Aqara Door & Window Sensor')
    self.add_mac_device('0x00158d00057b2b4c',      self.room_name + ' Basin',                 'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('0x00158d000460247b',      self.room_name + ' Dressing Room',         'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('0x00158d00054750ca',      self.room_name + ' Shower',                'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('0x00158d000171756e',      self.room_name + ' Floor LED',             'Switch',             'Mi Power Plug ZigBee')
    # Dressing Room
    self.add_mac_device("0x00158d00042d4092",      self.room_name + " Dressing Room",         'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Single Rocker)", flex_switch=True)
    self.add_mac_device("28d1272057d5",            self.room_name + " Dressing Room Light",   'Light',              "Mijia BLE Lights")

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

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'master-room'
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
    self.cfg_tv                 = True
    self.cfg_flex_wall_switch   = True
    
  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [

     #"binary_sensor.kitchen_occupancy_sensor_occupancy",

      "binary_sensor.kitchen_worktop_motion_sensor_motion",
      "binary_sensor.kitchen_dining_motion_sensor_motion"
    ]


  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("a4c1380e91a7",           self.room_name,               'Temperature Sensor', "Mijia2 Temperature Sensor")     
    self.add_mac_device("curtain_1e9e",           self.room_name + " Curtain",  'Curtain',            "Generic Curtains")     
    self.add_mac_device('0x04cf8cdf3c7ad647',     self.room_name,               'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Triple Rocker)', integration='Z2M', flex_switch=[2])
    self.add_mac_device("dced8308f596",           self.room_name,               'Motion Sensor',      "Ziqing Occupancy Sensor")


    
    #self.add_mac_device("e4aaec4500e4",           self.room_name + " Window",              "Mijia2 Contact")     
    #self.add_mac_device("0x158d00023e6015",       self.room_name + " Worktop",             "Aqara Wireless Switch")     

   # Still in MQTT

#('0x00158d00057acaac', 'Kitchen Dining',             'Aqara Motion and Illuminance Sensor')
#('0x00158d0004660308', 'Kitchen Worktop',            'Aqara Motion and Illuminance Sensor')
#('0x00158d0005210fa9', 'Kitchen Extractor',          'Aqara D1 Wall Switch (With Neutral, Double Rocker)')


  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.ceiling_lights          = ["light.kitchen_ceiling_light",
                                    "light.kitchen_dining_light"]
    self.leds                    = ["switch.kitchen_floor_led"]
    self.lights                  = self.leds + self.lamps + self.ceiling_lights

  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains               = ["cover.kitchen_curtain"] 

  def gen_wall_button_single_automations(self):
    self.gen_a_wall_button_toggle_automation( button_state_list=["single_left", "button_1_single"],
                                              button_state_name='Single Left',
                                              light_list='light.kitchen_ceiling_light',
                                              light_name='Ceiling Light')

    self.gen_a_wall_button_toggle_automation( button_state_list=["single_center", "button_2_single"],
                                              button_state_name='Single Center',
                                              light_list='light.kitchen_dining_light',
                                              light_name='Dining Light')

    self.gen_a_wall_button_toggle_automation( button_state_list=["single_right", "button_3_single"],
                                              button_state_name='Single Right',
                                              light_list=self.leds,
                                              light_name='Floor LED')

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'lovelace-kitchen'
    self.dashboard_view_name = 'kitchen'
    self.room_icon           = 'mdi:silverware-clean'

  # Customize system card information
  def getRoomCard (self):
    room_card = super().getRoomCard()
    # Adding vaccum info
    room_card['card']['cards'][0]['secondary'] += " | {{states('vacuum.x1')}}"
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
    self.cfg_scene_colour_lamp  = True
    self.cfg_temp_control       = True
    self.cfg_temp_calibration   = True
    self.cfg_tv                 = True
    self.cfg_flex_wall_switch   = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.living_room_sofa_motion_sensor_motion",
      "binary_sensor.living_room_entrance_motion_sensor_motion",
      "binary_sensor.tais_desk_motion_sensor_motion"
    ]

  def get_room_name_and_property(self):  
    super().get_room_name_and_property()
    self.room_type              = 'bedroom' # as we often fall into sleep in living room

  def get_entity_declarations(self):
    super().get_entity_declarations()

    self.add_average_temperature_sensor(sensor_1='sensor.living_room_temperature_sensor_1', 
                                        sensor_2='sensor.living_room_temperature_sensor_2', 
                                        name='Living Room Temperature Sensor')

    self.add_mac_device("2ab7",               self.room_name,              'Temperature Sensor', "Mijia2 Temperature Clock",  postfix='1', integration='Passive BLE Monitor')
    self.add_mac_device("a4c13864aca3",       self.room_name,              'Temperature Sensor', "Mijia2 Temperature Sensor", postfix='2')
    self.add_mac_device('0x00158d00045e2300', 'Living Room',               'Wall Switch',        'Aqara Single Key Wired Wall Switch Without Neutral Wire', flex_switch=True)
    self.add_mac_device('54ef44e31acd',       'Tais Desk',                 'Motion Sensor',      'Mijia2 Motion Sensor')

    
#('0x00158d0003140ea8', 'Living Room TV',             'Aqara Motion and Illuminance Sensor')
#('0x00158d0004501b0a', 'Living Room Sofa',           'Aqara Motion and Illuminance Sensor')
#('0x00158d0001212747', 'Boiler Room',                'Aqara Door & Window Sensor')
#('0x00158d000424f995', 'Living Room',                'MiJia Wireless Switch')

#('0x00158d000522e00e', 'Garden',                     'Aqara D1 Wall Switch (With Neutral, Double Rocker)')
#('0x00158d000548b8a5', 'Living Room Sliding Door',   'Aqara Motion and Illuminance Sensor')


  def get_light_entities(self):
    super().get_light_entities()
    self.leds                    = ["light.living_room_tv_led", 
                                    "light.living_room_sofa_led"] 
    self.lamps                   = ["light.living_room_floor_light_1", 
                                    "light.living_room_3_head_lamp_1",
                                    "light.living_room_3_head_lamp_2",
                                    "light.living_room_3_head_lamp_3",
                                    "switch.living_room_floor_light_3"] 
    self.lights                  = self.leds + self.lamps + self.ceiling_lights

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'living-room'
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
    self.add_mac_device('54ef44e34c16',       'Garden Bike Shed',      'Motion Sensor', 'Mijia2 Motion Sensor')

#self.add_mac_device('0x00158d000522e00e', 'Garden',                'Wall Switch',   Aqara D1 Wall Switch (With Neutral, Double Rocker)')
#self.add_mac_device('0x00158d000548b8a5', 'Garden Sliding Door',   'Motion Sensor', Aqara Motion and Illuminance Sensor')


  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'lovelace-garden'
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
    self.cfg_tv                 = True

  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device('0x00158d000403d6c0', self.room_name,               'Button',             'MiJia Wireless Switch')
    self.add_mac_device('0x00158d00047d69e6', self.room_name,               'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
    self.add_mac_device("dced8308f496",       self.room_name,               'Motion Sensor',      "Ziqing Occupancy Sensor")
    self.add_mac_device('0x00158d00057b37be', self.room_name + ' Entrance', 'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x00158d000423319f', self.room_name + ' Floor',    'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('54ef44e559c6',       self.room_name + ' Bed',      'Motion Sensor',      'Mijia2 Motion Sensor')
    self.add_mac_device("a4c138b0eb53",       self.room_name,               'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device("curtain_d29a",       self.room_name + " Curtain",  'Curtain',            "Generic Curtains")     

  def get_tv_entities(self):
    super().get_tv_entities()
    self.tv_room_entity          = 'portable'
    self.tvs                     = ["media_player." + self.tv_room_entity + "_tv"]
    self.fire_tvs                = ["media_player." + self.tv_room_entity + "_fire_tv"]      

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.en_suite_room_bed_motion_sensor_motion",
      "binary_sensor.en_suite_room_entrance_motion_sensor_motion",
      "binary_sensor.en_suite_room_floor_motion_sensor_motion",
      "binary_sensor.en_suite_room_occupancy_sensor_occupancy"
    ]
    
    self.non_bed_motion_sensors = 'binary_sensor.en_suite_room_floor_motion_sensor_motion'

  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.leds                    = ["light.en_suite_room_bed_led"] 
    self.lights                  = self.leds + self.lamps + self.ceiling_lights

  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains               = [ "cover.en_suite_room_curtain"] 

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'en-suite-room'
    self.dashboard_view_name = 'en-suite-room'
    self.room_icon           = 'mdi:bed-queen'


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

  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("0x158d00053fdaba",   self.room_name,  'Door',          "Aqara Door & Window Sensor")
    self.add_mac_device('0x158d000572839f',   self.room_name,  'Motion Sensor', 'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x158d000522d90c',   self.room_name,  'Wall Switch',   'Aqara D1 Wall Switch (With Neutral, Single Rocker)')

    
  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.en_suite_toilet_motion_sensor_motion"
    ]


  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'en-suite-room'
    self.dashboard_view_name = 'en-suite-toilet'
    self.room_icon           = 'mdi:shower-head'

class GuestRoom(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name              = 'Guest Room'    
    self.room_short_name        = 'GR'
    self.num_of_xiaomi_button   = 0
    self.num_of_lamps           = 1
    self.cfg_occupancy          = True       
    self.cfg_group_auto         = True
    self.cfg_temp_control       = True
    self.cfg_temp_calibration   = True
    self.cfg_scene              = True            
    self.cfg_motion_light       = True
    self.cfg_remote_light       = True
    self.cfg_flex_wall_switch   = True
    
  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("582d343483e9",       self.room_name,                    'Temperature Sensor', "Qingping Temperature Sensor")
    self.add_mac_device("50ec50dd67be",       self.room_name + " Lamp",          'Light',              "Generic Lights")
    self.add_mac_device("28d12735ea1e",       self.room_name + " Ceiling Light", 'Light',              "Generic Lights")
    self.add_mac_device('0x00158d00047b69d2', self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', flex_switch=True)


  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.guest_room_door_motion_sensor_motion",
      "binary_sensor.guest_room_bed_motion_sensor_motion"
    ]

  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    #self.leds                    = ["light.guest_room_bed_led"]
    
    self.lights                  = self.leds + self.lamps + self.ceiling_lights


  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'guest-room'
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

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.guest_toilet_motion_sensor_motion"
    ]

  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.leds                    = ["switch.guest_toilet_floor_led"]
    self.lights                  = self.leds + self.lamps + self.ceiling_lights


  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("a4c1387a7b78",       self.room_name,     'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device('0x00158d000487851a', self.room_name,     'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)', integration='Z2M')


#('0x00158d00052b35f7', 'Guest Toilet',               'Aqara Motion and Illuminance Sensor')
#('0x00158d00053e96ae', 'Guest Toilet',               'Aqara Door & Window Sensor')


  # Guest Toilet - Left key - Ceiling light
  # Guest Toilet - Right key - Floor LED
  def gen_wall_button_single_automations(self):
    self.gen_a_wall_button_toggle_automation( button_state_list=["single_left"],
                                              button_state_name='Single Left',
                                              light_list=self.ceiling_lights,
                                              light_name='Ceiling Light')

    #self.gen_a_wall_button_toggle_automation( button_state_list=["single_right"],
    #                                          button_state_name='Single Right',
    #                                          light_list=self.leds,
    #                                          light_name='Floor LEDs')


  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'guest-room'
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

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.study_motion_sensor_motion",
      "binary_sensor.kes_desk_motion_sensor_motion"
    ]

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'lovelace-misc'
    self.dashboard_view_name = 'study'
    self.room_icon           = 'mdi:desk'


  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device('0x00158d00045245be', self.room_name, 'Wall Switch', 'Aqara D1 Wall Switch (With Neutral, Single Rocker)', integration='Z2M')
    

    #self.add_mac_device("xxxxxxxxxxxx",       self.room_name,     'Temperature Sensor', "Mijia2 Temperature Sensor")

#('0x00158d00054a6eb9', 'Study',                      'Aqara Motion and Illuminance Sensor')

#0x00158d000403d6c0

class Corridor(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name              = 'Corridor'    
    self.room_short_name        = 'CR'
    self.cfg_occupancy          = True       
    self.cfg_group_auto         = True
    self.cfg_temp_control       = True
    self.cfg_remote_light       = True
    self.cfg_flex_wall_switch   = True
    
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
    self.add_mac_device('0x00158d00045019fd', 'Ground Corridor',             'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('0x00158d00048783e5', 'Ground Corridor',             'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)', integration='Z2M', flex_switch=[1])
    self.add_mac_device('0x00158d0005210fcf', 'First Corridor',              'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)', integration='Z2M', flex_switch=[2])
    
#('0x00158d0004525183', 'First Corridor',             'Aqara Motion and Illuminance Sensor')
#('0x00158d00045f640a', 'Upstairs Heating',           'Aqara Single Key Wired Wall Switch Without Neutral Wire')
#('0x00158d0005227632', 'Downstairs Heating',         'Aqara D1 Wall Switch (With Neutral, Double Rocker)')


  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'lovelace-misc'
    self.dashboard_view_name = 'corridors'
    self.room_icon           = 'mdi:toilet'

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

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.ground_toilet_motion_sensor_motion"
    ]

  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("a4c1387c09bd",        self.room_name,                                  'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device('0x00158d0004667569',  self.room_name,                                  'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device("0x00158d0005435643",  self.room_name,                                  'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Double Rocker)")
    self.add_mac_device("0x90fd9ffffe8e24b6",  self.room_name + " Ceiling Light Spotlight 1",   'Light',              "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum", integration='Z2M')
    self.add_mac_device("0x000b57fffee8e6b4",  self.room_name + " Ceiling Light Spotlight 2",   'Light',              "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum", integration='Z2M')

    #('0x00158d0004667569', 'Ground Toilet',              'Aqara Motion and Illuminance Sensor')
    #('0x00158d00052d5691', 'Ground Toilet',              'Aqara Door & Window Sensor')




  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'lovelace-misc'
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
      "group.living_room_motion",
      #"group.garden_motion",
      "group.kitchen_motion",
      "group.corridor_motion",
      "group.study_motion",
      "group.ground_toilet_motion",
      "group.master_room_motion",
      "group.master_toilet_motion",
      "group.en_suite_room_motion",
      "group.en_suite_toilet_motion",
      "group.guest_room_motion",
      "group.guest_toilet_motion"
    ]

class System(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'System'

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_root      = 'lovelace-system'
    self.dashboard_view_name = 'system'
    self.room_icon           = 'mdi:server'

  # Customize system card information
  def getRoomCard (self):
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
              "navigation_path": "/lovelace-system/system\\"
            }
          },
          {
            "type": "custom:stack-in-card",
            "mode": "horizontal",
            "cards": [
              {
                "type": "custom:mushroom-entity-card",
                "entity": "switch.gaming_pc",
                "icon": "mdi:desktop-classic",
                "icon_color": "amber",
                "primary_info": "state",
                "secondary_info": "none",
                "tap_action": {
                  "action": "more-info"
                }
              },
              {
                "type": "custom:mushroom-entity-card",
                "entity": "binary_sensor.fire_tv_streaming_pc_contents",
                "icon": "mdi:television-box",
                "icon_color": "deep-orange",
                "primary_info": "state",
                "secondary_info": "none",
                "tap_action": {
                  "action": "more-info"
                }
              }
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


class OverallDashboard(RoomBase):
  def __init__ (self):
    super().__init__()
    self.getRooms()
    self.getOverallDashboard()
    self.writeYaml()
    
  def getOverallDashboard(self):
    self.room_cards = []

    for room in self.rooms:
      self.room_cards += [room.getRoomCard()]
      #print (self.room_card)

    #print (self.room_cards)

    self.overall_dashboard = {
        "square": False,
        "columns": 2,
        "type": "grid",
        "cards": self.room_cards}   

  def getRooms(self):
    self.rooms = [ 
              LivingRoom(),
              Kitchen(),
              MasterRoom(),
              MasterToilet(),
              Study(),
              System(),
              GroundToilet(),
              Corridor(),
              Garden(),
              EnSuiteRoom(),
              EnSuiteToilet(),
              GuestRoom(),
              GuestToilet()]

  def writeYaml(self):
    
    # File Path
    self.script_dir         = os.path.dirname(os.path.realpath(__file__))
    self.auto_gen_dir       = self.script_dir + "/../lovelace/"
    self.auto_gen_yaml_path = self.auto_gen_dir + "/auto_gen_overall_dashboard.yaml"

    # Open a new file and write automation
    f = open(self.auto_gen_yaml_path, "w")
    
    f.write(yaml.dump(self.overall_dashboard, sort_keys=False, width=float("inf")))
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
args = parser.parse_args()

if args.render_auto_config :
  render_package_for_rooms = [ 
            LivingRoom(),
            Kitchen(),
            #EnSuiteToilet(),
            GuestRoom(),
            Study(),
            GuestToilet(),
            Garden(),
            Corridor(),
            #EnSuiteRoom(),
            GroundToilet(),
            MasterRoom(),
            MasterToilet(),
            WholeHome()
            ]         
  yaml.Dumper.ignore_aliases = lambda *args : True
  
  for room in render_package_for_rooms:
    room.writeYaml()

read_core_entity_entries_json()
check_core_entity_unexpected_entities()

if args.create_system_config:
  read_core_entity_entries_json()
  remove_auto_gen_automation_entities()
  write_core_entity_entries_json()

# Instantiate and render dashboard into yaml
# Disable it as we dashboard does not need to be updated
#dashboard = OverallDashboard()


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




















