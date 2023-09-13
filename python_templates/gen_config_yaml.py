#####################################################################
# This script won't update En-suite Room/Toilet configurations
# It is intentional to stop breaking automations in tenant room. 
#####################################################################

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
  def __init__ (self, dashboard_type=None):

    # Create Empty JSON Database
    self.reset_json_environment()
    
    # Name and basic configs
    self.get_room_config()
    self.get_room_name_and_property()
    
    print ("Generating " + self.room_name + " Yaml Package")

    # Entities
    self.get_motion_sensor_entities()
    self.get_remote_entities()
    self.get_wall_switches()
    self.get_light_entities()
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
    self.populate_entnties_into_database()
    
    # Remove disabled entities
    self.remove_disabed_entities()
    # Generate user control group including automations and other controls
    self.get_automation_group_declarations()

    # Get dashboard settings
    self.dashboard_type = dashboard_type
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
    self.cfg_tv                 = False

    # Adavanced Enables
    self.cfg_scene_color_led   = False
    self.cfg_scene_color_lamp  = False
    self.cfg_custom_scene       = False
    self.cfg_led_only_scene     = False
    self.cfg_motion_bed_led     = False
    self.cfg_auto_curtain_ctl   = False
    
    # Automatically loaded by settings later
    self.cfg_flex_switch       = False
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
    self.motion_group    = "group." + self.room_entity + "_motion_group"
    self.occupancy_group = "group." + self.room_entity + "_occupancy_group"

    # Motion sensor entities
    self.bed_motion_sensors      =  ["binary_sensor." + self.room_entity + "_bed_motion_sensor_motion"] if self.room_type == 'bedroom' else []
    self.non_bed_motion_sensors  =  []
    self.all_motion_sensors      =  ["uninitialized_all_motion_sensors"]
    self.entrance_motion_sensors =  ["binary_sensor." + self.room_entity + "_entrance_motion_sensor_motion"] if self.room_type == 'bedroom' else \
                                    [self.motion_group]
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
    self.light_group             =  'group.' + self.room_entity + '_light_group'


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
    self.curtain_control_when['Lights off']                          = "input_boolean.curtain_control_" +       "when_left_"           + self.room_entity
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
                        '{{ ((state_attr(climate, "temperature")  > state_attr(climate, "current_temperature"))  and  (not states(climate, "off")) )  }}'  + \
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
    self.room_cards          = []
    self.views               = []
    self.dashboard_type      = None
    self.header_card_list    = []
    self.main_card_list      = []
    self.tail_card_list      = []    

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


  # for lovelace single entity:
  # entity
  # entity_name
  # entity_name_translation
  # card name -> can be inferred from entity name -> can be inferred from entity
  # card type -> can be inferred from entity type
  # card icon -> can be inferred from device icon if added
  # card icon color 
  # double tab action
  def getEntityCard(self, entity, entity_name=None, entity_name_translation=None, 
                          card_name=None, card_type=None,card_icon=None,card_icon_color=None,double_tab_action=None,simple=None,
                          secondary_info=None):
    card = {}     
    
    # Set up card_type based on entity_type
    if card_type is None:

      # remove entity name to get entity type
      # "light" = Remove ".living_room_ceiling_light" from "light.living_room_ceiling_light"
      entity_type = re.sub("\.(\w+)$", "", entity)

      if entity_type in ['light', 'cover', 'climate']:
        card_type = 'custom:mushroom-' + entity_type    + '-card'
      elif entity_type in ['media_player']:
        card_type = 'custom:mushroom-' + 'media-player' + '-card'
      if entity_type in ['binary_sensor', 'switch', 'input_boolean']:
        card_type = 'custom:mushroom-' + 'entity'       + '-card'
      elif entity_type in ['group']:
        card_type = 'custom:group-card'
      elif entity_type in ['sensor']:
        card_type = 'sensor'
      elif entity_type in ['input_select']:
        card_type = 'custom:mushroom-select-card'
      elif entity_type in ['input_number', 'number']:
        card_type = 'custom:mushroom-number-card'

    if entity_name is None:
      entity_name = self.getName(entity)

    if card_name is None:
      # Remove room name from entity name to get card name
      # "Ceiling Light" = Remove "Living Room" from "Living Room Ceiling Light" 
      card_name = re.sub(self.room_name, "", entity_name)

    #if entity_name_translation != None:
    #  entity_name_translation = 

    card_name = '' if card_name is None else card_name
    card_icon = '' if card_icon is None else card_icon

    # light
    if card_type == 'custom:mushroom-light-card':
      card = {
        "type": card_type,
        "fill_container": True,
        "use_light_color": False,
        "show_brightness_control": True,
        "show_color_control": False,
        "show_color_temp_control": True,
        "collapsible_controls": False,
        "name": card_name,
        "icon": card_icon,
        "entity": entity
      } | self.getCardMod('ios16_toggle', card_type=card_type, color='ios_yellow')
    
    # cover
    elif card_type == 'custom:mushroom-cover-card':
      card = {
        "type": card_type,
        "fill_container": True,
        "tap_action":{
          "action": "toggle"
        },
        "double_tap_action":{
          "action": "more-info"
        },
        "hold_action":{
          "action": "more-info"
        },                
        "show_position_control": True,
        "show_buttons_control": True,
        "name": card_name,
        "icon": card_icon,
        "entity": entity
      }

    # climate
    elif card_type == 'custom:mushroom-climate-card':
      card = {
        "type": card_type,
        "show_temperature_control": True,
        "collapsible_controls": False,
        "name": card_name,
        "icon": card_icon,
        "entity": entity
      }

    # media_player card
    # tap - toggle/navigate/more-info
    elif card_type == 'custom:mushroom-media-player-card':
      card = {
        "type": card_type,
        "fill_container": True,
        "tap_action":{
          "action": "more-info"
        },
        "volume_controls":[
         # "volume_mute",
          "volume_set",
          "volume_buttons"
        ],
        "show_volume_level": False,
        "name": card_name,
        "icon": card_icon,
        "entity": entity
      }
    # group card
    elif card_type == 'custom:group-card':
      card = {
        "type": card_type,
        "card":{
          "type": "entities",
          "title": card_name
        },
        "group": entity
      }

    # sensor
    elif card_type == 'sensor':
      if simple is True:
        card = {
          "type": card_type,
          "graph": "line",
          "name": card_name,
          "icon": card_icon,
          "entity": entity
        }
      else: # complex minigraph temperature sensor card from 
      # https://bbs.hassbian.com/forum.php?mod=redirect&goto=findpost&ptid=22509&pid=550976
        card = {
          "type": "custom:vertical-stack-in-card",
          "cards": [
            {
              "type": "custom:mushroom-template-card",
              "entity": entity,
              "primary": card_name,
              "secondary": "{{ states('" + entity + "') | round(0) }}\u00b0C\n",
              "icon": "mdi:thermometer",
              "icon_color": "{% set value = states('" + entity + "') | int %}\n{% if value < 18 %}\n  blue\n{% elif value < 28 %}\n  light-green\n{% elif value < 40 %}\n  red\n{% else %}\n  green\n{% endif %}",
              "tap_action": {
                "action": "more-info"
              }
            } | self.getCardModColor('transparent'),
            {
              "type": "custom:layout-card",
              "layout_type": "masonry",
              "layout": {
                "width": 150,
                "max_cols": 1,
                "height": "auto",
                "padding": "0px",
                "card_margin": "var(--masonry-view-card-margin, -10px 8px 15px)"
              },
              "cards": [
                {
                  "type": "custom:mini-graph-card",
                  "tap_action": {
                    "action": "more-info"
                  },
                  "entities": [
                    {
                      "entity": entity,
                      "name": "Temperature"
                    }
                  ],
                  "color_thresholds": [
                    {
                      "value": -10,
                      "color": "#0000ff"
                    },
                    {
                      "value": 18,
                      "color": "#0000ff"
                    },
                    {
                      "value": 18.1,
                      "color": "#00FF00"
                    },
                    {
                      "value": 27,
                      "color": "#00FF00"
                    },
                    {
                      "value": 27.1,
                      "color": "#FF0000"
                    },
                    {
                      "value": 40,
                      "color": "#FF0000"
                    }
                  ],
                  "hours_to_show": 24,
                  "line_width": 3,
                  "animate": True,
                  "show": {
                    "name": False,
                    "icon": False,
                    "state": False,
                    "legend": False,
                    "fill": "fade"
                  },
                  "card_mod": {
                    "style": "ha-card {\n  background: none;\n  box-shadow: none;\n  --ha-card-border-width: 0;\n}"
                  }
                }
              ]
            }
          ]
        }

    # entity card
    # binary_sensor    - tap to more-info
    # switch           - tap to toggle
    # input boolean
    elif card_type == 'custom:mushroom-entity-card':
      card = {
        "type": card_type,
        "fill_container": True,
        "tap_action":{
          "action": "toggle"
        },
        "name": card_name,
        "icon": card_icon,
        "entity": entity
      }
    
    # entities card
    # input_timer
    elif card_type == 'entities':
      card = {
        "type": card_type,
        "entities":[
          { "name":   card_name,
            "entity": entity}
        ]
      }

    # schduler card
    elif card_type == 'custom:scheduler-card':
      card = {
        "type": card_type,
        "include": entity,
        "exclude": [],
        "title": True,
        "discover_existing": True,
        "time_step": 30        
      }

    # timer card
    elif card_type == 'custom:flipdown-timer-card':
      card = {
        "type": card_type,
        "show_hour": True,
        "show_title": True,
        "theme": 'dark',
        "styles": {
          "rotor": {
            "width": "50px",
            "height": "80px"},
          "button": {
            "width": "100px",
            "location": "bottom"}
        },
        "name": card_name,
        "icon": card_icon,
        "entity": entity
      }

    # input_number
    # number
    elif card_type == 'custom:mushroom-number-card':
      card = {
        "type": card_type,
        "fill_container": True,
        "tap_action":{
          "action": "more-info"
        },
        "display_mode": "buttons",
        "name": card_name,
        "icon": 'mdi:counter' if card_icon is None else card_icon,
        "entity": entity
      }

    # input_select
    elif card_type == 'custom:mushroom-select-card':
      card = {
        "type": card_type,
        "fill_container": True,
        "tap_action":{
          "action": "more-info"
        },
        "icon": "mdi:brightness-4" if card_icon is None else card_icon,
        "secondary_info": state if secondary_info is None else secondary_info,
        "name": card_name,
        "icon": card_icon,
        "entity": entity
      }
    return card



  def getCardMod(self, style='background_color_select', card_type=None, color=None, support_dark_mode=True):
    css_variable = ""

    if style == 'background_color_select':
      css_variable += ":host { --ha-card-background:" + self.getColor(color) + ";}\n" 

    elif style == 'ios16_toggle':
      entity_is_on_condition = " (states(config.entity) in ['on']) " + \
                                  ("and (states('sun.sun') != 'below_horizon')" if support_dark_mode == True else '')

      # Make card background white if on, dark if off
      css_variable += (":host {\n"
      "--ha-card-background:    {% if" + entity_is_on_condition + "%} " + self.getColor("less_transparent_white") + "  {% else  %} " + self.getColor("more_transparent_grey") + "  {% endif %};\n" 
      "--primary-text-color:    {% if" + entity_is_on_condition + "%} black                                            {% else  %} white                                           {% endif %};\n" 
      "--secondary-text-color : {% if" + entity_is_on_condition + "%} " + self.getColor("dark_grey") +                "{% else  %} " + self.getColor("light_grey") +             " {% endif %};\n"
      ";}\n")
      
      # Make icon a bit larger, similar to ios 16
      css_variable += ("ha-card > mushroom-card > mushroom-state-item > mushroom-shape-icon > ha-state-icon {\n"
      "--mdc-icon-size: 0.7em;"
      ";}\n")

      # Make icon inner white if on, outter dark if off
      if card_type == 'custom:mushroom-light-card':
          css_variable +=  "ha-card > mushroom-card > mushroom-state-item > mushroom-shape-icon {"       + " \n" + \
            "--icon-color-disabled:   " + self.getColor(color)                                           + ";\n" + \
            "--shape-color-disabled:  " + self.getColor("more_transparent_grey")                         + ";\n" + \
            "--icon-color:            " + self.getColor("white")                                         + ";\n" + \
            "--shape-color:            {% if state_attr(config.entity, 'color_mode') == 'color_temp' %}" + " \n" + \
                                          self.getColor(color)                                           + " \n" + \
                                      "{% else  %}"                                                      + " \n" + \
                                      "   rgb{{state_attr(config.entity, 'rgb_color')}}"                 + " \n" + \
                                      "{% endif%}"                                                       + ";\n" + \
            "}\n"

      else:
        css_variable += ( "ha-card > mushroom-card > mushroom-state-item > mushroom-shape-icon {\n"
          "--icon-color-disabled:  " + self.getColor(color)            + ";\n"
          "--shape-color-disabled: " + self.getColor("more_transparent_grey") + ";\n"
          "--icon-color:           " + self.getColor("white")                 + ";\n"
          "--shape-color:          " + self.getColor(color)            + ";\n"
          "}\n")

      # Make brightness slider color same as the light color if it is in RGB, otherwise use ios_yellow
      if card_type == 'custom:mushroom-light-card':
          css_variable +=  "ha-card > mushroom-card > div > mushroom-light-brightness-control {"         + " \n" + \
            "--slider-color:           {% if state_attr(config.entity, 'color_mode') == 'color_temp' %}" + " \n" + \
                                          self.getColor(color)                                           + " \n" + \
                                      "{% else  %}"                                                      + " \n" + \
                                      "   rgb{{state_attr(config.entity, 'rgb_color')}}"                 + " \n" + \
                                      "{% endif%}"                                                       + ";\n" + \
            "--slider-bg-color:        {% if state_attr(config.entity, 'color_mode') == 'color_temp' %}" + " \n" + \
                                          "{{ '" + self.getColor(color) + "' | regex_replace(',([\d\.])+\)$', ',0.2)') }}" + " \n" + \
                                      "{% else  %}"                                                      + " \n" + \
                                      "   rgba{{(state_attr(config.entity, 'rgb_color')|string)[0:-1]}}, 0.2)"  + " \n" + \
                                      "{% endif%}"                                                       + ";\n" + \
            "}\n"

      # Make bottom buttons background more visiable in white card
      # and default in dark card
      if card_type == 'custom:mushroom-light-card':
        for index in [2,3]:
          css_variable += "" + \
            "ha-card > mushroom-card > div > mushroom-button:nth-child(" + str(index) + ") {"
          css_variable += "" + \
            "  --bg-color: {% if " + entity_is_on_condition + " %} " + self.getColor("less_transparent_white") + " {% else %} rgba(var(--rgb-primary-text-color), 0.05)" +  " {% endif %};" + \
            "}\n"
        
    else: 
      raise TypeError( "\n" +\
          "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
          "getCardMod does not support style = " + style + \
          "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

    return {
      "card_mod": {
        "style":  css_variable 
      }    
    }

  def getColor(self, color):
    # The last digit of rgba represents opacity and the value of it is between 0.0 and 1.0 
    # !! always needs to follow the rgba format to maintain a compatibility 
    if color == 'transparent':
      return "rgba(245, 245, 245, 0)"
    elif color == 'more_transparent_grey':
      return "rgba(10, 10, 10, 0.4)"
    elif color == 'less_transparent_grey':
      return "rgba(10, 10, 10, 0.7)"
    elif color == 'most_transparent_white':
      return "rgba(245, 245, 245, 0.1)"
    elif color == 'more_transparent_white':
      return "rgba(245, 245, 245, 0.3)"
    elif color == 'less_transparent_white':
      return "rgba(245, 245, 245, 0.9)"
    elif color == 'dark_grey':
      return "rgba(100, 100, 100, 1)"
    elif color == 'light_grey':
      return "rgba(220, 220, 220, 1)"
    elif color == 'ios_yellow':
      return "rgba(253,204,0,1)"
    else: 
      return color

  def getCardModColor(self, color):
    return self.getCardMod('background_color_select', color=color)

#  def addEntityCard(self, entity, entity_name=None, entity_name_translation=None, 
#                          card_name=None, card_type=None,card_icon=None,card_icon_color=None,double_tab_action=None, card_group=None):
#
#
#    self.room_cards += [self.getEntityCard(entity=entity,
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

        # Rename switches based on switch rename
        if switch_rename_dir is not None and i in switch_rename_dir:
          #print (switch_rename_dir[i])
          self.switch_list += [
            {
              "platform": "group",
              "name": switch_rename_dir[i],
              "entities": raw_switch_entity,
              "configured": True 
            }        
          ]
        
        # added wall switches
        if light_wall_switch == True:
          self.wall_switches += [raw_switch_entity]
        
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
    # Aqara Wireless Switch,   WXKG11LM  ZigbeeID: ["lumi.sensor_switch.aq2"]
    # MiJia Wireless Switch,   WXKG01LM  ZigbeeID: ["lumi.sensor_switch"]
    # MiJia Wireless Switch 2, ble XMWXKG01LM
    ###################################################################################################
    elif((model == "Aqara Wireless Switch") or \
         (model == "MiJia Wireless Switch") or \
         (model == "MiJia Wireless Switch 2")): 

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
    # Xiaomi Light Detection Sensor GZCGQ01LM ZigbeeID: ["lumi.sen_ill.mgl01"]
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
              "state": '{% if (states.sensor["' + mac + '"].state) | float | round(1) > ' + str(power_on_threshold) + ' %} on {% else %} off {% endif %}'
            }
          ],
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
        self.getPostfix(self.curtain_control_when['Lights off']) : {
          "name" :  self.getName(self.curtain_control_when['Lights off']),
          #"initial": "off",
          "configured": True
        } | ({"initial": "off"} if len(self.curtains) == 0 else {}),
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
          self.getPostfix(self.occupancy_group) : {
            "name": self.getName(self.occupancy_group), 
            "entities": [self.room_occupancy, self.motion_group] + self.all_motion_sensors 
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

      # Add dashboard cards
      # Entertainment
      if self.tvs is not None and self.tvs != []:
        self.main_card_list.append(self.getEntityCard(entity=self.tvs[0],     card_name='TV'))

      # Light and curtains
      for light in self.lights:
        self.main_card_list.append(self.getEntityCard(entity=light))

      for curtain in self.curtains:
        self.main_card_list.append(self.getEntityCard(entity=curtain))
      
      # Climate Control
      if self.thermostat is not None:      
        self.main_card_list.append(self.getEntityCard(entity=self.thermostat, card_name='Raditor'))

      if self.cfg_temp_control:
        self.main_card_list.append(self.getEntityCard(entity=self.room_heating_override, card_name='Heating Override'))

      if self.temperature_sensor is not None:
        self.main_card_list.append(self.getEntityCard(entity=self.temperature_sensor, card_name='Temperature'))

      if self.cfg_temp_control:
        self.tail_card_list.append(self.getEntityCard(entity=[self.thermostat], entity_name='', card_name='Schedule', card_type='custom:scheduler-card'))

      # Motion 
      if self.cfg_occupancy:
        self.tail_card_list.append(self.getEntityCard(entity=self.occupancy_group, card_name='Occupancy'))

      # Room Automation Control
      if self.cfg_group_auto:      
        self.tail_card_list.append(self.getEntityCard(entity=self.room_auto_gen_automations, card_name='Automation Control'))
      


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
      ([self.curtain_control_when['Lights off']                         ] if len(self.curtains) > 0       and len(self.curtains) > 0 else []) + \
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
        self.getPostfix(self.room_auto_gen_automations) : {
          "name": self.getName(self.room_auto_gen_automations), 
          "entities": self.automation_entity_list 
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
            "entity_id": self.motion_group,
            "state": "off",
            "for": "00:01:00"
          }],
        "action": { 
          'parallel': [
            # Re-enable lights on automation
            self.turn(self.automation_lights_on['id'], 'on'),
            # Turn off lights/curtains/tv
            {"if": self.continueIf(self.curtain_control_when["Lights off"], "on"), "then": self.turn(self.curtains, "on"), "else": self.turn(self.curtains, "off")},
            self.turn(self.tvs, 'off'),
            self.callSceneService("All Off")          
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


  def gen_tv_automations(self):
    self.automations += [
      { 
        "alias" : "ZTV-" + self.automation_room_name + "Reset Picture Mode When Turning on TV" + "-" + self.room_name,
        "configured": self.cfg_tv,
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
            "notify_ke": "yes"
          }
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
          }
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

    if self.cfg_scene_color_led or self.cfg_scene_color_lamp:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Hue")]          
    if self.cfg_led_only_scene:
      cond_seq += [self.setNewSceneFromOldScene(nxt_scene="LED White")]
    if self.cfg_custom_scene:
      cond_seq+= [self.setNewSceneFromOldScene(nxt_scene="Sleep Mode")]
    if self.cfg_custom_scene:
      #cond_seq += [self.setNewSceneFromOldScene(nxt_scene="Night Mode")] 
      cond_seq+= [self.setNewSceneFromOldScene(nxt_scene="Dark Night Mode")]
      
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
        ] + [
          self.turn(gateway_power_switch, "off"),
          {"delay": "00:00:02"},
          self.turn(gateway_power_switch, "on")
        ] if gateway_power_switch != 'N/A' else []
    }]  
  
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
              self.callSceneServiceIfSelected("Sleep Mode"),
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

  def gen_occupancy_automations(self):
    
    #print ("[OC] " + self.room_name + " occupancy_on_x_min_ratio_sensor is " + self.occupancy_on_x_min_ratio_sensor)
    
    self.automations += [
      {
        "alias":"ZOc-" + self.automation_room_name + "Occupancy Update" + "-" + self.room_name,
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
                    "motion_str":                     self.motion_group,                                 
                    "motion_on_ratio_for_x_min_str":  self.occupancy_on_x_min_ratio_sensor,
                    "motion_on_ratio_for_2x_min_str": self.occupancy_on_2x_min_ratio_sensor,
                    "room_type":                      self.room_type 
                    },
          }
        ]
      }
    ]

  # Generate automation ID/entity_name based on alias name
  def getIDFromName(self, name):
    id = name.lower()
    id = re.sub("-", "_", id)
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
  def turn(self, entity_list, state=None, light_brightness=None, tv_brightness=None, inc_unavail=True):
    assert state in ['on', 'off', 'toggle', None], "State has to be one of 'on', 'off', 'toggle', 'None', but it is " + state

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
      
      # Shutter blind
      if self.aqara_shutter_blind == True and state in ['on', 'off']:
        if state == 'on': 
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
          pass
      
      # Normal blind or curtains
      else:
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


    if entity_list != None and entity_list != []:
      return self.convertToSingleService(action_service, 
                                         alias =  ('Turn'  + \
                                                   (' nothing'        if entity_list==[]              else \
                                                    ' ' + entity_list if isinstance(entity_list, str) else " " + " ".join(entity_list)) + \
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
                            self.turn(self.leds, "off")]
      elif scene_name in ['Lights on in hot sunshine',
                          'Lights on when bright outdoor',
                          'Lights on when dark outdoor']:
        
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
                  "above": "15" if self.west_face_windows else "18"
                },
                # In the period that there might be a direct sunshine
                {
                  "condition": "time",
                  "after":  "13:00:00"           if self.west_face_windows else self.daytime_start,
                  "before": self.daytime_end     if self.west_face_windows else "16:00:00"
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
    self.dashboard_default_root = 'Uninitliazed_dashboard_root'
    self.dashboard_view_name = 'Uninitliazed_dashboard_view_name'
    self.room_icon           = 'Uninitliazed_room_icon'
    self.room_theme          = 'Mushroom Shadow'

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

  def getTemplateCard(self, icon='mdi:head-alert-outline', 
                            icon_color='blue', 
                            primary=None, 
                            secondary=None, 
                            condition_entity=None, 
                            tap_entity=None, 
                            condition_state='on', 
                            condition_state_not=None, 
                            condition_states=None,
                            tap_action='more-info'):
    
    self.dashboard_view_path = "/" + self.dashboard_root + "/" + self.room_entity
    
    tap_action_dict = {}
    entity =  tap_entity                  if tap_entity       != None else \
              condition_entity            if condition_entity != None else \
              'input_boolean.placeholder'
             
    if   tap_action == 'navigate':
      tap_action_dict = {
        "action": "navigate",
        "navigation_path": self.dashboard_view_path} 
    elif tap_action == 'more-info':
      tap_action_dict = {"action": "more-info"}
    
    template_card = {
      "type":       "custom:mushroom-template-card",
      "icon":       "{% set entity = '"+entity+"' %}\n" + icon,
      "icon_color": "{% set entity = '"+entity+"' %}\n" + icon_color,
      "tap_action": tap_action_dict,
      "entity":     entity,
      "layout":     "horizontal",
      "fill_container": True,
    } | ({"primary"  : primary  } if primary   !=None else {}) \
      | ({"secondary": secondary} if secondary !=None else {}) 

    if condition_entity == None:
      return template_card
    else:
      condition_card = {}

      # Use single condition
      if condition_states is None:
        condition_card = {
          "type": "conditional",
          "conditions": [
            ( {"entity":    condition_entity}) | ( 
              {"state_not": condition_state_not} if condition_state_not != None else \
              {"state":     condition_state}    )
          ],
          "card": template_card }
          
      else: # Use multiple conditions 
        condition_card = {
          "type": "custom:state-switch",
          "entity": condition_entity,
          states: {}}
        for state in condition_states:
          condition_card['states'] |= { state : template_card}

      return condition_card


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
    
    self.addView(title=self.room_name, theme=self.room_theme, viewPath=self.room_entity, cards=all_cards)
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
        self.getEntityCard(entity=self.room_scene_ctl, secondary_info='none')
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
    self.cfg_scene_color_led   = True
    self.cfg_scene_color_lamp  = True
    self.cfg_custom_scene       = True
    self.cfg_motion_bed_led     = True
    self.cfg_auto_curtain_ctl   = True
    self.cfg_tv                 = True

  def get_entity_declarations(self):
    super().get_entity_declarations()    
    self.add_mac_device('0x54ef441000792d09',       self.room_name + ' Bed',                 'Pressure Sensor',    'Aqara Pressure Sensor')    
    self.add_mac_device("0x04cf8cdf3c7ad638",       self.room_name,                          'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Triple Rocker)", flex_switch=[2,3])
    self.add_mac_device("582d343b6a27",             self.room_name,                          'Temperature Sesnor', "Mijia2 Temperature Sensor", postfix='new_1')
    self.add_mac_device("a4c138ecdbba",             self.room_name,                          'Temperature Sesnor', "Mijia2 Temperature Sensor", postfix='new_2')
    self.add_mac_device("dced830908fb",             self.room_name,                          'Motion Sensor',      "Ziqing Occupancy Sensor")
    self.add_mac_device("dced8309090d",             self.room_name + " Drawer",              'Motion Sensor',      "Ziqing Occupancy Sensor")
    self.add_mac_device("0x00158d0005228ba8",       self.room_name + " TV",                  'Motion Sensor',      "Aqara Motion and Illuminance Sensor")
    self.add_mac_device('50ec50df3056',             self.room_name + " Ceiling Light Bulb 1",'Light',              'Mijia BLE Lights')
    self.add_mac_device("0x04cf8cdf3c73a19b",       self.room_name + " Curtain",             'Curtain',            "Aqara B1 curtain motor")
    self.add_mac_device('1001e49ec4_1',             self.room_name + ' Dressing Table Light','Switch',             'Generic Switches')
    self.add_mac_device('18c23c24681a',             self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='1')
    self.add_mac_device('18c23c25960b',             self.room_name,                          'Button',             'MiJia Wireless Switch 2', postfix='2')
    self.add_mac_device('e4aaec755efa',             self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='1')    
    self.add_mac_device('e4aaec755f4b',             self.room_name + ' Bed',                 'Pressure Sensor 4',  'Mijia2 Pressure Sensor',  postfix='2')    
    self.add_mac_device("1001e4a0a0_1",             self.room_name + ' Gateway Power',       'Switch',             "Generic Switches")


    # New unused button
    #self.add_mac_device('18c23c25a26c',              self.room_name,                           'Button',             'MiJia Wireless Switch 2', postfix='3')

    #self.add_mac_device('50ec50df0a79',       'Master Room Ceiling Light Bulb 2',  'Light',              'Mijia BLE Lights')

    #self.add_mac_device("54ef44e58958",             self.room_name + " Bed",                 'Motion Sensor',      "Mijia2 Motion Sensor")
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
      #"binary_sensor.master_room_bed_motion_sensor_motion",
      "binary_sensor.master_room_bed_pressure_sensor",
      "binary_sensor.master_room_occupancy_sensor_occupancy",
      "binary_sensor.master_room_drawer_occupancy_sensor_occupancy",
      "binary_sensor.master_room_bed_pressure_sensor_1",
      "binary_sensor.master_room_bed_pressure_sensor_2"
    ]
    
    self.all_motion_sensors = self.non_bed_motion_sensors + self.bed_motion_sensors
    
  def get_light_entities(self):
    super().get_light_entities()
    # Light/Switch entities
    self.leds                    = ["light.master_room_drawer_led",
                                    "light.master_room_tv_led",
                                    "light.master_room_bed_led"] 
    
    self.other_lights            = ["switch.master_room_entrance_wall_switch",
                                    "switch.master_room_dressing_table_light"]
    
    self.ceiling_lights          = ["light.master_room_ceiling_light_bulb_1",
                                    "light.master_room_drawer_ceiling_light_yeelight"]
                                    
    self.lights                  = self.leds + self.lamps + self.ceiling_lights + self.other_lights
    
  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains               = [ "cover.master_room_blind",
                                    "cover.master_room_curtain"] 

  def get_remote_entities(self):  
    super().get_remote_entities()
    self.wall_buttons            = ["sensor." + self.room_entity + "_entrance_wall_button"]
    self.buttons                 = self.wall_buttons + self.xiaomi_buttons

  def gen_room_specific_automations(self):
    self.add_offline_device_automations(
      device_type          = 'Zigbee',
      offline_device       = 'switch.master_toilet_wall_switch',
      gateway_power_switch = 'switch.master_room_gateway_power',
      tts_message          = self.automation_room_name + "gateway zigbee devices are offline - Restarting gateway -"
      )

    self.add_offline_device_automations(
      device_type          = 'Wifi',
      offline_device       = 'cover.master_room_blind_1',
      tts_message          = self.automation_room_name + "wifi devices are offline. You may want to manual restart 2.4Ghz Wifi."
      )

  def gen_window_automations(self):
    if len(self.windows) > 0:
      self.add_window_open_notification_when_leaving_zone_automations()

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_default_root = 'master-room'
    self.dashboard_view_name    = 'master-room'
    self.room_icon              = 'mdi:bed-king-outline'
    self.room_theme             = 'ios-dark-mode-dark-green'


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

  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device('0x00158d00047d69be',      self.room_name,                            'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)')
    self.add_mac_device("a4c1381d6ddb",            self.room_name,                            'Temperature Sensor', "Mijia2 Temperature Sensor")
    self.add_mac_device('e4aaec80bc19',            self.room_name + ' Door',                  'Door Sensor',        'Mijia2 Contact')
    self.add_mac_device('0x00158d00057b2b4c',      self.room_name + ' Basin',                 'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('0x00158d000460247b',      self.room_name + ' Dressing Room',         'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('0x00158d00054750ca',      self.room_name + ' Shower',                'Motion Sensor',      'Aqara Motion and Illuminance Sensor', integration='Z2M')
    self.add_mac_device('mss210_cebd_outlet',      self.room_name + ' Floor LED',             'Switch',             'Generic Switches')
    #self.add_mac_device('0x00158d000171756e',      self.room_name + ' Floor LED',             'Switch',             'Mi Power Plug ZigBee')
    # Dressing Room
    self.add_mac_device("0x00158d00042d4092",      self.room_name + " Dressing Room",         'Wall Switch',        "Aqara D1 Wall Switch (With Neutral, Single Rocker)", flex_switch=True)
    self.add_mac_device("28d1272057d5",            self.room_name + " Dressing Room Light",   'Light',              "Mijia BLE Lights")
    self.add_mac_device("0x00158d00070b2f2a",      self.room_name + " Dressing Room Blind",   'Blind',              "Aqara roller shade motor")

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
    self.cfg_tv                 = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.kitchen_occupancy_sensor_occupancy",
      "binary_sensor.kitchen_worktop_motion_sensor_motion",
      "binary_sensor.kitchen_dining_motion_sensor_motion"
    ]


  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("a4c1380e91a7",                               self.room_name,                   'Temperature Sensor', "Mijia2 Temperature Sensor")     
    self.add_mac_device("curtain_1e9e",                               self.room_name + " Curtain",      'Curtain',            "Generic Curtains")     
    self.add_mac_device('0x04cf8cdf3c7ad647',                         self.room_name,                   'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Triple Rocker)', flex_switch=[2], switch_rename_dir={3: 'Kitchen Floor LED'})
    self.add_mac_device("dced8308f596",                               self.room_name,                   'Motion Sensor',      "Ziqing Occupancy Sensor")
    self.add_mac_device('mss210_c944_outlet',                         self.room_name + ' Plate Warmer', 'Switch',             'Generic Switches')
    self.add_mac_device('52b1_measure_mss310_power_w_main_channel',   'Washing Machine Power',          'Power',              'Generic Power Measurement Switch', power_on_threshold=4)
    self.add_mac_device('560a_measure_mss310_power_w_main_channel',   'Rice Cooker Power',              'Power',              'Generic Power Measurement Switch', power_on_threshold=4)
    self.add_mac_device('0x00158d00057acaac',                         self.room_name + ' Dining',       'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x00158d0004660308',                         self.room_name + ' Worktop',      'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x00158d0005210fa9',                         self.room_name + ' Extractor',    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Double Rocker)', switch_rename_dir={2: 'Kitchen Extractor'}, light_wall_switch=False)
    self.add_mac_device("e4aaec4500e4",                               self.room_name + " Window",       'Window',             "Mijia2 Contact") # belong_to_group=self.windows)


    # MCCGQ02HL
    #self.add_mac_device("0x158d00023e6015",       self.room_name + " Worktop",             "Aqara Wireless Switch")     
  
  def get_remote_entities(self):  
    super().get_remote_entities()    
    self.wall_buttons            = ["sensor." + self.room_entity + "_wall_button_2"]

  def get_window_entities(self):
    super().get_window_entities()
    self.windows                 = ["binary_sensor.kitchen_window"]

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
    self.gen_a_button_toggle_automation(      button_state_list=["single_left", "button_1_single"],
                                              button_state_name='Single Left',
                                              device_list='light.kitchen_ceiling_light',
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
    self.cfg_scene_color_lamp  = True
    self.cfg_temp_control       = True
    self.cfg_temp_calibration   = True
    self.cfg_tv                 = True

  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.living_room_sofa_motion_sensor_motion",
      "binary_sensor.living_room_entrance_motion_sensor_motion",
      "binary_sensor.tais_desk_motion_sensor_motion",
      "binary_sensor.living_room_sofa_pressure_sensor",
      "binary_sensor.living_room_occupancy_sensor_occupancy"
    ]

  def get_room_name_and_property(self):  
    super().get_room_name_and_property()
    self.room_type              = 'bedroom' # as we often fall into sleep in living room

  def get_entity_declarations(self):
    super().get_entity_declarations()

    self.add_average_temperature_sensor(sensor_1='sensor.living_room_temperature_sensor_1', 
                                        sensor_2='sensor.living_room_temperature_sensor_2', 
                                        name='Living Room Temperature Sensor')

#    self.add_mac_device("living_room_ceiling_light_yeelight", self.room_name + ' Ceiling Light', 'Light',              "Yeelight Ceiling Light")




    self.add_mac_device("dced8308e951",                       self.room_name,                    'Motion Sensor',      "Ziqing Occupancy Sensor")
    self.add_mac_device("2ab7",                               self.room_name,                    'Temperature Sensor', "Mijia2 Temperature Clock",  postfix='1', integration='Passive BLE Monitor')
    self.add_mac_device("a4c13864aca3",                       self.room_name,                    'Temperature Sensor', "Mijia2 Temperature Sensor", postfix='2')
    self.add_mac_device('0x00158d0008d8ead8',                 self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', flex_switch=True)
    self.add_mac_device("0x54ef441000452fd8",                 self.room_name + ' Curtain',       'Curtain',            "Aqara B1 curtain motor",    postfix='1')
    self.add_mac_device("0x54ef4410001f409c",                 self.room_name + ' Curtain',       'Curtain',            "Aqara B1 curtain motor",    postfix='2')
    self.add_mac_device('0x04cf8cdf3c7b560f',                 self.room_name,                    'Light Sensor',       'Xiaomi Light Detection Sensor')
    self.add_mac_device('0x54ef441000792d1d',                 self.room_name + ' Sofa',          'Pressure Sensor 1',  'Aqara Pressure Sensor')    
    self.add_mac_device('0x00158d0003140ea8',                 self.room_name + ' Entrance',      'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    #self.add_mac_device('mss210_ef0f_outlet',                self.room_name + ' Floor Light 3', 'Switch',             'Generic Switches')
    self.add_mac_device('ef0f_29831979_mss210_main_channel',  self.room_name + ' Floor Light 3', 'Switch',             'Generic Switches')
    self.add_mac_device('0x00158d000424f995',                 self.room_name,                    'Button',             'MiJia Wireless Switch')
    self.add_mac_device("1001e49906_1",                       self.room_name + ' Gateway Power', 'Switch',             "Generic Switches")
    self.add_mac_device("e4aaec80beca",                       self.room_name + " Window",        'Window',             "Mijia2 Contact") 
    self.add_mac_device("e4aaec80bedb",                       self.room_name + " Sliding Door",  'Door',               "Mijia2 Contact") 


    self.add_mac_device('0x00158d000451f90b',                 'Tais Desk',                       'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    #self.add_mac_device('mss210_b3bd_outlet',                'Tais Desk Screen LED',            'Switch',             'Generic Switches')
    self.add_mac_device('1001e49dd9_1',                       'Tais Desk Screen LED',            'Switch',             'Generic Switches')
    self.add_mac_device('0x00158d00054d83df',                 'Boiler Room',                     'Motion Sensor',      'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('28d127202ef6',                       'Boiler Room Light',               'Motion Sensor',      'Mijia BLE Lights')



#('0x00158d0004501b0a', 'Living Room Sofa',           'Aqara Motion and Illuminance Sensor')
#('0x00158d0001212747', 'Boiler Room',                'Aqara Door & Window Sensor')

  def get_window_entities(self):
    super().get_window_entities()
    self.windows                 = ["binary_sensor.living_room_sliding_door",
                                    "binary_sensor.living_room_window"]


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

  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains               = [ "cover.living_room_curtain_1",
                                    "cover.living_room_curtain_2"] 

  def gen_room_specific_automations(self):
    self.add_offline_device_automations(
      device_type          = 'Zigbee',
      offline_device       = 'switch.living_room_wall_switch',
      gateway_power_switch = 'switch.living_room_gateway_power',
      tts_message          = self.automation_room_name + "gateway zigbee devices are offline. Restarting gateway."
      )

    self.add_offline_device_automations(
      device_type          = 'Wifi',
      offline_device       = 'light.kitchen_worktop_led',
      tts_message          = self.automation_room_name + "wifi devices are offline. You may want to manual restart 2.4Ghz Wifi."
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
    self.add_mac_device('54ef44e34c16',           self.room_name + ' Bike Shed',      'Motion Sensor', 'Mijia2 Motion Sensor')
    self.add_mac_device('0x00158d000548b8a5',     self.room_name + ' Sliding Door',   'Motion Sensor', 'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x00158d000522e00e',     self.room_name,                     'Wall Switch',   'Aqara D1 Wall Switch (With Neutral, Double Rocker)', switch_rename_dir={2: 'Garden Ceiling Light'})
    self.add_mac_device('mss425e_5df5_outlet_1',  self.room_name + ' Spotlight 1',    'Switch',        'Generic Switches')
    #self.add_mac_device('mss425e_5df5_outlet_2',  self.room_name + ' Spotlight 2',    'Switch',        'Generic Switches')
    #self.add_mac_device('mss425e_5df5_outlet_3',  self.room_name + ' Spotlight 3',    'Switch',        'Generic Switches')

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
    self.dashboard_default_root = 'en-suite-room'
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
    self.add_mac_device("0x158d00053fdaba",   self.room_name + ' Door',  'Door',          "Aqara Door & Window Sensor")
    self.add_mac_device('0x158d000572839f',   self.room_name,            'Motion Sensor', 'Aqara Motion and Illuminance Sensor')
    self.add_mac_device('0x158d000522d90c',   self.room_name,            'Wall Switch',   'Aqara D1 Wall Switch (With Neutral, Single Rocker)')

    
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
    self.num_of_xiaomi_button   = 0
    self.num_of_lamps           = 1
    self.cfg_occupancy          = True       
    self.cfg_group_auto         = True
    self.cfg_temp_control       = True
    self.cfg_temp_calibration   = True
    self.cfg_scene              = True            
    self.cfg_motion_light       = True
    self.cfg_remote_light       = True

  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device("582d343483e9",       self.room_name,                    'Temperature Sensor', "Qingping Temperature Sensor")
    self.add_mac_device("50ec50dd67be",       self.room_name + " Lamp",          'Light',              "Generic Lights")
    self.add_mac_device("28d12735ea1e",       self.room_name + " Ceiling Light", 'Light',              "Generic Lights")
    self.add_mac_device('0x00158d00047b69d2', self.room_name,                    'Wall Switch',        'Aqara D1 Wall Switch (With Neutral, Single Rocker)', flex_switch=True)
    self.add_mac_device("curtain_1050",       self.room_name + " Curtain",       'Curtain',            "Generic Curtains")     


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

  def get_light_entities(self):
    super().get_light_entities()
    self.leds                   =  ["switch.study_screen_led"] 
    self.lamps                   = ["switch.study_studio_lamp"] 
    self.lights                  = self.leds + self.lamps + self.ceiling_lights


  def get_motion_sensor_entities(self):
    super().get_motion_sensor_entities()
    self.all_motion_sensors = [
      "binary_sensor.study_motion_sensor_motion",
      "binary_sensor.kes_desk_motion_sensor_motion"
    ]

  def get_cover_entities(self):
    super().get_cover_entities()
    # Cover entities
    self.curtains               = [ "cover.study_blind"] 

  def getDashboardSettings(self):
    super().getDashboardSettings()
    self.dashboard_default_root = 'lovelace-misc'
    self.dashboard_view_name = 'study'
    self.room_icon           = 'mdi:desk'


  def get_entity_declarations(self):
    super().get_entity_declarations()
    self.add_mac_device('0x00158d00045245be', self.room_name,                     'Wall Switch', 'Aqara D1 Wall Switch (With Neutral, Single Rocker)', integration='Z2M', flex_switch=True)
    self.add_mac_device("0x00158d00070b2f26", self.room_name + ' Blind',          'Curtain',     "Aqara roller shade motor")
    self.add_mac_device("0x00158d00070b2f26", self.room_name + ' Blind',          'Curtain',     "Aqara roller shade motor")
    self.add_mac_device("mss210_b083_outlet", self.room_name + ' Studio Lamp 1',   'Switch',      "Generic Switches")
    self.add_mac_device("mss210_ce70_outlet", self.room_name + ' Studio Lamp 2',   'Switch',      "Generic Switches")
    self.add_mac_device("1001e49ade_1",       self.room_name + ' Gateway Power',   'Switch',      "Generic Switches")

#('0x00158d00054a6eb9', 'Study',                      'Aqara Motion and Illuminance Sensor')
    #self.add_mac_device("mss210_c519_outlet", self.room_name + ' Screen LED',      'Switch',      "Generic Switches")


  def gen_room_specific_automations(self):
    self.add_offline_device_automations(
      device_type          = 'Zigbee',
      offline_device       = 'switch.guest_room_wall_switch',
      gateway_power_switch = 'switch.study_gateway_power',
      tts_message          = self.automation_room_name + "gateway zigbee devices are offline. Restarting gateway."
      )

    self.add_offline_device_automations(
      device_type          = 'Wifi',
      offline_device       = 'light.master_room_drawer_led',
      tts_message          = self.automation_room_name + "wifi devices are offline. You may want to manual restart 2.4Ghz Wifi."
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
    self.add_mac_device('0x00158d00053fdaa8',  self.room_name + ' Door',                        'Door',               'Aqara Door & Window Sensor')
    self.add_mac_device("0x90fd9ffffe8e24b6",  self.room_name + " Ceiling Light Spotlight 1",   'Light',              "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum", integration='Z2M')
    self.add_mac_device("0x000b57fffee8e6b4",  self.room_name + " Ceiling Light Spotlight 2",   'Light',              "TRADFRI LED Bulb GU10 400 Lumen, Dimmable, White spectrum", integration='Z2M')



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
              "navigation_path": "/lovelace-system/system\\"
            }
          },
          self.getCardModColor("transparent") | {
            "type": "custom:stack-in-card",
            "mode": "horizontal",
            "cards": [
              self.getTemplateCard(
                icon       = "mdi:desktop-classic",
                icon_color = "{% set entity = 'switch.gaming_pc' %} {% if   is_state(entity, 'on') %} amber {% endif %}",
                tap_entity = 'switch.gaming_pc',
                tap_action = 'more-info'
              ),
              self.getTemplateCard(
                icon       = "mdi:television-box",
                icon_color = "{% set entity = 'binary_sensor.fire_tv_streaming_pc_contents' %} {% if   is_state(entity, 'on') %} deep-orange {% endif %}",
                tap_entity = 'binary_sensor.fire_tv_streaming_pc_contents',                
                tap_action = 'more-info'
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


class Dashboard(RoomBase):
  def __init__ (self, format=None, dashboard_type=None):
    print ("-------------------------------------")
    print ("** Generating Overall Lovelace Configs. **")
    self.format         = 'yaml'   if format         == None else format
    self.dashboard_type = 'mobile' if dashboard_type == None else dashboard_type
    self.room_nav_cards = []
    self.dashboard = {}
    self.views = []
    self.rooms = [ 
              LivingRoom(      dashboard_type=dashboard_type),
              Kitchen(         dashboard_type=dashboard_type),
              MasterRoom(      dashboard_type=dashboard_type),
              MasterToilet(    dashboard_type=dashboard_type),
              Study(           dashboard_type=dashboard_type),
              System(          dashboard_type=dashboard_type),
              GroundToilet(    dashboard_type=dashboard_type),
              Corridor(        dashboard_type=dashboard_type),
              Garden(          dashboard_type=dashboard_type),
              EnSuiteRoom(     dashboard_type=dashboard_type),
              EnSuiteToilet(   dashboard_type=dashboard_type),
              GuestRoom(       dashboard_type=dashboard_type),
              GuestToilet(     dashboard_type=dashboard_type)]
    self.addNavigationView()
    self.addAllRoomView()
    self.getDashbaord()
    self.writeConfig()
    print ("-------------------------------------")

  def addNavigationView(self):
    for room in self.rooms:
      self.room_nav_cards += [room.getNavigationRoomCard()]

    room_nav_grid_cards = self.getLayoutWrapperCardList(self.room_nav_cards)

    self.addView(viewPath='home', cards=room_nav_grid_cards)

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
    if self.format == 'json':
      self.auto_gen_config_path = self.script_dir + "/../.storage/lovelace.dashboard_mobile"
    else: # yaml
      self.auto_gen_config_path = self.script_dir + "/../lovelace/auto_gen_overall_dashboard.yaml"


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
           #EnSuiteToilet(),
           #EnSuiteRoom(),
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

if args.render_dashboard_yaml:
  dashboard = Dashboard(format='yaml', dashboard_type=dashboard_type)
elif args.render_dashboard_json:
  dashboard = Dashboard(format='json', dashboard_type=dashboard_type)


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

















