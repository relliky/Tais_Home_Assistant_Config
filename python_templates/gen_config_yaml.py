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
    # Basic Parameter
    self.get_room_config()
    self.get_room_name_and_property()
    self.get_motion_sensor_entities()
    self.get_remote_entities()
    self.get_light_entities()
    self.get_tv_entities()
    self.get_time_setup()
    self.get_cover_entities()
    self.get_temperature_control_entities()
    self.get_post_room_config()
    
    # Render json database
    self.reset_json_environment()
    # Populate entities into database
    self.get_entity_declarations()
    self.get_automation_declarations()
    self.populate_entnties_into_database()
    
    # Remove disabled entities
    self.remove_disabed_entities()
    # Generate automation group
    self.get_automation_group_declarations()

    
  def get_room_config(self):  
    # Room configuration                    
    self.room_entity           = False
    self.num_of_xiaomi_button  = 0
    self.num_of_lamps          = 0
    # Enables
    self.en_scene              = False            
    self.en_occupancy          = False        
    self.en_group_auto         = False       
    self.en_motion_light       = False
    self.en_remote_light       = False
    self.en_temp_control       = False
    self.en_temp_calibration   = False
    # Optional Enables
    self.en_scene_colour_led   = False
    self.en_scene_colour_lamp  = False
    self.en_cst_scene          = False
    self.en_led_only_scene     = False
    self.en_motion_bed_led     = False
    
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
    self.bed_motion_sensors      = ["binary_sensor." + self.room_entity + "_bed_motion_sensor_motion"] if self.room_type == 'bedroom' else []
    self.non_bed_motion_sensors  = []
    self.room_motion_sensor      =  "group."         + self.room_entity + "_motion"
    self.all_motion_sensors      = ["uninitialized_all_motion_sensors"]
    self.entrance_motion_sensors = ["binary_sensor." + self.room_entity + "_entrance_motion_sensor_motion"] if self.room_type == 'bedroom' else \
                                   [self.room_motion_sensor]
    self.room_occupancy_postfix = self.room_entity + "_occupancy"       
    self.room_occupancy         = "input_select."  + self.room_occupancy_postfix                    
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

  def get_tv_entities(self):
    # TV entities
    self.tv_room_entity          = 'portable' if self.room_entity == 'en_suite_room' else self.room_entity
    self.tvs                     = ["media_player." + self.tv_room_entity + "_tv"]
    self.fire_tvs                = ["media_player." + self.tv_room_entity + "_fire_tv"]

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
    self.curtains               = []

  def get_temperature_control_entities(self):
    # Temperature sensor entities
    self.outside_temperature              = "sensor.cambridge_city_airport_temperature"
    self.room_default_temperature_postfix = self.room_entity + "_default_temperature" 
    self.room_default_temperature         = "input_number." + self.room_default_temperature_postfix
    self.thermostat                       = "climate." + self.room_entity
    self.thermostat_schedule              = "switch.schedule_" + self.room_entity + "_temperature"
    self.temperature_sensor               = "sensor." + self.room_entity + "_temperature_sensor"
    
  def get_post_room_config(self):

    # Scene 
    self.room_scene_postfix  = self.room_entity + "_scene"
    self.room_scene          = "input_select." + self.room_scene_postfix
    
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
    
    
  def get_occupancy_ratio_sensor_config(self, x_minutes_multiple_str):
    x_minutes_multiple = 1 if x_minutes_multiple_str == '1x' else \
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
        "enabled": self.en_occupancy
      }
    return ratio_sensor_config
    
    

  def get_entity_declarations(self):

      self.input_select_dict |= {
        self.room_scene_postfix : {
          "name" : self.room_name + " Scene",
          "options": \
          (["Hue"            ] if self.en_scene_colour_lamp else [])  
        + (["Night Mode",
            "Dark Night Mode"] if self.en_cst_scene else[])
        + (["Lamp LED White" ] if len(self.lamps) > 0 else [])  
        + (["LED White"      ] if len(self.leds)  > 0 else [])  
        +  [ "All White",
             "Ceiling Light White",
             "All Off"
           ],
          "enabled": self.en_scene 
        }
      }
      
      self.input_select_dict |= {
        self.room_occupancy_postfix : {
          "name" : self.room_name + " Occupancy",
          "options":[
            "Outside",
            "Just Entered",
            "Stayed Inside",
            "In Sleep"
          ],
          "enabled": self.en_occupancy
        }
      }
    
      self.sensor_list += [
        self.get_occupancy_ratio_sensor_config('1x'),
        self.get_occupancy_ratio_sensor_config('2x')
      ]

      # Group is special for "enabled" as we need to remove disabled 
      # automations for generating groups
      if self.en_occupancy:
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
    # Generate automations group 
    self.automation_entity_list = []
    for automation in self.entity_declarations['automation']:
      self.automation_entity_list += [automation['id']]

    if self.en_group_auto:
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
        "sensor":        self.sensor_list
      }


  def gen_motion_light_automations(self):
    self.automation_lights_on = {"alias":"ZL-" + self.automation_room_name + "Ceiling Lights On Or Open Curtains If Entering to Room" + "-" + self.room_name }
    self.automation_lights_on['id'] = self.getIDFromAlias(self.automation_lights_on['alias'])
    self.automations += [self.automation_lights_on | {
        # Lights on automation are initially off until it is automatically turned on when no present detected
        "enabled" : self.en_motion_light,
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
            "data": {
              "stop_actions": False
            }
          },
          {
            "choose": [
              #  IF the room is a common_room/toilet     
              #  Turn on all ceiling light and LED after sunset 
              #  but only turn on ceiling light during daytime       
              {
                "conditions": self.alwaysOnIf(self.room_type != 'bedroom'),
                "sequence": [
                  self.setNewScene("Ceiling Light White"),
                  {
                    "condition": "state",
                    "entity_id": "sun.sun",
                    "state": "below_horizon"
                  },
                  self.setNewScene("All White")              
                ]
              },
              # ELSE - in bedrooms            
              # IF - the room have a curtain and now is in the daytime
              #    - and not the hot afternoons in summer
              #    not (i.e. outdoor temperature above 15 & in the afternoon & in the summer)
              #.   then open curtain
              {
                "conditions": [
                  # Room has curtains
                  self.alwaysOnIf(len(self.curtains) > 0),
                  # in daytime
                  {
                    "condition": "state",
                    "entity_id": "input_select.indoor_brightness",
                    "state": "bright"
                  },
                  # not the hot afternoons in summer
                  {
                    "condition": "not",
                    "conditions": [
                      {
                        "condition": "and",
                        "conditions": [
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
                          }
                        ]
                      }
                    ]
                  }
                ],
                "sequence": self.turn(self.curtains, 'on')
              },
            # ELSE - in nighttime/hot days in summer afternoon
            #.       turn on master room ceiling/bed lights
            
            # only turn on bright lights on non-sleeping times
            # IF daytime, turn on bright lights
              {
                "conditions": [
                  {
                    "condition": "time",
                    "after":  self.daytime_start,
                    "before": self.daytime_end
                  }
                ],
                "sequence": self.setNewScene("All White")
              }
            ],

            # ELSE nighttime, turn on lamps and led only if the room have lamps
            #                 otherwise, turn on ceiling lights and leds 
            "default": self.setNewScene("Lamp LED White") if len(self.lamps) > 0 else \
                       self.setNewScene("All White")
          }
        ]
    }]
    

    self.automation_lights_off = {"alias":"ZL-" + self.automation_room_name + "Lights Off If No Person" + "-" + self.room_name}
    self.automation_lights_off['id'] = self.getIDFromAlias(self.automation_lights_off['alias'])
    self.automations += [self.automation_lights_off | {
        "enabled": self.en_motion_light,
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
        "action": [
          # Re-enable lights on automation
          {
            "service": "homeassistant.turn_on",
            "entity_id": self.automation_lights_on['id']
          },
          # Turn off lights/curtains/tv
          self.setNewScene("All Off"),
          self.turn(self.leds + self.ceiling_lights + self.lamps, 'off'),
          self.turn(self.tvs, 'off'),
          self.turn(self.curtains, 'off')
        ]
      }
    ]

    self.automations += [
      {
        "alias" : "ZL-" + self.automation_room_name + "LED On for 3 Min if Walking In the Dark" + "-" + self.room_name,
        "enabled": self.en_motion_light and self.en_motion_bed_led,
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
            "entity_id": self.leds + self.ceiling_lights + self.lamps if self.room_entity == 'en_suite_room' else \
                         self.leds + self.ceiling_lights,
            "condition": "state",
            "state": "off"
          }
        ],
        "action": [
          self.turn(self.leds, 'on', light_brightness=40),
          {"delay": "00:03:00"},
          self.turn(self.leds, 'off')
        ]
      }
    ]


  def gen_temp_control_automations(self):
    self.automations += [
      {
        "alias" : "ZH-" + self.automation_room_name + "Heating Schedule On If Staying In the Room" + "-" + self.room_name,
        "enabled": self.en_temp_control and self.en_occupancy,
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
            "then": [
              { "service": "climate.set_hvac_mode",
                "data":   {"hvac_mode": "heat"},
                "target": {"entity_id": self.thermostat}
              },
              { "service": "switch.turn_on",
                "target": {"entity_id": self.thermostat_schedule}
              }
            ]
          }
        ]
      }      
    ]

    self.automation_heating_off = {"alias":"ZH-"+self.automation_room_name+"Heating Schedule Off If People Left the Room"+"-"+self.room_name}
    self.automation_heating_off['id'] = self.getIDFromAlias(self.automation_heating_off['alias'])
    self.automations += [self.automation_heating_off | {      
        "enabled": self.en_temp_control and self.en_occupancy,
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
        "action": [
            { "service": "climate.set_hvac_mode",
              "data":   {"hvac_mode": "off"},
              "target": {"entity_id": self.thermostat}
            },
            { "service": "switch.turn_off",
              "target": {"entity_id": self.thermostat_schedule}
            },
            # If it is not triggered by Outside condition (e.g. manual override by double click button)
            # set occupancy to Outside
            {"service": "input_select.select_option",
             "target":  {"entity_id": self.room_occupancy},
             "data":    {"option": "Outside"}
            }]
      }      
    ]

    self.automations += [
      {
        "alias" : "ZH-" + self.automation_room_name + "Valve Calibrate Temperature Using External Sensor" + "-" + self.room_name,
        "enabled": self.en_temp_control and self.en_temp_calibration,
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
  # + ([self.setNewSceneFromOldScene(nxt_scene="Night Mode")]    if self.en_cst_scene else []) 
  # + ([self.setNewSceneFromOldScene(nxt_scene="LED White")])    if self.en_led_only_scene else [] 
  # + ([self.setNewSceneFromOldScene(nxt_scene="All Off")])
  #
  def get_scene_state_machine(self):
    cond_seq = []
    
    cond_seq += [self.setNewSceneFromOldScene(cur_scene="All Off", nxt_scene="All White"),
                 self.setNewSceneFromOldScene(nxt_scene="Lamp LED White")] 

    if self.en_scene_colour_led or self.en_scene_colour_lamp:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Hue")]          
    if self.en_led_only_scene:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="LED White")]
    if self.en_cst_scene:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Night Mode")] 
      #cond_seq+= [self.setNewSceneFromOldScene(nxt_scene="Dark Night Mode")]
      
    cond_seq += [self.setNewSceneFromOldScene(nxt_scene="All Off")] 
      
    return cond_seq

  
  def gen_xiaomi_button_automations(self):
    self.automations += [{
        "alias" : "ZLB-" + self.automation_room_name + "Remote Button - Single - Applies Different Scenes (State Machine)" + "-" + self.room_name,
        "enabled": self.en_remote_light and (self.num_of_xiaomi_button > 0),
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.xiaomi_buttons,
            "to": ["single", "1"]
          }
        ],
        "mode":"queued",
        "action": [
          {
            "choose": self.get_scene_state_machine(),
            # In the case no condition is matching, turn off everything
            "default": self.setNewScene("All Off")
          }
        ]
    }]

    self.automations += [{
        "alias" : "ZLB-" + self.automation_room_name + "Applies Different Scenes Based on Scene Selections (State Execution)" + "-" + self.room_name,
        "enabled": self.en_scene,
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.room_scene,
          }
        ],
        "mode":"queued",
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
              self.callSceneServiceIfSelected("All Off")
            ]
          }
        ]
    }]

    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Remote Button - Double - Toggle Lamps" + "-" + self.room_name,
        "enabled": self.en_remote_light and (self.num_of_xiaomi_button > 0),
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
        "enabled": self.en_remote_light and (self.num_of_xiaomi_button > 0),
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
        "enabled": self.en_remote_light and (self.num_of_xiaomi_button > 0),
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
    self.gen_a_wall_button_toggle_automation( button_state_list=["1", "single", "single_left", "single_right", "single_center", 
                                                                 "button_1_single", "button_2_single", "button_3_single"],
                                              button_state_name='Single',
                                              light_list=self.ceiling_lights,
                                              light_name='Ceiling Light')

  def gen_a_wall_button_toggle_automation(self,button_state_list, button_state_name, light_list, light_name, button_list=None):
    if button_list is None:
      button_list = self.wall_buttons
      
    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Wall Switch-" + button_state_name + " Press - Toggle " + light_name + "-" + self.room_name,
        "enabled": self.en_remote_light,
        "trigger": [
          {
            "platform": "state",
            "entity_id": button_list,
            "to": button_state_list
          }
        ],
        "action": [
            self.turn(light_list, "toggle") 
        ]
      }
    ]

  def gen_wall_button_double_automations(self):
    self.automations += [
      {
        "alias":"ZLB-" + self.automation_room_name + "Wall Switch - Double Press - Leave Room and Turn Off Everything" + "-" + self.room_name,
        "enabled": self.en_remote_light,
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.wall_buttons,
            "to":  ["2", "double", "double_left", "double_right", "double_center"]
          }
        ],
        "action": [
          {
            "service": "automation.trigger",
            "entity_id": [self.automation_lights_off['id'],
                          self.automation_heating_off['id']]
          }
        ]
      }
    ]

  def gen_occupancy_automations(self):
    
    #print ("[OC] " + self.room_name + " occupancy_on_x_min_ratio_sensor is " + self.occupancy_on_x_min_ratio_sensor)
    
    self.automations += [
      {
        "alias":"ZOc-" + self.automation_room_name + "Occupancy Update" + "-" + self.room_name,
        "enabled": self.en_occupancy,
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
           "data": {"occupancy_entity_str":           self.room_occupancy,
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
  def turn(self, entity_list, state=None, light_brightness=None, tv_brightness=None):
    assert state in ['on', 'off', 'toggle', None], "State has to be one of 'on', 'off', 'toggle', None"

    if light_brightness != None:
      action_service = {"service" : "light.turn_on",
                        "entity_id" : entity_list,
                        "data": {"brightness_pct": light_brightness}}
    elif tv_brightness != None:
      action_service = {"service" : "samsungtv_smart.select_picture_mode",
                        "data": {"entity_id" : entity_list,
                                 "picture_mode": "Movie"    if tv_brightness in [1, '1'] else \
                                                 "Natural"  if tv_brightness in [2, '2'] else \
                                                 "Standard" if tv_brightness in [3, '3'] else \
                                                 "Dynamic"}}
      #action_service = {"service": "input_select.select_option",
      #                  "target": {
      #                    "entity_id": self.room_entity + "_tv_picture_mode"
      #                  },
      #                  "data":{
      #                    "option": "Movie"    if tv_brightness in [1, '1'] else \
      #                              "Natural"  if tv_brightness in [2, '2'] else \
      #                              "Standard" if tv_brightness in [3, '3'] else \
      #                              "Dynamic"}} 
    elif entity_list == self.curtains:
      action_service = {"service": "cover.open_cover"       if state == 'on'     else \
                                   "cover.close_cover"      if state == 'off'    else \
                                   "cover.toggle"           if state == 'toggle' else None,
                        "entity_id": entity_list}
    else:
      action_service = {"service": "homeassistant.turn_on"  if state == 'on'     else \
                                   "homeassistant.turn_off" if state == 'off'    else \
                                   "homeassistant.toggle"   if state == 'toggle' else None,
                        "entity_id": entity_list}

    if entity_list != None:
      return action_service
    else:
      return {"service": "script.do_nothing"}

  def callSceneService(self, scene_name):  
      parallel_enable = True  
      scene_service = []  
      if   scene_name == 'All White':
          scene_service += [self.turn(self.lamps + self.ceiling_lights + self.leds, "on"),
                            self.turn(self.tvs, tv_brightness=3)]
      elif scene_name == 'Ceiling Light White':
          scene_service += [self.turn(self.leds + self.lamps, "off"),
                            self.turn(self.ceiling_lights, "on"),
                            self.turn(self.tvs, tv_brightness=3)]                            
      elif scene_name == 'Lamp LED White':
          scene_service += [self.turn(self.ceiling_lights, "off"),
                            self.turn(self.lamps + self.leds, "on"),
                            self.turn(self.tvs, tv_brightness=3)]
      elif scene_name == 'LED White':
          scene_service += [self.turn(self.ceiling_lights + self.lamps, "off"),
                            self.turn(self.leds, "on"),
                            self.turn(self.tvs, tv_brightness=2)]
      elif scene_name == 'Hue': 
          parallel_enable = False
          scene_service += [self.turn(self.lamps + self.leds, "on", light_brightness=100),
                            {"service" : "pyscript.set_rgb_light_list",
                             "data": {"light_list": self.lamps + self.ceiling_lights+ self.leds}},
                            self.turn(self.tvs, tv_brightness=3)]
      elif scene_name == 'Night Mode': 
          scene_service += [{ "service": "homeassistant.turn_on",
                              "entity_id": "scene." + self.room_entity + "_night_mode" }]
      elif scene_name == 'Dark Night Mode': 
          scene_service += [{ "service": "homeassistant.turn_on",
                              "entity_id": "scene." + self.room_entity + "_dark_night_mode" }]
      elif scene_name == 'All Off':
          scene_service += [self.turn(self.lamps + self.ceiling_lights+ self.leds, "off")]

      if parallel_enable == True:
        scene_service = [{"parallel":scene_service}] 
      return scene_service

  def setNewScene(self, new_scene):
    seq = {
      "service": "input_select.select_option",
       "target": {
         "entity_id": self.room_scene
       },
       "data":{
         "option": new_scene
       }
      }
    return seq
        
  def ifOldSceneSetNewScene(self, old_scene, new_scene):
    cond_seq = {
        "conditions": 
          { "condition": "state",
            "entity_id": self.room_scene,
            "state": old_scene
          },
        "sequence": self.setNewScene(new_scene)
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
      cond_seq = self.ifOldSceneSetNewScene(self.cur_scene, nxt_scene)
      self.cur_scene = nxt_scene

    return cond_seq


  def alwaysOnIf(self, cond):
    return {"condition": "state",
            "entity_id": "input_boolean.always_on" if cond else "input_boolean.always_off",
            "state": "on"
           }

  def setTvBrightness (self, brightness):
    seq = {
       "service": "input_select.select_option",
       "target": {
         "entity_id": self.room_entity + "_tv"
       },
       "data":{
         "option": "Movie"    if brightness in [1, '1'] else \
                   "Natural"  if brightness in [2, '2'] else \
                   "Standard" if brightness in [3, '3'] else \
                   "Dynamic"
       }
      }
    return seq

  def callSceneServiceIfSelected(self, scene_name):
    cond_seq = {
        "conditions": [
          {
            "condition": "state",
            "entity_id": self.room_scene,
            "state": scene_name
          }
        ],
        "sequence": self.callSceneService(scene_name) 
      }
    return cond_seq

  # Create a new yaml and write to it
  def writeYaml (self):
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
          if entity["enabled"] == True:
            # remove 'enabled' key
            entity.pop('enabled')
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
          if entity["enabled"] == True:
            # remove 'enabled' key
            entity.pop('enabled')
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
    self.en_scene              = True            
    self.en_occupancy          = True        
    self.en_group_auto         = True       
    self.en_motion_light       = True
    self.en_remote_light       = True
    self.en_temp_control       = True
    self.en_temp_calibration   = True
    self.en_scene_colour_led   = True
    self.en_scene_colour_lamp  = True
    self.en_cst_scene          = True
    self.en_motion_bed_led     = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.master_room_bed_motion_sensor_motion",
      "binary_sensor.master_room_entrance_motion_sensor_motion",
      "binary_sensor.master_room_stair_motion_sensor_motion",
      "binary_sensor.master_room_dressing_table_motion_sensor_motion",
      "binary_sensor.master_room_tv_motion_sensor_motion",
      "binary_sensor.master_room_drawer_motion_sensor_motion",
      "binary_sensor.master_toilet_dressing_room_motion_sensor_motion"
    ]
    
    self.non_bed_motion_sensors = [
      "binary_sensor.master_room_entrance_motion_sensor_motion",
      "binary_sensor.master_room_stair_motion_sensor_motion",
      "binary_sensor.master_room_dressing_table_motion_sensor_motion",
      "binary_sensor.master_room_tv_motion_sensor_motion",
      "binary_sensor.master_room_drawer_motion_sensor_motion",
      "binary_sensor.master_toilet_dressing_room_motion_sensor_motion"   
    ]
    
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
    self.curtains               = ["cover.master_room_blind",
                                   "cover.master_room_curtain"] 
                                   
  def get_remote_entities(self):  
    super().get_remote_entities()
    self.wall_buttons            = ["sensor." + self.room_entity + "_entrance_wall_button"]
    self.buttons                 = self.wall_buttons + self.xiaomi_buttons



class MasterToilet(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Master Toilet'    
    self.room_short_name       = 'MT'
    self.en_occupancy          = True       
    self.en_group_auto         = True
    self.en_temp_control       = True
    self.en_scene              = True            
    self.en_motion_light       = True
    self.en_remote_light       = True

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



class Kitchen(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Kitchen'    
    self.room_short_name       = 'KC'
    self.en_occupancy          = True       
    self.en_group_auto         = True
    self.en_temp_control       = True
    self.en_temp_calibration   = True
    self.en_scene              = True            
    self.en_motion_light       = True
    self.en_remote_light       = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.kitchen_worktop_motion_sensor_motion",
      "binary_sensor.kitchen_dining_motion_sensor_motion"
    ]

  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.ceiling_lights          = ["light.kitchen_ceiling_light",
                                    "light.kitchen_dining_light"]
    self.leds                    = ["switch.kitchen_floor_led"]
    self.lights                  = self.leds + self.lamps + self.ceiling_lights

  # Kitchen - Left - Ceiling light & Dining light
  # Kitchen - Right - Floor LED
  # [TODO] Kitchen - Middle - Kitchen worktop led
  # [TODO] Kitchen - xxx - Extractor
  def gen_wall_button_single_automations(self):
    self.gen_a_wall_button_toggle_automation( button_state_list=["single_left"],
                                              button_state_name='Single Left',
                                              light_list=self.ceiling_lights,
                                              light_name='Ceiling Light')

    self.gen_a_wall_button_toggle_automation( button_state_list=["single_right"],
                                              button_state_name='Single Right',
                                              light_list=self.leds,
                                              light_name='Floor LED')

class LivingRoom(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Living Room'    
    self.room_short_name       = 'LR'
    self.num_of_xiaomi_button  = 1
    self.num_of_lamps          = 2    
    # Enables
    self.en_scene              = True            
    self.en_occupancy          = True        
    self.en_group_auto         = True       
    self.en_motion_light       = True
    self.en_remote_light       = True
    self.en_temp_control       = True
    self.en_temp_calibration   = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.living_room_sofa_motion_sensor_motion",
      "binary_sensor.living_room_tv_motion_sensor_motion",
      "binary_sensor.tais_desk_motion_sensor_motion"
    ]

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



class EnSuiteRoom(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'En-suite Room'    
    self.room_short_name       = 'ER'
    self.num_of_xiaomi_button  = 1
    self.num_of_lamps          = 2
    # Enables
    self.en_scene              = True            
    self.en_occupancy          = True        
    self.en_group_auto         = True       
    self.en_motion_light       = True
    self.en_remote_light       = True
    self.en_temp_control       = True
    self.en_temp_calibration   = True
    self.en_led_only_scene     = True
    self.en_motion_bed_led     = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.en_suite_room_bed_motion_sensor_motion",
      "binary_sensor.en_suite_room_entrance_motion_sensor_motion",
      "binary_sensor.en_suite_room_floor_motion_sensor_motion"
    ]
    
    self.non_bed_motion_sensors = 'binary_sensor.en_suite_room_floor_motion_sensor_motion'

  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.leds                    = ["light.en_suite_room_bed_led"] 
    self.lights                  = self.leds + self.lamps + self.ceiling_lights



class EnSuiteToilet(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'En-suite Toilet'    
    self.room_short_name       = 'ET'
    self.en_occupancy          = True       
    self.en_group_auto         = True
    self.en_temp_control       = True
    self.en_scene              = True            
    self.en_motion_light       = True
    self.en_remote_light       = True
    self.en_led_only_scene     = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.en_suite_toilet_motion_sensor_motion"
    ]


class GuestRoom(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Guest Room'    
    self.room_short_name       = 'GR'
    self.num_of_xiaomi_button  = 0
    self.num_of_lamps          = 0
    self.en_occupancy          = True       
    self.en_group_auto         = True
    self.en_temp_control       = True
    self.en_scene              = True            
    self.en_motion_light       = True
    self.en_remote_light       = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.guest_room_door_motion_sensor_motion",
      "binary_sensor.guest_room_bed_motion_sensor_motion"
    ]

  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.leds                    = ["light.guest_room_bed_led"] 
    self.lights                  = self.leds + self.lamps + self.ceiling_lights



class GuestToilet(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Guest Toilet'    
    self.room_short_name       = 'GT'
    self.en_occupancy          = True       
    self.en_group_auto         = True
    self.en_temp_control       = True
    self.en_scene              = True            
    self.en_motion_light       = True
    self.en_remote_light       = True

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

  # Guest Toilet - Left key - Ceiling light
  # Guest Toilet - Right key - Floor LED
  def gen_wall_button_single_automations(self):
    self.gen_a_wall_button_toggle_automation( button_state_list=["single_left"],
                                              button_state_name='Single Left',
                                              light_list=self.ceiling_lights,
                                              light_name='Ceiling Light')

    self.gen_a_wall_button_toggle_automation( button_state_list=["single_right"],
                                              button_state_name='Single Right',
                                              light_list=self.leds,
                                              light_name='Floor LEDs')


class Study(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Study'    
    self.room_short_name       = 'ST'
    self.num_of_xiaomi_button  = 0
    self.num_of_lamps          = 0
    self.en_occupancy          = True       
    self.en_group_auto         = True
    self.en_temp_control       = True
    self.en_scene              = True            
    self.en_motion_light       = True
    self.en_remote_light       = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.study_motion_sensor_motion",
      "binary_sensor.kes_desk_motion_sensor_motion"
    ]


class Garden(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Garden'    
    self.room_short_name       = 'GD'
    self.en_occupancy          = True       
    self.en_group_auto         = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.garden_sliding_door_motion_sensor_motion",
      "binary_sensor.garden_bike_shed_motion_sensor_motion"
    ]


class Corridor(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Corridor'    
    self.room_short_name       = 'CR'
    self.en_occupancy          = True       
    self.en_group_auto         = True
    self.en_temp_control       = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.ground_corridor_motion_sensor_motion",
      "binary_sensor.first_corridor_motion_sensor_motion"
    ]


class GroundToilet(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Ground Toilet'
    self.room_short_name       = '0T'
    self.en_occupancy          = True       
    self.en_group_auto         = True
    self.en_temp_control       = True
    self.en_scene              = True            
    self.en_motion_light       = True
    self.en_remote_light       = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.ground_toilet_motion_sensor_motion"
    ]


class WholeHome(RoomBase):
  def get_room_config(self):
    super().get_room_config()
    self.room_name             = 'Whole Home'
    self.room_short_name       = 'WH'
    self.en_occupancy          = True       

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
  rooms = [ LivingRoom(),
            Kitchen(),
            EnSuiteToilet(),
            GuestRoom(),
            Study(),
            GuestToilet(),
            Garden(),
            Corridor(),
            EnSuiteRoom(),
            GroundToilet(),
            MasterRoom(),
            MasterToilet(),
            WholeHome()
            ]         
  yaml.Dumper.ignore_aliases = lambda *args : True
  
  for room in rooms:
    room.writeYaml()

read_core_entity_entries_json()
check_core_entity_unexpected_entities()

if args.create_system_config:
  read_core_entity_entries_json()
  remove_auto_gen_automation_entities()
  write_core_entity_entries_json()

