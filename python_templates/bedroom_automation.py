import re
import yaml
import os
#from ruamel.yaml import YAML
#from varname import nameof

class RoomBase:
  def __init__ (self, room_entity, num_of_xiaomi_button=1, num_of_lamps=2):
    self.room_entity           = room_entity
    self.num_of_xiaomi_button  = num_of_xiaomi_button
    self.num_of_lamps          = num_of_lamps
    self.room_name  = 'En-suite Room'   if self.room_entity == 'en_suite_room'   else \
                      'Master Room'     if self.room_entity == 'master_room'     else \
                      'Guest Room'      if self.room_entity == 'guest_room'      else \
                      'En-suite Toilet' if self.room_entity == 'en_suite_toilet' else \
                      'Master Toilet'   if self.room_entity == 'master_toilet'   else \
                      'Guest Toilet'    if self.room_entity == 'guest_toilet'    else \
                      'Groud Toilet'    if self.room_entity == 'ground_toilet'   else \
                      'Study'           if self.room_entity == 'study'           else \
                      'Kitchen'         if self.room_entity == 'kitchen'         else \
                      'Garden'          if self.room_entity == 'garden'          else \
                      'Living Room'     if self.room_entity == 'living_room'     else \
                      'Corridor'        if self.room_entity == 'corridor'        else \
                      None

    self.room_short_name = 'ER'         if self.room_entity == 'en_suite_room'   else \
                           'MR'         if self.room_entity == 'master_room'     else \
                           'GR'         if self.room_entity == 'guest_room'      else \
                           'ET'         if self.room_entity == 'en_suite_toilet' else \
                           'MT'         if self.room_entity == 'master_toilet'   else \
                           'GT'         if self.room_entity == 'guest_toilet'    else \
                           '0T'         if self.room_entity == 'ground_toilet'   else \
                           'ST'         if self.room_entity == 'study'           else \
                           'KC'         if self.room_entity == 'kitchen'         else \
                           'GD'         if self.room_entity == 'garden'          else \
                           'LR'         if self.room_entity == 'living_room'     else \
                           'CR'         if self.room_entity == 'corridor'        else \
                           None
    
    self.automation_room_name = self.room_short_name + " " + self.room_name + " "

    self.room_type =  'bedroom'       if (('_room' in self.room_entity) and ('living_room' != self.room_entity)) else \
                      'toilet'        if '_toilet' in self.room_entity else \
                      'common_area'

    self.west_face_windows = True     if self.room_entity in ['en_suite_room', 'master_room'] else False
    
    # Motion sensor entities
    self.bed_motion_sensors      = ["binary_sensor." + self.room_entity + "_bed_motion_sensor_motion"]
    self.all_motion_sensor       =  "group."         + self.room_entity + "_motion"
    self.entrance_motion_sensors = ["binary_sensor." + self.room_entity + "_entrance_motion_sensor_motion"] if self.room_type == 'bedroom' else \
                                   [self.all_motion_sensor]
    self.room_occupancy          = self.room_entity + "_occupancy"                           
    self.occupancy_state_duration= 4 # Minutes
    self.occupancy_on_x_min_ratio_sensor  = []
    self.occupancy_on_2x_min_ratio_sensor = []

    # Button (sensor) entities
    self.xiaomi_buttons          = []
    for i in range(self.num_of_xiaomi_button):
      self.xiaomi_buttons       += ["sensor." + self.room_entity + "_button"] 
      if self.num_of_xiaomi_button != 1:
        self.xiaomi_buttons[i]  += "_" + str(i+1)
    self.wall_buttons            = ["sensor." + self.room_entity + "_entrance_wall_button"] if self.room_entity == 'master_room' else \
                                   ["sensor." + self.room_entity + "_wall_button"]
    self.buttons                 = self.wall_buttons + self.xiaomi_buttons

    # Light/Switch entities
    self.bed_leds                = ["light." + self.room_entity + "_bed_led"      ] if self.room_type == 'bedroom' else None
    self.other_leds              = ["light.master_room_drawer_led",
                                    "light.master_room_tv_led"     ] if self.room_entity == 'master_room' else []
    self.leds                    = ["light.living_room_tv_led", 
                                    "light.living_room_sofa_led"] if self.room_entity == 'living_room' else \
                                   self.other_leds + self.bed_leds

    self.ceiling_lights          = ["light." + self.room_entity + "_ceiling_light"]
    
    self.lamps                   = []
    for i in range(num_of_lamps):
      self.lamps                += ["light." + room_entity + "_lamp"]
      if num_of_lamps != 1:
        self.lamps[i]           += "_" + str(i+1)
    self.lamps                   = ["light.living_room_floor_light_1", 
                                    "light.living_room_3_head_lamp_1",
                                    "light.living_room_3_head_lamp_2",
                                    "light.living_room_3_head_lamp_3",
                                    "switch.living_room_floor_light_3"] if self.room_entity == 'living_room' else \
                                   self.lamps    

    self.lights                  = self.leds + self.lamps + self.ceiling_lights

    # TV entities
    self.tv_room_entity          = 'portable' if self.room_entity == 'en_suite_room' else self.room_entity
    self.tvs                     = ["media_player." + self.tv_room_entity + "_tv"]
    self.fire_tvs                = ["media_player." + self.tv_room_entity + "_fire_tv"]

    # Time setup
    self.daytime_lights_off_timeout   = "00:15:00"
    self.nighttime_lights_off_timeout = "02:00:00" if self.room_type == "bedroom" else \
                                        self.daytime_lights_off_timeout
    self.daytime_start                = "10:00:00"
    self.afternoon_start              = "13:00:00"
    self.daytime_end                  = "22:00:00"

    # Cover entities
    self.curtains               = ["cover.master_room_blind",
                                   "cover.master_room_curtain"] if self.room_entity == "master_room" else None
    # Temperature sensor entities
    self.outside_temperature    = ["sensor.cambridge_city_airport_temperature"]

    # Scene 
    self.room_scene             =                   self.room_entity + "_scene"
    self.room_scene_entity      = "input_select." + self.room_entity + "_scene"
    
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

    # Render entity declarations
    self.get_entity_declarations()

    # Render Automation
    self.automations  = []
    self.automations += self.get_lighting_automations()
    self.get_automation_group_declarations()
  
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

    ratio_sensor_config = {
        "platform": "history_stats",
        "name": sensor_name,
        "entity_id": self.all_motion_sensor,
        "state": "on",
        "type": "ratio",
        "duration": {
          "minutes": str(x_minutes_total)
        },
        "end": "{{ (now() | as_timestamp) | as_datetime | as_local }}"
      }
    return ratio_sensor_config


  def get_entity_declarations(self):
    self.entity_declarations = {
      "input_select":{
        self.room_scene : {
          "name" : self.room_name + " Scene",
          "options":([
            "Hue"
          ] if self.room_entity == 'master_room' else [])  
        + [ "All White",
            "Lamp LED White",
            "LED White",
            "Night Mode",
            "Dark Night Mode",
            "All Off"
          ]
        },
        self.room_occupancy : {
          "name" : self.room_name + " Occupancy",
          "options":[
            "Outside",
            "Just Entered",
            "Stayed Inside"
          ]
        }
      },

      "sensor":[
        self.get_occupancy_ratio_sensor_config('1x'),
        self.get_occupancy_ratio_sensor_config('2x')
      ]
    }
    
    
  def get_automation_group_declarations(self):    
    # Generate automations group 
    self.automation_entity_list = []
    for automation in self.automations:
      self.automation_entity_list += [automation['id']]

    self.entity_declarations |= {
      "group": {
        self.room_entity + "_auto_gen_automations" : {
          "name": self.room_name + " Auto-gen Automations",
          "entities": self.automation_entity_list 
        }  
      }
    }


  # Lighting Automations
  def get_lighting_automations(self):
    self.automations = []
    self.automation_lights_on = {"alias":"L-" + self.automation_room_name + "Ceiling Lights On Or Open Curtains If Entering to Room"}
    self.automation_lights_on['id'] = self.getIDFromAlias(self.automation_lights_on['alias'])
    self.automations += [self.automation_lights_on | {
        # Lights on automation are initially off until it is automatically turned on when no present detected
        #"initial_state": False,
        "trigger": [
          {
            "entity_id": self.entrance_motion_sensors,
            "platform": "state",
            "to": "on"
          }
        ],
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
              # IF - in daytime
              #    - not the hot afternoons in summer
              #    not (i.e. outdoor temperature above 15 & in the afternoon & in the summer)
              #.   then open curtain
              {
                "conditions": [
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
              }
            ],
            # ELSE - in nighttime/hot days in summer afternoon
            #.       turn on master room ceiling/bed lights
            "default": [
              {
                # only turn on bright lights on non-sleeping times
                "choose": [
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
                "default": self.setNewScene("Lamp LED White") if self.room_entity != 'living_room' else \
                           self.setNewScene("All White")
              }
            ]
          }
        ]
      }
    ]

    self.automation_lights_off = {"alias":"L-" + self.automation_room_name + "Lights Off If No Person"}
    self.automation_lights_off['id'] = self.getIDFromAlias(self.automation_lights_off['alias'])
    self.automations += [self.automation_lights_off | {
        "trigger": [
          {
            "platform": "state",
            "from": "on",
            "to": "off",
            "for": self.daytime_lights_off_timeout,
            "entity_id": self.all_motion_sensor
          },
          {
            "minutes": "/5",
            "platform": "time_pattern"
          }
        ],
        "condition": [
          {
            "condition": "or",
            "conditions": [
              # in daytime, turn off if no person for shorter time
              {
                "condition": "and",
                "conditions": [
                  {
                    "after": self.daytime_start,
                    "before": self.daytime_end,
                    "condition": "time"
                  },
                  {
                    "condition": "state",
                    "entity_id": self.all_motion_sensor,
                    "for": self.daytime_lights_off_timeout,
                    "state": "off"
                  }
                ]
              },
              # in nighttime, turn off if no person for longer time
              {
                "condition": "and",
                "conditions": [
                  {
                    "after": self.daytime_end,
                    "before": self.daytime_start,
                    "condition": "time"
                  },
                  {
                    "condition": "state",
                    "entity_id": self.all_motion_sensor,
                    "for": self.nighttime_lights_off_timeout,
                    "state": "off"
                  }
                ]
              }
            ]
          }
        ],
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
    
    self.automations += [{
        "alias" : "LB-" + self.automation_room_name + "Remote Button - Single - Applies Different Scenes (State Execution)",
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.xiaomi_buttons,
            "to": "single"
          }
        ],
        "mode":"queued",
        "action": [
          {
            "choose": [
              # State Machine
              # "All Off"
              # -> "All White" ->  "Lamp LED White" -> "LED White"
              # -> "Hue" -> "Night Mode" ->  "Dark Night Mode"
              #
              #  Default room supports these secnes 
              self.ifOldSceneSetNewScene("All Off",         "All White"),
              self.ifOldSceneSetNewScene("All White",       "Lamp LED White"),
              self.ifOldSceneSetNewScene("Lamp LED White",  "LED White")
            ] + ([
              # Master Room supports a few more scenes
              self.ifOldSceneSetNewScene("LED White",       "Hue"),
              self.ifOldSceneSetNewScene("Hue",             "Night Mode"),
              self.ifOldSceneSetNewScene("Night Mode",      "Dark Night Mode"),
              self.ifOldSceneSetNewScene("Dark Night Mode", "All Off")
            ] if self.room_entity == 'master_room' else [
              # Default Room does not support extra scenes 
              self.ifOldSceneSetNewScene("LED White",       "All Off")
            ]),
            "default": self.setNewScene("Lamp LED White")
          }
        ]
    }]

    self.automations += [{
        "alias" : "LB-" + self.automation_room_name + "Remote Button - Single - Applies Different Scenes (Execution)",
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.room_scene_entity,
          }
        ],
        "mode":"queued",
        "action": [
          {
            "choose": [
              self.callSceneServiceIfSelected("All White"),
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
        "alias":"LB-" + self.automation_room_name + "Remote Button - Double - Toggle Lamps",
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.xiaomi_buttons,
            "to": "double"
          }
        ],
        "action": [
            self.turn(self.lamps, "toggle"),
        ]
      }
    ]

    self.automations += [
      {
        "alias":"LB-" + self.automation_room_name + "Remote Button - Triple - Set Scene",
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.xiaomi_buttons,
            "to": "triple"
          }
        ],
        "action": [
            self.turn(self.lamps, "toggle"),
        ]
      }
    ]

    self.automations += [
      {
        "alias":"LB-" + self.automation_room_name + "Remote Button - Long - Toggle LEDs",
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

    self.automations += [
      {
        "alias":"LB-" + self.automation_room_name + "Wall Switch - Single Press - Toggle Ceiling Light",
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.wall_buttons,
            "to": "single"
          }
        ],
        "action": [
            self.turn(self.ceiling_lights, "toggle") 
        ]
      }
    ]

    self.automations += [
      {
        "alias":"LB-" + self.automation_room_name + "Wall Switch - Double Press - Leave Room and Turn Off Everything",
        "trigger": [
          {
            "platform": "state",
            "entity_id": self.wall_buttons,
            "to": "double"
          }
        ],
        "action": [
          {
            "service": "automation.trigger",
            "entity_id": self.automation_lights_off['id']
          }
        ]
      }
    ]

    self.automations += [
      {
        "alias":"Oc-" + self.automation_room_name + "Occupancy Update",
        "trigger": [
          {
            "entity_id": self.all_motion_sensor,
            "platform": "state",
            "to": "on"
          },
          {
            "entity_id": self.all_motion_sensor,
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
           "data": {"occupancy_entity_str":        self.room_occupancy,
                    "motion_str":                  self.all_motion_sensor,                                 
                    "motion_ratio_for_x_min_str":  self.occupancy_on_x_min_ratio_sensor,
                    "motion_ratio_for_2x_min_str": self.occupancy_on_2x_min_ratio_sensor
                   },
          }
        ]
      }
    ]


    for self.automation in self.automations:
      self.automation['id'] = self.getIDFromAlias(self.automation['alias'])

    return self.automations;

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
          scene_service += [self.turn(self.lamps + self.ceiling_lights+ self.leds, "on"),
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

  def setNewScene (self, new_scene):
    seq = {
      "service": "input_select.select_option",
       "target": {
         "entity_id": self.room_scene_entity
       },
       "data":{
         "option": new_scene
       }
      }
    return seq
        
  def ifOldSceneSetNewScene (self, old_scene, new_scene):
    cond_seq = {
        "conditions": 
          { "condition": "state",
            "entity_id": self.room_scene_entity,
            "state": old_scene
          },
        "sequence": self.setNewScene(new_scene)
      }
    return cond_seq

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
            "entity_id": self.room_scene_entity,
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
    f.write("automation:\n")
    for automation in room.automations:
      f.write(yaml.dump([automation], sort_keys=False, width=float("inf")))
      f.write("\n\n")
    #f.write(yaml.dump([room.automations[3]], sort_keys=False, width=float("inf")))
    f.close()


rooms = [RoomBase('en_suite_room',num_of_xiaomi_button=1),
         RoomBase('master_room',  num_of_xiaomi_button=2),
         RoomBase('living_room',  num_of_xiaomi_button=1)]


#YAML = YAML()
#print (YAML.dump(rooms[0].automation))

yaml.Dumper.ignore_aliases = lambda *args : True

for room in rooms:
  room.writeYaml()

  #print ("\n\n")
  #print (yaml.dump(room.automations, sort_keys=False))
  #print ("\n\n")

  #for automation in room.automations:
  #  print (yaml.dump(automation['id'], sort_keys=False))


#print ([list(room.lamps), list(room.leds)])

#  print (list(room.leds))

