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
    self.all_motion_sensors      = ["group."         + self.room_entity + "_motion"]
    self.entrance_motion_sensors = ["binary_sensor." + self.room_entity + "_entrance_motion_sensor_motion"] if self.room_type == 'bedroom' else \
                                   self.all_motion_sensors

    # Button (sensor) entities
    self.xiaomi_buttons          = []
    for i in range(self.num_of_xiaomi_button):
      self.xiaomi_buttons       += ["sensor." + self.room_entity + "_button"] 
      if self.num_of_xiaomi_button != 1:
        self.xiaomi_buttons[i]  += "_" + str(i+1)
    self.wall_buttons            = ["sensor." + self.room_entity + "_entrance_wall_button"] if self.room_entity == 'master_room' else \
                                   ["sensor." + self.room_entity + "_ceiling_light_wall_button"]
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
                                    "light.living_room_3_head_lamp_3"] if self.room_entity == 'living_room' else \
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

    # Render Automation
    self.automations  = []
    self.automations += self.get_lighting_automations()
    self.entity_declarations = {}    
    self.get_entity_declarations()

  def get_entity_declarations(self):
    self.entity_declarations = {
      "input_select":{
        self.room_entity + "_scene" : {
          "name" : self.room_name + " Scene",
          "options":[
            "All White",
            "Lamp Led White",
            "LED White",
            "Hue",
            "Night Mode",
            "Dark Night Mode"
          ]
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
                    "sequence": self.turn(self.lamps + self.ceiling_lights, 'on')
                  }
                ],
                "default": self.turn(self.leds, 'on')
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
            "entity_id": self.all_motion_sensors
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
                    "entity_id": self.all_motion_sensors,
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
                    "entity_id": self.all_motion_sensors,
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
          self.turn(self.lights, 'off'),
          self.turn(self.tvs, 'off'),
          self.turn(self.curtains, 'off')
        ]
      }
    ]

    self.automations += [{
        "alias" : "LB-" + self.automation_room_name + "Remote Button - Single - Toggle Bed Lights/Ceiling Lights",
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
            # N.B. choose will only choose the first matching condition to execute
            #      and exit the choose function immediately after the cooresponding
            #      sequence completed and will not continue to test other condtions.
            #      So it is a proper IF-ELSE statement.
            "choose": [
              # IF ceiling lights on - turn off ceiling lights and turn on bedside lights + LED
              {
                "conditions": [
                  {
                    "condition": "state",
                    "entity_id": self.ceiling_lights,
                    "state": "on"
                  }
                ],
                "sequence": {
                  "parallel": [
                    self.turn(self.ceiling_lights, "off"),
                    self.turn(self.lamps + self.leds, "on")
                  ]
                }
              },
              # ELSE IF bed lamp lights on - turn off all lights apart from LED
              {
                "conditions": [
                  {
                    "condition": "state",
                    "entity_id": self.lamps,
                    "state": "on"
                  }
                ],
                "sequence": {
                  "parallel": [
                    self.turn(self.lamps+self.ceiling_lights, "off"),
                    self.turn(self.leds, "on")
                  ]
                }
              },
              # ELSE IF bed LDE on - turn off all lights
              {
                "conditions": [
                  {
                    "condition": "state",
                    "entity_id": self.leds,
                    "state": "on"
                  }
                ],
                "sequence": self.turn(self.lamps + self.ceiling_lights+ self.leds, "off")

              }
            ],
            # ELSE - no lights on - turn on all lightss
            "default": self.turn(self.lamps + self.ceiling_lights+ self.leds, "on")
          }
        ]
      }
    ]

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

    for self.automation in self.automations:
      self.automation['id'] = self.getIDFromAlias(self.automation['alias'])

    return self.automations;

  # Generate automation ID/entity_name based on alias name
  def getIDFromAlias (self, alias):
    id = "automation." + alias.lower()
    id = re.sub("-", "_", id)
    id = re.sub("/", "_", id)
    id = re.sub("\s", "_", id)
    id = re.sub("(_+)", "_", id)
    return id

  # Create service call for turn on/off entities
  def turn(self, entity_list, state):
    assert state in ['on', 'off', 'toggle'], "State has to be on, off, toggle"

    if entity_list == self.curtains:
      action_service = {"service": "cover.open_cover"       if state == 'on'     else \
                                   "cover.close_cover"      if state == 'off'    else \
                                   "cover.toggle"           if state == 'toggle' else None}
    else:
      action_service = {"service": "homeassistant.turn_on"  if state == 'on'     else \
                                   "homeassistant.turn_off" if state == 'off'    else \
                                   "homeassistant.toggle"   if state == 'toggle' else None}
    action_service |= {"entity_id": entity_list}
    if entity_list != None:
      return action_service
    else:
      return {"service": "script.do_nothing"}

  # Create a new yaml and write to it
  def writeYaml (self):
    # File Path
    self.script_dir         = os.path.dirname(os.path.realpath(__file__))
    self.auto_gen_dir       = self.script_dir + "/../packages/_auto_generated_packages/"
    self.auto_gen_yaml_path = self.auto_gen_dir + "/auto_gen_" + self.room_entity + ".yaml"

    # Open a new file and write automation
    f = open(self.auto_gen_yaml_path, "w")
    f.write("automation:\n")
    for automation in room.automations:
      f.write(yaml.dump([automation], sort_keys=False, width=float("inf")))
      f.write("\n\n")
    #f.write(yaml.dump([room.automations[3]], sort_keys=False, width=float("inf")))
    f.write(yaml.dump(self.entity_declarations, sort_keys=False, width=float("inf")))
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

  for automation in room.automations:
    print (yaml.dump(automation['id'], sort_keys=False))


#print ([list(room.lamps), list(room.leds)])

#  print (list(room.leds))

# single button - light
# double button - close light
# people present - turn on celing light
# people not present - turn off everything

