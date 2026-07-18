#!/usr/bin/env python3

#####################################################################
# This script won't update En-suite Room/Toilet configurations
# It is intentional to stop breaking automations in tenant room.
#####################################################################

from HA_Composite_Card_Lib.src.main import HA_Composite_Card_Lib
import automation_helpers
import battery_entity_builder
import button_automation_helpers
import camera_automation_helpers
import configured_entity_filter
import dashboard_card_mod
import dashboard_colors
import dashboard_entity_cards
import dashboard_generator
import dashboard_restrictions
import dashboard_settings
import dashboard_view_helpers
import entity_declaration_builders
import entity_interface_defaults
import entity_naming
import generator_cli
import generator_io
import gui_control_group
import ha_entity_registry
import media_automation_helpers
import message_helpers
import mirror_automation_helpers
import motion_light_automation_helpers
import offline_device_automation_helpers
import occupancy_automation_helpers
import occupancy_state_machine
import occupancy_ratio_sensor
import package_writer
import room_config_defaults
import room_device_defaults
import room_light_entities
import room_motion_entities
import room_properties
import room_registry
import room_remote_entities
import room_scene_defaults
import room_time_settings
import rooms
import sensor_declaration_builders
import service_action_helpers
import tv_automation_helpers
import unavailable_entity_builder
import window_automation_helpers
import re
import os
from copy import deepcopy


SCRIPT_DIR = generator_io.SCRIPT_DIR
OUTPUT_ROOT = generator_io.OUTPUT_ROOT
PACKAGES_DIR = generator_io.PACKAGES_DIR
AUTO_GENERATED_PACKAGES_DIR = generator_io.AUTO_GENERATED_PACKAGES_DIR
STORAGE_DIR = generator_io.STORAGE_DIR
DASHBOARD_OUTPUT_DIR = generator_io.DASHBOARD_OUTPUT_DIR


def configure_output_root(output_root=None):
  global OUTPUT_ROOT
  global PACKAGES_DIR
  global AUTO_GENERATED_PACKAGES_DIR
  global STORAGE_DIR
  global DASHBOARD_OUTPUT_DIR

  generator_io.configure_output_root(output_root)
  OUTPUT_ROOT = generator_io.OUTPUT_ROOT
  PACKAGES_DIR = generator_io.PACKAGES_DIR
  AUTO_GENERATED_PACKAGES_DIR = generator_io.AUTO_GENERATED_PACKAGES_DIR
  STORAGE_DIR = generator_io.STORAGE_DIR
  DASHBOARD_OUTPUT_DIR = generator_io.DASHBOARD_OUTPUT_DIR


def write_yaml_file(path, data, include_header=False):
  generator_io.write_yaml_file(path, data, include_header=include_header)


def write_json_file(path, data):
  generator_io.write_json_file(path, data)

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
    # Initialize entity interface variables
    self.initialize_entity_intf()

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
    self.get_mirror_entities()
    self.get_lighting_control_entities()
    self.get_tv_entities()
    self.get_time_setup()
    self.get_cover_entities()
    self.get_window_entities()
    self.get_temperature_control_entities()
    self.get_post_room_config()

    # Populate entities into database
    self.get_entity_declarations()
    self.get_unavailable_entity()
    self.get_battery_entity()
    self.get_automation_declarations()

    # Populate interface variables into a database for dump out
    self.implement_entity_intf()
    # Remove disabled entities
    self.remove_disabed_entities()
    # Generate user control group including automations and other controls.
    # This removes disabled entities in the group
    self.implement_group_intf_for_gui()

    # Get dashboard settings
    self.dashboard_type = dashboard_type
    #self.dashboard_language = dashboard_language
    #print (self.dashboard_language)
    self.getDashboardSettings()
    self.dashboard_root = dashboard_settings.dashboard_root_for_type(
      dashboard_type,
      self.dashboard_default_root,
    )
    # Render config
    self.writeConfig()

  def get_room_config(self):
    for key, value in room_config_defaults.default_room_config().items():
      setattr(self, key, value)

  def error(self, msg):
        message_helpers.raise_config_error(msg)

  def warn(self, str):
      message_helpers.warn_config(str)

  def info(self, str):
      message_helpers.print_info(str)

  def get_time_entities(self):
    settings = room_time_settings.default_sleep_time_entities()
    self.end_of_sleep_time = settings["end_of_sleep_time"]
    self.start_of_sleep_time = settings["start_of_sleep_time"]

  def get_room_name_and_property(self):
    properties = room_properties.derive_room_properties(self.room_name, self.room_short_name)
    self.room_entity = properties["room_entity"]
    self.room_navi_path = properties["room_navi_path"]
    self.automation_room_name = properties["automation_room_name"]
    self.room_type = properties["room_type"]
    self.west_face_windows = properties["west_face_windows"]

  def get_motion_sensor_entities(self):
    entities = room_motion_entities.default_motion_sensor_entities(
      self.room_entity,
      self.room_type,
      self.room_name,
      self.automation_room_name,
      self.getIDFromAlias,
    )
    self.motion_group = entities["motion_group"]
    self.occupancy_group = entities["occupancy_group"]
    self.bed_motion_sensors = entities["bed_motion_sensors"]
    self.non_bed_motion_sensors = entities["non_bed_motion_sensors"]
    self.all_motion_sensors = entities["all_motion_sensors"]
    self.entrance_motion_sensors = entities["entrance_motion_sensors"]
    self.room_occupancy = entities["room_occupancy"]
    self.sleep_time = entities["sleep_time"]
    self.entered_to_inside_timeout = entities["entered_to_inside_timeout"]
    self.inside_to_outside_timeout = entities["inside_to_outside_timeout"]
    self.sleep_to_outside_timeout = entities["sleep_to_outside_timeout"]
    self.inside_to_sleep_timeout = entities["inside_to_sleep_timeout"]
    self.automation_occupancy = entities["automation_occupancy"]
    self.occupancy_state_duration = entities["occupancy_state_duration"]
    self.occupancy_on_x_min_ratio_sensor = entities["occupancy_on_x_min_ratio_sensor"]
    self.occupancy_on_2x_min_ratio_sensor = entities["occupancy_on_2x_min_ratio_sensor"]
    self.set_to_outside_when_no_motion = entities["set_to_outside_when_no_motion"]
    self.occupancy_override_entity = entities["occupancy_override_entity"]
    self.occupancy_override_timer_entity = entities["occupancy_override_timer_entity"]
    self.occupancy_override_default_timeout = entities["occupancy_override_default_timeout"]

    self.gui_ctl_entity_list = [self.occupancy_override_entity,
                                self.occupancy_override_timer_entity]

  def get_remote_entities(self):
    entities = room_remote_entities.default_remote_entities(
      self.room_entity,
      self.num_of_xiaomi_button,
    )
    self.xiaomi_buttons = entities["xiaomi_buttons"]
    self.wall_buttons = entities["wall_buttons"]
    self.buttons = entities["buttons"]
    self.curtain_buttons = entities["curtain_buttons"]
    self.six_key_buttons = entities["six_key_buttons"]
    self.four_key_buttons = entities["four_key_buttons"]
    self.eight_key_knob_buttons = entities["eight_key_knob_buttons"]

  def get_wall_switches(self):
    switches = room_remote_entities.default_wall_switches()
    self.wall_switches = switches["wall_switches"]
    self.decouple_wall_switches = switches["decouple_wall_switches"]
    self.raw_wall_switches = switches["raw_wall_switches"]
    self.alias_wall_switches = switches["alias_wall_switches"]


  def get_light_entities(self):
    entities = room_light_entities.default_light_entities(
      self.room_entity,
      self.room_name,
      self.num_of_lamps,
      self.cfg_adaptive_lighting,
    )
    self.ceiling_lights = entities["ceiling_lights"]
    self.lamps = entities["lamps"]
    self.leds = entities["leds"]
    self.lights = entities["lights"]
    self.light_group = entities["light_group"]
    self.screen_leds = entities["screen_leds"]
    self.extractor = entities["extractor"]
    self.al_sleep_mode = entities["al_sleep_mode"]
    self.al_adapt_brightness = entities["al_adapt_brightness"]
    self.al_light_list += entities["al_light_list_additions"]


  def get_mirror_entities(self):
    entities = room_device_defaults.default_mirror_entities()
    self.mirror_sensors = entities["mirror_sensors"]
    self.demisters = entities["demisters"]
    self.shower_sensors = entities["shower_sensors"]

  def get_lighting_control_entities(self):
    entities = room_light_entities.default_lighting_control_entities(
      self.room_entity,
      self.west_face_windows,
    )
    self.ceiling_light_control_when = entities["ceiling_light_control_when"]
    self.lamp_control_when = entities["lamp_control_when"]
    self.led_control_when = entities["led_control_when"]
    self.curtain_control_when = entities["curtain_control_when"]
    self.light_intensity_threshold_when = entities["light_intensity_threshold_when"]
    self.light_intensity_entity = entities["light_intensity_entity"]
    self.noon_time = entities["noon_time"]
    self.time_controls = entities["time_controls"]
    self.light_sensor = entities["light_sensor"]
    self.min_value_as_bright = entities["min_value_as_bright"]
    self.light_sensor_controls = entities["light_sensor_controls"]
    self.gui_ctl_entity_list += entities["gui_ctl_entity_list_additions"]

  def getPrefix(self, entity):
    return entity_naming.get_prefix(entity)

  def getPostfix(self, entity):
    return entity_naming.get_postfix(entity)

  def getNameFromPostfix(self, postfix):
    return entity_naming.get_name_from_postfix(postfix)

  # match the beginning of the string or a space, followed by a non-space
  def captilizeSentence(self, s):
    return entity_naming.captilize_sentence(s)

  def getNameFromEntity(self, entity):
    return entity_naming.get_name_from_entity(entity)

  # Generate entity_name based on alias name
  def getEntityFromName(self, text):
    return entity_naming.get_entity_from_name(text)

  def getIDFromAlias (self, alias):
    return entity_naming.get_id_from_alias(alias)

  def get_tv_entities(self):
    entities = room_device_defaults.default_tv_entities()
    self.tv_room_entity = entities["tv_room_entity"]
    self.tvs = entities["tvs"]
    self.tv_picture_mode = entities["tv_picture_mode"]
    self.tv_soundbars = entities["tv_soundbars"]
    self.fire_tvs = entities["fire_tvs"]
    self.media_players = entities["media_players"]

  def get_time_setup(self):
    settings = room_time_settings.default_light_time_settings(self.room_type)
    self.daytime_lights_off_timeout = settings["daytime_lights_off_timeout"]
    self.nighttime_lights_off_timeout = settings["nighttime_lights_off_timeout"]
    self.daytime_start = settings["daytime_start"]
    self.afternoon_start = settings["afternoon_start"]
    self.daytime_end = settings["daytime_end"]

  def get_cover_entities(self):
    entities = room_device_defaults.default_cover_entities(self.room_entity)
    self.curtains = entities["curtains"]
    self.aqara_shutter_blind = entities["aqara_shutter_blind"]
    self.curtain_group = entities["curtain_group"]

    # Cover extra controls
#    self.light_in_daytime_postfix      = self.room_entity + "_light_in_daytime"
#    self.light_in_daytime              = "input_boolean." + self.room_entity + "_light_in_daytime"
#    self.curtain_in_nighttime_postfix = self.room_entity + "_curtain_in_nighttime"
#    self.curtain_in_nighttime          = "input_boolean." + self.room_entity + "_curtain_in_nighttime"


  def get_window_entities(self):
    entities = room_device_defaults.default_window_entities(self.room_entity)
    self.windows = entities["windows"]
    self.timeout_windows = entities["timeout_windows"]
    self.window_group = entities["window_group"]
    self.timeout_window_group = entities["timeout_window_group"]

  def get_temperature_control_entities(self):
    entities = room_device_defaults.default_temperature_control_entities(self.room_entity)
    self.outside_temperature = entities["outside_temperature"]
    self.room_default_temperature = entities["room_default_temperature"]
    self.thermostat = entities["thermostat"]
    self.thermostat_cloud_tado = entities["thermostat_cloud_tado"]
    self.thermostat_schedule = entities["thermostat_schedule"]
    self.temperature_sensor = entities["temperature_sensor"]
    self.room_heating_override = entities["room_heating_override"]

  def get_post_room_config(self):
    config = room_scene_defaults.default_post_room_config(
      self.room_entity,
      self.cfg_group_auto,
    )
    self.room_scene_ctl = config["room_scene_ctl"]
    self.cur_scene = config["cur_scene"]
    if "gui_ctl_group" in config:
      self.gui_ctl_group = config["gui_ctl_group"]

  def initialize_entity_intf(self):
    for key, value in entity_interface_defaults.default_entity_interface().items():
      setattr(self, key, value)

  def get_occupancy_ratio_sensor_config(self, x_minutes_multiple_str):
    result = occupancy_ratio_sensor.build_occupancy_ratio_sensor_config(
      x_minutes_multiple_str,
      self.occupancy_state_duration,
      self.room_name,
      self.motion_group,
      self.cfg_occupancy,
      self.getEntityFromName,
    )
    sensor_update = result["sensor_update"]
    if sensor_update != {}:
      setattr(self, sensor_update["attribute"], sensor_update["entity"])
    return result["ratio_sensor_config"]

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

  def add_group(self, group_entity_type, group_name, group_entity_list):
    simple_group_dict = entity_declaration_builders.simple_group(group_name, group_entity_list)

    if(group_entity_type == 'light'):
      self.light_list += simple_group_dict
    elif(group_entity_type == 'switch'):
      self.switch_list += simple_group_dict
    else:
        error("group_entity_type " + group_entity_type + " is not supported yet")


  def add_automation(self, entity_id, name, automation_type, unavailable_period='00:00:30', unavailable_device_id=None, device_id=None):
    if(automation_type == "Wifi Device Reconnect When Unavailable" ):
        self.automation_list += [
          entity_declaration_builders.wifi_reconnect_automation(
            entity_id=entity_id,
            name=name,
            automation_room_name=self.automation_room_name,
            room_name=self.room_name,
            unavailable_period=unavailable_period,
            unavailable_device_id=unavailable_device_id
          )
        ]
    else:
      error("Automation_type '" + automation_type + "' is not supported. Name = '" + name + "', entity_id:'" + entity_id + "'\n")



  def add_device(self, mac, name, comment, model, postfix=None, integration='Xiaomi Gateway 3', flex_switch=None, power_on_threshold=None,
                 switch_rename_dir=None, light_wall_switch=True, belong_to_group=None, enable_battery=True, smooth_battery=False, smooth_power=True, delay_off_minute=0,
                 enable_humidity_sensor=True, enable_shower_sensor=False, mdi_icon=None, device_class=None):

    # Check if inputs are legal
    group = belong_to_group
    if belong_to_group != None and type(belong_to_group) is not list:
      error("Model " + model + " belong_to_group is not a list. Name = " + name + name_postfix + ', MAC Address:' + mac + ", Integration " + integration)

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
         (model == "Mijia2 Contact"                    and integration in ['Xiaomi Gateway 3', 'Xiaomi Home'])):

      #entity_name = name + name_postfix
      #if group != None:
      #    group += ["binary_sensor." + self.getEntityFromName(entity_name)]
      mac_contact_postfix = '_contact_state_p_2_2' if integration == 'Xiaomi Home' else '_contact'
      mac_battery_postfix = '_battery_level_p_3_1' if integration == 'Xiaomi Home' else '_battery'
      self.binary_sensor_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "binary_sensor." + mac + mac_contact_postfix,
          "configured": True
        }
      ]

      self.add_battery_sensor(mac + mac_battery_postfix, name + " Battery" + name_postfix)

    elif((model == "Inverted Binary Sensor")):

      self.template_list += [
        {
          "binary_sensor": [
            {
              "name": name + name_postfix,
              "state": '{% set state = states.binary_sensor["' + mac + '"].state %} {% if state == "on"%} off {% elif state == "off"%} on {% else%} {{state}} {% endif %}'
            }
          ],
          "configured": True
        }
      ]

    ###################################################################################################
    # Buttons
    # Aqara Wireless Switch,   WXKG11LM  ZigbeeID: ["lumi.sensor_switch.aq2"]       action_list:[]
    # MiJia Wireless Switch,   WXKG01LM  ZigbeeID: ["lumi.sensor_switch"]           action_list:['single', 'double', 'triple', 'quadruple', 'many','release', 'hold']
    # MiJia Wireless Switch 2, ble XMWXKG01LM, lumi.remote.mcn001                   action_list:['single', 'double', 'hold']
    # Aqara Opple switch 3 bands, WXCJKG13LM, ZigbeeID: ["lumi.remote.b686opcn01"]  action_list:['button_1_single', 'button_2_single', 'button_3_single', 'button_4_single', 'button_5_single', 'button_6_single'] - more buttons for double/hold etc
    # Linptech KS1 Pro using Xiaomi Home, linp.sensor_ht.ks1bp
    # Yeelight 6 Key Remote, YLYK01YL
    ###################################################################################################
    elif((model == "Aqara Wireless Switch") or \
         (model == "MiJia Wireless Switch") or \
         (model == "MiJia Wireless Switch 2") or \
         (model == "Aqara Opple switch 3 bands") or \
         (model == 'Linptech KS1 4-Key Button') or \
         (model == 'Yeelight 6 Key Remote')):

      battery_postfix = ''
      if model == 'Linptech KS1 4-Key Button':

          battery_postfix     =            mac + '_battery_level_p_4_1003'
          single_click_entity = 'event.' + mac + '_click_e_5_1012'
          double_click_entity = 'event.' + mac + '_double_click_e_5_1013'
          long_press_entity   = 'event.' + mac + '_long_press_e_5_1014'

          self.add_event_binary_sensor(single_click_entity, name + ' Button 1 Single Click' + name_postfix, attribute_value=1)
          self.add_event_binary_sensor(single_click_entity, name + ' Button 2 Single Click' + name_postfix, attribute_value=2)
          self.add_event_binary_sensor(single_click_entity, name + ' Button 3 Single Click' + name_postfix, attribute_value=3)
          self.add_event_binary_sensor(single_click_entity, name + ' Button 4 Single Click' + name_postfix, attribute_value=4)
          self.add_event_binary_sensor(double_click_entity, name + ' Button 1 Double Click' + name_postfix, attribute_value=1)
          self.add_event_binary_sensor(double_click_entity, name + ' Button 2 Double Click' + name_postfix, attribute_value=2)
          self.add_event_binary_sensor(double_click_entity, name + ' Button 3 Double Click' + name_postfix, attribute_value=3)
          self.add_event_binary_sensor(double_click_entity, name + ' Button 4 Double Click' + name_postfix, attribute_value=4)
          self.add_event_binary_sensor(long_press_entity,   name + ' Button 1 Long Press'   + name_postfix, attribute_value=1)
          self.add_event_binary_sensor(long_press_entity,   name + ' Button 2 Long Press'   + name_postfix, attribute_value=2)
          self.add_event_binary_sensor(long_press_entity,   name + ' Button 3 Long Press'   + name_postfix, attribute_value=3)
          self.add_event_binary_sensor(long_press_entity,   name + ' Button 4 Long Press'   + name_postfix, attribute_value=4)

          self.automation_list += [{
              "alias" : "ZLB-" + self.automation_room_name + " 4-Key Button Light Control" + "-" + self.room_name,
              "configured": self.cfg_remote_light,
              "trigger":
                ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_1_single_click',
                                                       f'binary_sensor.{self.getEntityFromName(name)}_button_1_double_click',],   "to": 'on', "id": self.CYCLE_LAMP_0           }]) + \
                ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_1_long_press',  ],   "to": 'on', "id": self.TOGGLE_LAMP_0          }]) + \
                ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_2_single_click',
                                                       f'binary_sensor.{self.getEntityFromName(name)}_button_2_double_click',],   "to": 'on', "id": self.CYCLE_CEILING_LIGHTS   }]) + \
                ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_2_long_press',  ],   "to": 'on', "id": self.TOGGLE_CEILING_LIGHTS  }]) + \
                ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_3_single_click',
                                                       f'binary_sensor.{self.getEntityFromName(name)}_button_3_double_click',],   "to": 'on', "id": self.CYCLE_LAMP_1           }]) + \
                ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_3_long_press',  ],   "to": 'on', "id": self.TOGGLE_LAMP_1          }]) + \
                ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_4_single_click',
                                                       f'binary_sensor.{self.getEntityFromName(name)}_button_4_double_click',],   "to": 'on', "id": self.CYCLE_LEDS             }]) + \
                ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_4_long_press',  ],   "to": 'on', "id": self.TOGGLE_LEDS            }]) + \
                ([]),
              "mode":"queued", # this has to be queued to make sure no button press is ignored
              "action": self.get_trigger_action_list()
          }]

      elif model == 'Yeelight 6 Key Remote':
        # no battery entity for this remote

        self.add_event_binary_sensor('event.' + mac + '_button_on',          name + ' Button 1 Single Click', 'event_type', 'press')
        self.add_event_binary_sensor('event.' + mac + '_button_off',         name + ' Button 2 Single Click', 'event_type', 'press')
        self.add_event_binary_sensor('event.' + mac + '_button_brightness',  name + ' Button 3 Single Click', 'event_type', 'press')
        self.add_event_binary_sensor('event.' + mac + '_button_plus',        name + ' Button 4 Single Click', 'event_type', 'press')
        self.add_event_binary_sensor('event.' + mac + '_button_m',           name + ' Button 5 Single Click', 'event_type', 'press')
        self.add_event_binary_sensor('event.' + mac + '_button_min',         name + ' Button 6 Single Click', 'event_type', 'press')
        self.add_event_binary_sensor('event.' + mac + '_button_on',          name + ' Button 1 Long Press',   'event_type', 'long_press')
        self.add_event_binary_sensor('event.' + mac + '_button_off',         name + ' Button 2 Long Press',   'event_type', 'long_press')
        self.add_event_binary_sensor('event.' + mac + '_button_brightness',  name + ' Button 3 Long Press',   'event_type', 'long_press')
        self.add_event_binary_sensor('event.' + mac + '_button_plus',        name + ' Button 4 Long Press',   'event_type', 'long_press')
        self.add_event_binary_sensor('event.' + mac + '_button_m',           name + ' Button 5 Long Press',   'event_type', 'long_press')
        self.add_event_binary_sensor('event.' + mac + '_button_min',         name + ' Button 6 Long Press',   'event_type', 'long_press')

        # There is no Double Click but just leave placeholders in the trigger
        self.automation_list += [{
            "alias" : "ZLB-" + self.automation_room_name + "6 Key Button Remote" + "-" + self.room_name,
            "configured": self.cfg_remote_light,
            "trigger":
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_1_single_click',
                                                     f'binary_sensor.{self.getEntityFromName(name)}_button_1_double_click' ],   "to": 'on', "id": self.CYCLE_SCENES            }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_1_long_press',  ],   "to": 'on', "id": self.TOGGLE_ALL_LIGHTS       }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_2_single_click',
                                                     f'binary_sensor.{self.getEntityFromName(name)}_button_2_double_click',
                                                     f'binary_sensor.{self.getEntityFromName(name)}_button_2_long_press',  ],   "to": 'on', "id": self.TOGGLE_CURTAINS         }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_3_single_click',
                                                     f'binary_sensor.{self.getEntityFromName(name)}_button_3_double_click',],   "to": 'on', "id":  self.CYCLE_CEILING_LIGHTS   }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_3_long_press',  ],   "to": 'on', "id": self.TOGGLE_CEILING_LIGHTS   }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_4_single_click',
                                                     f'binary_sensor.{self.getEntityFromName(name)}_button_4_double_click',],   "to": 'on', "id":   self.CYCLE_LEDS            }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_4_long_press',  ],   "to": 'on', "id":  self.TOGGLE_LEDS            }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_5_single_click',
                                                     f'binary_sensor.{self.getEntityFromName(name)}_button_5_double_click',],   "to": 'on', "id":  self.CYCLE_LAMP_0           }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_5_long_press',  ],   "to": 'on', "id": self.TOGGLE_LAMP_0           }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_6_single_click',
                                                     f'binary_sensor.{self.getEntityFromName(name)}_button_6_double_click',],   "to": 'on', "id":  self.CYCLE_LAMP_1           }]) + \
              ([{"platform": "state",  "entity_id": [f'binary_sensor.{self.getEntityFromName(name)}_button_6_long_press',  ],   "to": 'on', "id": self.TOGGLE_LAMP_1           }]) + \
              ([]),
            "mode":"queued", # this has to be queued to make sure no button press is ignored
            "action": self.get_trigger_action_list()
        }]

      elif ((model == "MiJia Wireless Switch") or (model == "MiJia Wireless Switch 2")) and integration == 'Xiaomi Home':

        battery_postfix = mac + '_battery_level_p_2_1003'

        self.add_event_binary_sensor('event.' + mac + '_click_e_3_1012',         name + ' Button Single Click',   'event_type', 'Click')
        self.add_event_binary_sensor('event.' + mac + '_double_click_e_3_1013',  name + ' Button Double Click',   'event_type', 'Double Click')
        self.add_event_binary_sensor('event.' + mac + '_long_press_e_3_1014',    name + ' Button Long Press',     'event_type', 'Long Press')

      else:
        if model == "Aqara Opple switch 3 bands" and integration == 'Z2M':
          mac = mac + "_" + mac
          mac_postfix = '_action'
        else:
          mac_postfix = '_button_action' if integration == 'Z2M' else \
                        '_action'

        battery_postfix = mac + '_battery'
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

      if battery_postfix != '': # some device such as Yeelight Remote does not have battery
        self.add_battery_sensor(battery_postfix, name + " Button Battery" + name_postfix, smooth_battery=True, enable_battery=enable_battery)

    ###################################################################################################
    # Light Sensors
    # Xiaomi Light Detection Sensor GZCGQ01LM ZigbeeID: ["lumi.sen_ill.mgl01"]
    # Xiaomi Light Detection Sensor To Mirror Sensor GZCGQ01LM ZigbeeID: ["lumi.sen_ill.mgl01"]
    # Generic Light Intensity
    ###################################################################################################
    elif((model == "Xiaomi Light Detection Sensor") or \
         (model == "Xiaomi Light Detection Sensor To Mirror Sensor") or \
         (model == "Generic Light Intensity")
         ):



      if model == "Xiaomi Light Detection Sensor":
        self.template_list += [
          {
            "sensor": [
              {
                "name": name + " Light Sensor" + name_postfix,
                "state": '{{states.sensor["' + mac + '_illuminance"].state}}',
                "unit_of_measurement": "lx",
              }
            ],
            "configured": True
          }
        ]
        self.add_battery_sensor(mac + '_battery', name + " Light Sensor Battery" + name_postfix, smooth_battery=True)

      if((model == "Xiaomi Light Detection Sensor To Mirror Sensor")):
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
        self.add_battery_sensor(mac + '_battery', name + " Light Sensor Battery" + name_postfix, smooth_battery=True)


      if (model == "Generic Light Intensity"):
        light_intensity_name = name + " Light Intensity" + name_postfix

        # Add a filtered sensor for 15 min moving average
        self.sensor_list += [
          {
            "platform": "filter",
            "name": mac + " 15 Min Moving Average",
            "entity_id": 'sensor.' + mac,
            "filters": [
              # 1. Outlier filter: Drops extreme spikes that deviate too fast from the median
              {"filter": "outlier", "window_size": 5, "radius": 20000},
              # 2. Moving Average: Smooths the remaining data over a rolling 15-minute window
              {"filter": "time_simple_moving_average", "window_size": "00:15:00", "precision": 0}
            ],
            "configured": True
          }
        ]

        # Add a template sensor for percentage
        self.template_list += [
          {
            "sensor": [
              {
                "name": light_intensity_name,
                "unit_of_measurement": "%",
                "icon": "mdi:eye",
                "state": """
                    {% set lux = states('sensor.""" + mac + """_15_min_moving_average') | float(0) %}

                    {# Map max expected daylight (70,000 lx) down to a 0-1 scale #}
                    {# y represents Relative Luminance (0.0 to 1.0) #}
                    {% set y = lux / 70000 %}
                    {% if y <= 0 %}
                      0
                    {% elif y <= 0.008856 %}
                      {# LINEAR TAIL FOR DEEP SHADOWS #}
                      {# 0.008856 is exactly (6/29)^3. It is the intersection threshold. #}
                      {# 903.3 is exactly (29/3)^3. It is the slope that perfectly matches the curve below. #}
                      {{ (y * 903.3) | round(1) }}
                    {% else %}
                      {# STEVENS' POWER LAW CUBE ROOT CURVE FOR DAYLIGHT #}
                      {# 116 and 16 are scaling factors ensuring that when y=1, output is exactly 100 #}
                      {% set perceived = ((y ** (1/3)) * 116) - 16 %}

                      {# Cap at 100% in case a summer glare pushes lux over 70,000 #}
                      {{ ([perceived, 100] | min) | round(1) }}
                    {% endif %}""",
              }
            ],
            "configured": True
          }
        ]

    ###################################################################################################
    # Motion Sensors
    #
    # Aqara Motion and Illuminance Sensor, RTCGQ11LM ZigbeeID: ["lumi.sensor_motion.aq2"]
    # MiJia Human Body Movement Sensor, RTCGQ01LM
    # Mijia Motion Sensor 2/2s,    RTCGQ02LM
    ###################################################################################################
    elif((model == "Aqara Motion and Illuminance Sensor"                                           ) or \
         (model == "MiJia Human Body Movement Sensor"                                              ) or \
         (model == "Mijia Motion Sensor 2"                   and integration == 'Xiaomi Gateway 3')):

      motion_entity_prefix  = 'lumi_cn_lumi_' if integration == 'Xiaomi Home' else \
                              ''            # if integration == 'Xiaomi Gateway 3'

      motion_entity_postfix = '_occupancy'              if integration == 'Z2M' else \
                              '_aq2_motion_state_p_2_1' if integration == 'Xiaomi Home' else \
                              '_motion'               # if integration == 'Xiaomi Gateway 3'


      # remove leading bits 0x00158d0005228ba8 -> 158d0005228ba8 for Xiaomi Home
      mac = mac.removeprefix("0x").lstrip("0") if integration == 'Xiaomi Home' else mac

      motion_full_name = name + " Motion Sensor Motion"  + name_postfix
      self.binary_sensor_list += [
        {
          "platform": "group",
          "name": motion_full_name,
          "device_class": 'motion',
          "entities": "binary_sensor." + motion_entity_prefix + mac + motion_entity_postfix,
          "configured": True
        }
      ]

      # Xiaomi Home does not support battery
      if integration != 'Xiaomi Home':
        self.add_battery_sensor(mac + '_battery', name + " Motion Sensor" + name_postfix + " Battery", smooth_battery=True)


         #      light_entity_postfix = '_illuminance_lux' if integration == 'Z2M' else \
         #                             '_illuminance'   # if integration == 'Xiaomi Gateway 3'
         #
         #      self.template_list += [
         #        {
         #          "sensor": [
         #            {
         #              "name": name + " Motion Sensor Light" + name_postfix,
         #              "unit_of_measurement": "lx",
         #              "state": '{{states.sensor["' + mac + light_entity_postfix + '"].state}}'
         #            }
         #          ],
         #          "configured": True
         #        }
         #      ]
         #


    ###################################################################################################
    # Motion Sensors, Occupancy Sensor
    #
    # Ziqing Occupancy Sensor, Mesh model: "mesh IZQ-24"
    # Xiaomi Occupancy Sensor
    # Linptech Occupancy Sensor ES3
    ###################################################################################################

    elif (model == "Ziqing Occupancy Sensor") or \
         (model == "Xiaomi Occupancy Sensor") or \
         (model == "Linptech Occupancy Sensor ES3") or \
         (model == "Linptech Occupancy Sensor ES5") :

      if name_postfix != '':
        error (f'name_postfix is not supported for {mac} and {model} in {self.room_name}')

      if integration == 'Xiaomi Home':
        if model == "Linptech Occupancy Sensor ES3":
          occupancy_postfix       = mac + '_occupancy_status_p_2_1078'
          no_one_duration_postfix = mac + '_no_one_duration_p_2_1079'
          battery_entity_postfix  = mac + '_battery_level_p_4_1003'
        elif model == "Linptech Occupancy Sensor ES5":
          occupancy_postfix       = mac + '_occupancy_status_p_2_1078'
          no_one_duration_postfix = mac + '_no_one_duration_p_2_1082'
          battery_entity_postfix  = mac + '_battery_level_p_7_1003'
        elif model == "Xiaomi Occupancy Sensor":
          occupancy_postfix       = mac + '_occupancy_status_p_2_1078'
          no_one_duration_postfix = mac + '_no_one_duration_p_2_1082'
          battery_entity_postfix  = mac + '_battery_level_p_3_1003'
        raw_occupancy_state   = f'states.binary_sensor["{occupancy_postfix}"].state'
        no_one_duration_state = f'states.sensor["{ no_one_duration_postfix}"].state'
      else: # Xiaomi Gateway 3
        raw_occupancy_state    = f'states.binary_sensor["{mac}_occupancy"].state'
        no_one_duration_state  = f'states.sensor["{       mac}_no_one_duration"].state'
        battery_entity_postfix = mac + '_battery'

      # These sensors maintain their 'On' state for extended periods and don't update frequently.
      # If Home Assistant reboots and the state changes while HA is offline, the state change will be missed.
      # HA will retain the last recorded state, resulting in an inaccurate reading. To address this,
      # use the no one duration sensor as an alternative approach.
      self.template_list += [
        {
          "binary_sensor": [
            {
              "name": name + " Occupancy Sensor Occupancy" + name_postfix,
              "state": "{%" + f" if {no_one_duration_state} == 'unavailable' or {no_one_duration_state}  == 'unknown'" + "%}\n"  + \
                         "{{" + raw_occupancy_state + "}}\n" + \
                       "{%" + f" elif {no_one_duration_state} == '0' " + "%}\n"  + \
                         "{{" + raw_occupancy_state + "}}\n" + \
                       "{#" + f' else is equivilence to elif {no_one_duration_state} > "0" ' + "#}\n"  + \
                       "{% else %}\n"  + \
                         "off\n" + \
                       "{% endif %}\n",
              "device_class": 'occupancy',
            }
          ],
          "configured": True
        }
      ]

      self.add_battery_sensor(battery_entity_postfix, name + " Occupancy Sensor Battery" + name_postfix, smooth_battery=True)


          #  self.binary_sensor_list += [
          #    {
          #      "platform": "group",
          #      "name": name + " Occupancy Sensor Raw Occupancy" + name_postfix,
          #      "entities": "binary_sensor." + mac + '_occupancy',
          #      "configured": True
          #    }
          #  ]
          #  self.template_list += [
          #    {
          #      "sensor": [
          #        {
          #          "name": name + " Occupancy Sensor Light" + name_postfix,
          #          "unit_of_measurement": "lx",
          #          "state": '{{states.sensor["' + mac + '_illuminance"].state}}'
          #        }
          #      ],
          #      "configured": True
          #    }
          #  ]



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
        } | ({"device_class": device_class} if device_class != None else {})
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
         (model == "Qingping Lite Temperature Sensor" and integration == 'Xiaomi Gateway 3') or \
         (model == "Mijia3 Temperature Sensor 3 Mini" and integration == 'Xiaomi Home'     )):

      mac_temperature_postfix = '_temperature_p_2_1001'        if integration == 'Xiaomi Home' else '_temperature'
      mac_humidity_postfix    = '_relative_humidity_p_2_1002'  if integration == 'Xiaomi Home' else '_humidity'
      mac_battery_postfix     = '_battery_level_p_3_1003'      if integration == 'Xiaomi Home' else '_battery'

      # Temperature entity
      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Temperature Sensor" + name_postfix,
              "unit_of_measurement": "°C",
              "state": '{{states.sensor["' + mac + mac_temperature_postfix + '"].state | float(22) | round(1)}}'
            }
          ],
          "configured": True
        }
      ]


      # Add battery entity
      self.add_battery_sensor(mac + mac_battery_postfix, name + " Temperature Sensor" + name_postfix + " Battery", smooth_battery=True)

      # Humidity entity
      if enable_humidity_sensor is True:
        humidity_sensor_name    = name + " Humidity Sensor" + name_postfix
        humidity_entity_postfix = self.getEntityFromName(humidity_sensor_name)
        humidity_entity         = 'sensor.' + humidity_entity_postfix
        self.template_list += [
          {
            "sensor": [
              {
                "name": humidity_sensor_name,
                "unit_of_measurement": "%",
                "state": '{{states.sensor["' + mac + mac_humidity_postfix + '"].state | float(40) | round(1)}}'
              }
            ],
            "configured": True
          }
        ]

        # Shower entity
        if enable_shower_sensor is True:
          humidity_rising_postfix  = self.getEntityFromName(name) + "_humidity_rising"
          humidity_falling_postfix = self.getEntityFromName(name) + "_humidity_falling"
          humidity_rising_entity   = 'binary_sensor.' + humidity_rising_postfix
          humidity_falling_entity  = 'binary_sensor.' + humidity_falling_postfix

          self.binary_sensor_list += [
            {
              "platform": "trend",
              "sensors": {
                humidity_rising_postfix: {
                  #'friendly_name ': self.getNameFromEntity(humidity_rising_postfix),
                  "entity_id": "sensor." + humidity_entity_postfix,
                  "sample_duration": 300,
                  "min_gradient": 0.002
                },
                humidity_falling_postfix: {
                  #'friendly_name ': self.getNameFromEntity(humidity_falling_postfix),
                  "entity_id": "sensor." + humidity_entity_postfix,
                  "sample_duration": 300,
                  "min_gradient": -0.002
                }
              },
              "configured": True,
            }
          ]

          shower_name = name + " Shower" + name_postfix
          self.template_list += [
            {
              "binary_sensor": [
                {
                  "name": shower_name,
                  "state":'{% set h = states("' + humidity_entity + '") %}' + \
                          '{% if h not in ["unknown", "unavailable", "none"] %}' + \
                            '{{ h | float > 60' + \
                              'and is_state("' + humidity_rising_entity + '", "on")' + \
                              'and not is_state("' + humidity_falling_entity + '", "on") }}' + \
                          '{% else %}' + \
                            'false' + \
                          '{% endif %}',
                  'delay_on': 5,
                  'delay_off': 5,
                }
              ],
              "configured": True
            }
          ]

          # Add to GUI
          self.shower_sensors  = ['binary_sensor.' + self.getEntityFromName(shower_name)]
          self.gui_ctl_entity_list += self.shower_sensors

    elif model in [ "Mijia2 Temperature Clock" ] and integration == 'Passive BLE Monitor':

      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Temperature Sensor" + name_postfix,
              "unit_of_measurement": "°C",
              "state": '{{states.sensor["temperature_humidity_sensor_' + mac + '_temperature"].state | float(22) | round(1)}}'
            }
          ],
          "configured": True
        }
      ]

    elif((model in ["Aqara B1 curtain motor", "Aqara roller shade motor"] and integration == 'Xiaomi Gateway 3')):

      cover_full_name = name + name_postfix
      self.cover_list += [
        {
          "platform": "group",
          "name": cover_full_name,
          "entities": "cover." + mac + "_motor",
          "configured": True
        }
      ]

      if mdi_icon != None:
        self.customize_dict |= {'cover.' + self.getEntityFromName(cover_full_name): {'icon': 'mdi:' + mdi_icon}}

          #      self.template_list += [
          #        {
          #          "sensor": [
          #            {
          #              "name": name + " Curtain Battery" + name_postfix,
          #              "unit_of_measurement": "%",
          #              "state": '{{states.sensor["' + mac + '_battery"].state}}'
          #            }
          #          ],
          #          "configured": True
          #        }
          #      ]

      self.aqara_shutter_blind = True if model in ["Aqara roller shade motor"] else False

    ###################################################################################################
    # Generic Light
    # Mijia BLE Lights, MJDP09YL
    ###################################################################################################
    elif((model == "Generic Light"                                                                    ) or \
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
    # Generic Switch
    # Mi Power Plug ZigBee, ZNCZ02LM ZigbeeID: ["lumi.plug"]
    ###################################################################################################
    elif((model == "Generic Switch"      ) or \
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

      raw_sensor            = 'sensor.' + mac
      smooth_sensor         = 'sensor.' + mac + '_smoothed'
      smooth_sensor_postfix =             mac + '_smoothed'
      if smooth_power:
        self.add_smooth_power_sensor(raw_sensor, smooth_sensor)
      else:
        smooth_sensor_postfix = mac

      self.template_list += [
        {
          "binary_sensor": [
            {
              "name": name + name_postfix,
              # round(1) means to round to 0.1
              "state": '{% if states("sensor.' + smooth_sensor_postfix + '") | float(0) | round(1) > ' + str(power_on_threshold) + ' %} on {% else %} off {% endif %}',
              "delay_off":  {"minutes": delay_off_minute},
            }
          ],
          "configured": True
        }
      ]

    ###################################################################################################
    # Tado Homekit
    ###################################################################################################
    elif model == "Tado Homekit":

      # common variable
      self.controlled_thermostat_entity      = f"climate.tado_smart_radiator_thermostat_{mac}"
      self.controlled_thermostat_temperature = f"sensor.tado_smart_radiator_thermostat_{mac}_current_temperature"
      self.climate_dummy_heater_entity       = f"input_boolean.{self.room_entity}_dummy_heater_entity"
      self.tado_heater_entity                = f"input_boolean.{self.room_entity}_tado_heater"
      # Add to GUI
      self.gui_ctl_entity_list               += [self.controlled_thermostat_entity]

      self.generic_thermostat = {
              "platform": "generic_thermostat",
              "name": name + name_postfix,
              "heater": 'unintialized_heater',
              "target_sensor": 'unintialized_sensor',
              "min_temp": 7,  # limited by generic_thermostat
              "max_temp": 25, # limited by tado
              "ac_mode": False,
              "cold_tolerance": 0, # start heating immediately below target temperature
              "precision": 0.1,
              "target_temp_step":0.5,
              "min_cycle_duration": '00:01:30',
              "configured": self.cfg_temp_control,
      }

      # Set a temperature sensor to detect if tado is online
      # if the temperautre is unavailable, it will be picked up by unavailable sensor
      self.template_list += [
        {
          "sensor": [
            {
              "name": name + " Tado Availiabity" + name_postfix,
              "unit_of_measurement": "°C",
              "state": '{{states("' + self.controlled_thermostat_temperature + '") | float(22) | round(1)}}'
            }
          ],
          "configured": True
        }
      ]

      # Getting heating required sensor if tado requires heating
      self.tado_heating_required = self.room_name + " Heating Required"
      self.template_list += [
        {
          "binary_sensor": [
            {
              "name": self.tado_heating_required,
              "state": (
                        '{% set climate = "' + self.controlled_thermostat_entity + '" %}'
                        # test entity state first, otherwise 'temperature' attribute may not be available if it is not in heat state
                        '{% if states(climate) == "unavailable" or states(climate) == "off" or (state_attr(climate, "temperature") <= state_attr(climate, "current_temperature"))  %}'
                        'off'
                        '{% else %} '
                        'on'
                        '{% endif %}'
                       )
            }
          ],
          "configured": self.cfg_temp_control
        }
      ]
      # Add to GUI
      self.gui_ctl_entity_list += ['binary_sensor.' + self.getEntityFromName(self.tado_heating_required)]


      if  self.cfg_tado_calibrate_uses_lan == False or \
         (self.cfg_tado_calibrate_uses_lan == True  and self.cfg_temp_calibration == False): # if no calibration, this method needs to be used

        # Sync helper renamed thermostat entity to the actual homekit radiator value as renaming feature
        # (controlling on tado valve by hand is not working, better to put child lock on)
        # Calibrate is using cloud integration, which only update every 10 min and may not be working due to out-of-order Tado integration

        self.input_boolean_dict |= {
          self.getPostfix(self.climate_dummy_heater_entity) : {
            "name" :  self.getNameFromEntity(self.climate_dummy_heater_entity),
            "initial": "off",
            "configured": self.cfg_temp_control
          }
        }

        self.generic_thermostat['heater']        = self.climate_dummy_heater_entity
        self.generic_thermostat['target_sensor'] = self.controlled_thermostat_temperature

        self.automation_list += [
          {
            "alias": "ZH-" + self.automation_room_name + "Rename Thermostat" + "-" + self.room_name,
            "configured": self.cfg_temp_control,
            "triggers": [
              {
                "trigger": "state",
                "entity_id": self.thermostat,
                "attribute": "temperature"
              },
              {
                "trigger": "state",
                "entity_id": self.thermostat, # HVAC state
              }
            ] + self.get_time_pattern_trigger(),
            "actions": [
              {
                "action": "climate.set_temperature",
                "data": {
                  "temperature": "{{states." + self.thermostat + ".attributes.temperature}}",
                  "hvac_mode":   "{{states." + self.thermostat + ".state}}",
                },
                "target": {
                  "entity_id": self.controlled_thermostat_entity
                }
              }
            ]
          }
        ]

        self.automation_list += [
          {
            "alias" : "ZH-" + self.automation_room_name + "Valve Calibrate Temperature Using External Sensor" + "-" + self.room_name,
            "configured": self.cfg_temp_control and self.cfg_temp_calibration,
            "use_blueprint": {
              "path": "calibrate_valve_temperature.yaml",
              "input": {
                "tado_valve_entity": self.thermostat_cloud_tado,
                "external_temperature_sensor_entity": self.temperature_sensor
              }
            }
          }
        ]

      else:
        # Sync helper renamed thermostat entity to the actual homekit radiator value as renaming feature
        # (controlling on tado valve by hand is not working, better to put child lock on)
        #
        # If external temperature sensor is online, using one of the following calibrations:
        # 1) Calibrate is using manual on-off automation, that on is tado open max, off is tado close.
        #    On - tado with offset -5 and set temperature to 25
        #    Off - tado off
        # 2) On top of method (1), instead of setting tado open max, setting the difference from
        #    the tado target temperature to the tado current temperature to the same value as
        #    the room target temperature to the room current temperature (measured by external temperature sensor).
        #    This should how much the valve is opened based on tado's algorithmn.
        #    Tado internal offset needs to be quite negative, such as -7, in order to heat the room up enough as
        #    the max value to set is 25 degrees.
        self.calibration_method = 2
        # If external temperature sensor is offline or not given. Using the default temperature sensor

        self.input_boolean_dict |= {
          self.getPostfix(self.tado_heater_entity) : {
            "name" :  self.getNameFromEntity(self.tado_heater_entity),
            "configured": self.cfg_temp_control
          }
        }

        self.generic_thermostat['heater']        = self.tado_heater_entity
        self.generic_thermostat['target_sensor'] = self.temperature_sensor # directly using the external temperature sensor
        self.generic_thermostat['min_temp']      = 16 # set max temperature higher
        self.generic_thermostat['max_temp']      = 27 # set max temperature higher

        if self.calibration_method == 1:
          self.automation_list += [
            {
              "alias": "ZH-" + self.automation_room_name + "Open/Close Radiator Valve Using External Sensor" + "-" + self.room_name,
              "configured": self.cfg_temp_control,
              "triggers": [
                {
                  "trigger": "state",
                  "entity_id": self.tado_heater_entity,
                }
              ] + self.get_time_pattern_trigger(),
              "actions": [
                {
                  "if": [
                    {
                      "condition": "state",
                      "entity_id": self.tado_heater_entity,
                      "state": "on"
                    }
                  ],
                  "then": [
                    {
                      "action": "climate.set_temperature",
                      "data": {
                        "hvac_mode": "heat",
                        "temperature": 25
                      },
                      "target": {
                        "entity_id": self.controlled_thermostat_entity
                      }
                    }
                  ],
                  "else": [
                    {
                      "action": "climate.turn_off",
                      "target": {
                        "entity_id": self.controlled_thermostat_entity
                      }
                    }
                  ]
                }
              ]
            }
          ]

        elif self.calibration_method == 2:

          self.automation_list += [
            {
              "alias": "ZH-" + self.automation_room_name + "Set Radiator Valve Target Temperature Based on External Sensor Temperature Difference" + "-" + self.room_name,
              "configured": self.cfg_temp_control,
              "triggers": [
                {
                  "trigger": "state",
                  "entity_id": self.tado_heater_entity,
                },
                {
                  "trigger": "state",
                  "entity_id": self.controlled_thermostat_entity, # tado current temperature
                  "attribute": "temperature"
                },
                {
                  "trigger": "state",
                  "entity_id": self.controlled_thermostat_entity,
                  "attribute": "current_temperature"
                },
              ] + self.get_time_pattern_trigger(),
              "mode":"single", # make sure calibration do not go too often, currently set a delay per calibration.
              "actions": [
                {
                  "if": [
                    {
                      "condition": "state",
                      "entity_id": self.tado_heater_entity,
                      "state": "on"
                    }
                  ],
                  "then": [
                    {
                      "action": "climate.set_temperature",
                      "data": {
                        "hvac_mode": "heat",
                        "temperature": \
                            "{%set room_helper_entity = '" + self.thermostat + "' %}" + \
                            "{%set tado_valve_entity  = '" + self.controlled_thermostat_entity + "' %}  " + \
                            "{%set room_cur_temp      = state_attr(room_helper_entity, 'current_temperature') | float %}  " + \
                            "{%set room_target_temp   = state_attr(room_helper_entity, 'temperature')         | float %}  " + \
                            "{%set tado_cur_temp      = state_attr(tado_valve_entity,  'current_temperature') | float %}  " + \
                            "{#diff = room_target_temp - room_cur_temp = tado_target_temp_nxt - tado_cur_temp #}" + \
                            "{% set tado_target_temp_nxt = ((room_target_temp - room_cur_temp + tado_cur_temp) * 2) | float(22) | round / 2 %} {# round to 0.5 #}" + \
                            "{%set tado_target_temp_nxt_sat = [[tado_target_temp_nxt, 25]|min,5]|max %} {# set lower and upper limit to [5,25] #}" + \
                            "{{tado_target_temp_nxt_sat}}"
                            # Debugging
                            # room_cur_temp: "{{    state_attr(room_helper_entity, 'current_temperature') | float }}"
                            # room_target_temp: "{{ state_attr(room_helper_entity, 'temperature')         | float }}"
                            # tado_cur_temp: "{{    state_attr(tado_valve_entity,  'current_temperature') | float }}"
                            # tado_target_temp_nxt = "{{ tado_target_temp_nxt }}"g
                            # tado_target_temp_nxt_sat = "{{ tado_target_temp_nxt_sat  }}"
                      },
                      "target": {
                        "entity_id": self.controlled_thermostat_entity
                      }
                    },
                    {"delay": '00:05:00'},
                  ],
                  "else": [
                    {
                      "action": "climate.turn_off",
                      "target": {
                        "entity_id": self.controlled_thermostat_entity
                      }
                    }
                  ]
                }
              ]
            }
          ]

      # Added configured generic thermostat
      self.climate_list += [self.generic_thermostat]

    ###################################################################################################
    elif model == "Generic Curtain":
    ###################################################################################################
      self.cover_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "cover." + mac,
          "configured": True
        }
      ]
    ###################################################################################################
    elif model == "Generic Locks":
    ###################################################################################################
      self.lock_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "lock." + mac,
          "configured": True
        }
      ]
    ###################################################################################################
    elif model == "Generic Event":
    ###################################################################################################
      self.event_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "event." + mac,
          "configured": True
        }
      ]

    ###################################################################################################
    elif model == "Generic Button":
    ###################################################################################################
      self.button_list += [
        {
          "platform": "group",
          "name": name + name_postfix,
          "entities": "button." + mac,
          "configured": True
        }
      ]
    ###################################################################################################
    elif model == "Generic Battery":
    ###################################################################################################

      self.add_battery_sensor(mac, name+name_postfix, smooth_battery=True)

    ###################################################################################################
    # Model not found, throw an error
    ###################################################################################################
    else:
      raise TypeError( "\n" +\
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                       "Model '" + model + "' is not supported. Name = '" + name + name_postfix + "', MAC Address:'" + mac + "', Integration '" + integration + "'\n" + \
                       "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")


  def get_time_pattern_trigger(self, minutes=30, ha_start_trigger=True):
    return automation_helpers.get_time_pattern_trigger(minutes=minutes, ha_start_trigger=ha_start_trigger)

  def add_average_temperature_sensor(self, sensor_1, sensor_2, sensor_out):
      self.template_list += [
        sensor_declaration_builders.average_temperature_sensor(
          sensor_1,
          sensor_2,
          sensor_out,
          self.getNameFromEntity,
        )
      ]


  def add_battery_sensor(self, mac, name, smooth_battery=True, enable_battery=True):
    if enable_battery is True:
        declarations = sensor_declaration_builders.battery_sensor_declarations(
          mac,
          name,
          self.getEntityFromName,
          self.getNameFromEntity,
        )
        self.sensor_list += declarations["sensor_list_additions"]
        self.template_list += declarations["template_list_additions"]

  def add_event_binary_sensor(self, entity_id, name, attribute_name='Button Type', attribute_value=1, auto_off=0.2):
      self.template_list += [
        sensor_declaration_builders.event_binary_sensor(
          entity_id,
          name,
          attribute_name=attribute_name,
          attribute_value=attribute_value,
          auto_off=auto_off,
        )
      ]

  def add_smooth_power_sensor(self, sensor_in, sensor_out):
      self.sensor_list += [
        sensor_declaration_builders.smooth_power_sensor(
          sensor_in,
          sensor_out,
          self.getNameFromEntity,
        )
      ]

  def add_smooth_temperature_sensor(self, sensor_in, sensor_out):
      self.sensor_list += [
        sensor_declaration_builders.smooth_temperature_sensor(
          sensor_in,
          sensor_out,
          self.getNameFromEntity,
        )
      ]

  def get_entity_declarations(self):
      self.get_script_dict()
      self.input_select_dict |= {
        self.getPostfix(self.room_scene_ctl) : {
          "name" :  self.getNameFromEntity(self.room_scene_ctl),
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

        }
      }

      self.input_select_dict |= {
        self.getPostfix(self.room_occupancy) : {
          "name" :  self.getNameFromEntity(self.room_occupancy),
          "options":[
            "Outside",
            "Just Entered",
            "Stayed Inside",
            "In Sleep"
          ],
          "configured": self.cfg_occupancy
        }
      }

      # Looping through all scenes
      for scene in self.ceiling_light_control_when:
        self.input_boolean_dict |= {
          self.getPostfix(self.ceiling_light_control_when[scene]) : {
            "name" :  self.getNameFromEntity(self.ceiling_light_control_when[scene]),
            #"initial": "on",
            "configured": True
          } | ({"initial": "off"} if len(self.ceiling_lights) == 0 and len(self.curtains) == 0 else {}),

          self.getPostfix(self.lamp_control_when[scene]) : {
            "name" :  self.getNameFromEntity(self.lamp_control_when[scene]),
            #"initial": "on",
            "configured": True
          } | ({"initial": "off"} if len(self.lamps) == 0 and len(self.curtains) == 0 else {}),

          self.getPostfix(self.led_control_when[scene]) : {
            "name" :  self.getNameFromEntity(self.led_control_when[scene]),
            #"initial": "on",
            "configured": True
          } | ({"initial": "off"} if len(self.leds) == 0 and len(self.curtains) == 0 else {}),

          self.getPostfix(self.curtain_control_when[scene]) : {
            "name" :  self.getNameFromEntity(self.curtain_control_when[scene]),
            #"initial": "off",
            "configured": True
          } | ({"initial": "off"} if len(self.curtains) == 0 else {}),
        }

        self.input_boolean_dict |= {
          #self.getPostfix(self.force_stay_inside) : {
          #  "name" :  self.getNameFromEntity(self.force_stay_inside),
          #  "initial": "off",
          #  "configured": self.cfg_occupancy
          #},
          self.getPostfix(self.room_heating_override) : {
            "name" :  self.getNameFromEntity(self.room_heating_override),
            "initial": "off",
            "configured": self.cfg_temp_control
          }
        }

      if self.room_type == 'bedroom':
        self.input_boolean_dict |= {
          self.getPostfix(self.sleep_time) : {
            "name" :  self.getNameFromEntity(self.sleep_time),
            "configured": self.cfg_occupancy
          }
        }

      self.input_number_dict |= {
        self.getPostfix(self.min_value_as_bright) : {
          "name" :  self.getNameFromEntity(self.min_value_as_bright),
          "min": 0,
          "max": 4000,
          "step": 1,
          "mode": 'box',
          #"initial": 250,
          "configured": True
        },
      }


      for scene in self.light_intensity_threshold_when:
        self.input_number_dict |= {
          self.getPostfix(self.light_intensity_threshold_when[scene]) : {
            "name" :  self.getNameFromEntity(self.light_intensity_threshold_when[scene]),
            #"initial": "8.0",
            "min": 0,
            "max": 100,
            "step": 0.1,
            "mode": 'box',
            "configured": True
          } | ({"initial": "0.0"} if self.light_intensity_entity == '' else {}),
        }


      self.input_datetime_dict |= {
        self.getPostfix(self.noon_time) : {
          "name" :  self.getNameFromEntity(self.noon_time),
          "has_date": False,
          "has_time": True,
          #"initial": "13:00:00",
          "configured": True
        },
        #self.getPostfix(self.morning_start_time) : {
        #  "name" :  self.getNameFromEntity(self.morning_start_time),
        #  "has_date": False,
        #  "has_time": True,
        #  #"initial": "00:00:01",
        #  "configured": True
        #},
        #
        #self.getPostfix(self.morning_end_time) : {
        #  "name" :  self.getNameFromEntity(self.morning_end_time),
        #  "has_date": False,
        #  "has_time": True,
        #  #"initial": "13:00:00",
        #  "configured": True
        #},
        #
        #self.getPostfix(self.afternoon_start_time) : {
        #  "name" :  self.getNameFromEntity(self.afternoon_start_time),
        #  "has_date": False,
        #  "has_time": True,
        #  #"initial": "13:00:00",
        #  "configured": True
        #},
        #
        #self.getPostfix(self.afternoon_end_time) : {
        #  "name" :  self.getNameFromEntity(self.afternoon_end_time),
        #  "has_date": False,
        #  "has_time": True,
        #  #"initial": "23:59:00",
        #  "configured": True
        #},

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
          "name" : self.getNameFromEntity(self.room_heating_override),
          "initial": "off",
          "configured": self.cfg_temp_control
        }
      }

      self.sensor_list += [
        self.get_occupancy_ratio_sensor_config('1x'),
        self.get_occupancy_ratio_sensor_config('2x')
      ]

      self.group_dict |= {
        self.getPostfix(self.occupancy_group) : {
          "name": self.getNameFromEntity(self.occupancy_group),
          "entities": [self.room_occupancy] + [self.motion_group] + self.all_motion_sensors + [self.automation_occupancy['id']],
          'configured': self.cfg_occupancy,
        }
      }

      self.group_dict |= {
        self.getPostfix(self.motion_group) : {
          "name": self.getNameFromEntity(self.motion_group),
          "entities": self.all_motion_sensors,
          'configured': True,
        }
      }

      self.group_dict |= {
        self.getPostfix(self.light_group): {
          "name" : self.getNameFromEntity(self.light_group),
          "entities": self.lights,
          'configured': True,
        }
      }

      self.group_dict |= {
        self.getPostfix(self.window_group): {
          "name" : self.getNameFromEntity(self.window_group),
          "entities": self.windows,
          'configured': len(self.windows) > 0,
        }
      }

      self.group_dict |= {
        self.getPostfix(self.timeout_window_group): {
          "name" : self.getNameFromEntity(self.timeout_window_group),
          "entities": self.timeout_windows,
          'configured': True,
        }
      }

      self.group_dict |= {
        self.getPostfix(self.curtain_group): {
          "name" : self.getNameFromEntity(self.curtain_group),
          "entities": self.curtains,
          'configured': True,
        }
      }


      # Occupancy Override
      self.timer_dict |= {
        self.getPostfix(self.occupancy_override_timer_entity): {
          "name" : self.getNameFromEntity(self.occupancy_override_timer_entity),
          'duration': self.occupancy_override_default_timeout,
          'configured': self.cfg_occupancy_override,
        }
      }

      self.input_boolean_dict |= {
        self.getPostfix(self.occupancy_override_entity): {
          "name" : self.getNameFromEntity(self.occupancy_override_entity),
          #"initial": "off",
          "icon": "mdi:timer-sand",
          "configured": self.cfg_occupancy_override,
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
        self.tail_card_list.append(self.hccl.getEntityCard(entity=self.gui_ctl_group, card_name='Automation Control'))


  def get_battery_entity(self):
    declarations = battery_entity_builder.build_room_battery_entities(
      self.room_entity,
      self.template_list,
      self.getPostfix,
      self.getNameFromEntity,
    )
    self.room_battery_entity_list = declarations["room_battery_entity_list"]
    self.room_battery_entity = declarations["room_battery_entity"]
    self.group_dict |= declarations["group_dict_additions"]
    self.room_min_battery_value_entity = declarations["room_min_battery_value_entity"]
    self.sensor_list += declarations["sensor_list_additions"]
    self.room_low_battery_entity = declarations["room_low_battery_entity"]
    self.template_list += declarations["template_list_additions"]


  def get_unavailable_entity(self):
    self.added_device_entities = unavailable_entity_builder.collect_added_device_entities(
      self.template_list,
      self.binary_sensor_list,
      self.switch_list,
      self.cover_list,
      self.lock_list,
      self.event_list,
      self.light_list,
    )

    # debug
    #yaml_string = yaml.dump(self.added_device_entities, sort_keys=False)
    #print(yaml_string)
    # Getting Unavailable Devices
    self.unavailable_entity  = "binary_sensor." + self.room_entity + "_unavailable_entities"

    self.template_list += [
      {
        "binary_sensor": [
          {
            "name": self.getNameFromEntity(self.unavailable_entity),
            "state":
                "{% set added_device_entities =  " + str(self.added_device_entities) + " %}" + \
                "{% set ns = namespace() %}" + \
                "{% set ns.num_unavail_devices = 0 %}" + \
                "{% for device in added_device_entities %}" + \
                "   {% if states(device) in ['unavailable', 'unknown', 'none'] %}" + \
                "      {% set ns.num_unavail_devices = ns.num_unavail_devices + 1 %}" + \
                "   {% endif %}" + \
                "{% endfor %}" + \
                "{% if ns.num_unavail_devices > 0%}" + \
                "  on  "     + \
                "{% else %}" + \
                "  off "     + \
                "{% endif %}",
            "attributes":
              {"value":
                      "{% set added_device_entities =  " + str(self.added_device_entities) + " %}" + \
                      "{% set ns = namespace() %}" + \
                      "{% set ns.unavail_devices = '' %}" + \
                      "{% for device in added_device_entities %}" + \
                      "   {% if states(device) in ['unavailable', 'unknown', 'none'] %}" + \
                      "   {% set ns.unavail_devices = ns.unavail_devices + '\n' +device %}" + \
                      " {% endif %}" + \
                      "{% endfor %}" + \
                      "{{ns.unavail_devices}}"
                #      "{{ expand(added_device_entities) | " + \
                #      "selectattr('state', 'in', ['unavailable', 'unknown', 'none']) | " + \
                #      "map(attribute='entity_id') | " + \
                #      "list | join(',\n')}}"
              },
          },
        ],
        "configured": True,
      }
    ]

  def get_script_dict(self):
    pass



################################################################################################################################################################################
###################################       LOVELACE START        ################################################################################################################
################################################################################################################################################################################

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
      card_type = dashboard_entity_cards.infer_entity_card_type(entity)

    if entity_name is None:
      entity_name = self.getNameFromEntity(entity)

    #if card_name is None:
    #  # Remove room name from entity name to get card name
    #  # "Ceiling Light" = Remove "Living Room" from "Living Room Ceiling Light"
    #  card_name = re.sub(self.room_name, "", entity_name)
    #  #if self.chinese == True:


    #if entity_name_translation != None:
    #  entity_name_translation =

    card_name = '' if card_name is None else card_name
    #if self.dashboard_language is 'Chinese':
    #  card_name = translator.translate(card_name)
    #  print (card_name)
    card_icon = '' if card_icon is None else card_icon

    # light
    if card_type == 'custom:mushroom-light-card':
      card = dashboard_entity_cards.light_card(entity, card_name, card_icon, card_type=card_type)

    # cover
    elif card_type == 'custom:mushroom-cover-card':
      card = dashboard_entity_cards.cover_card(entity, card_name, card_icon, card_type=card_type)

    # climate
    elif card_type == 'custom:mushroom-climate-card':
      card = dashboard_entity_cards.climate_card(entity, card_name, card_icon, card_type=card_type)

    # media_player card
    # tap - toggle/navigate/more-info
    elif card_type == 'custom:mushroom-media-player-card':
      card = dashboard_entity_cards.media_player_card(entity, card_name, card_icon, card_type=card_type)
    # group card
    elif card_type == 'custom:auto-entities':
      card = dashboard_entity_cards.group_card(entity, card_name, card_type=card_type)

    # sensor
    elif card_type == 'sensor':
      if simple is True:
        card = dashboard_entity_cards.simple_sensor_card(entity, card_name, card_icon, card_type=card_type)
      else: # complex minigraph temperature sensor card from
      # https://bbs.hassbian.com/forum.php?mod=redirect&goto=findpost&ptid=22509&pid=550976
        card = dashboard_entity_cards.complex_sensor_card(entity, card_name)

    # entity card
    # binary_sensor    - tap to more-info
    # switch           - tap to toggle
    # input boolean
    elif card_type == 'custom:mushroom-entity-card':
      card = dashboard_entity_cards.entity_card(entity, card_name, card_icon, card_type=card_type)

    # entities card
    # input_timer
    elif card_type == 'entities':
      card = dashboard_entity_cards.entities_card(entity, card_name, card_type=card_type)

    # schduler card
    elif card_type == 'custom:scheduler-card':
      card = dashboard_entity_cards.scheduler_card(entity, card_type=card_type)

    # timer card
    elif card_type == 'custom:flipdown-timer-card':
      card = dashboard_entity_cards.flipdown_timer_card(entity, card_name, card_icon, card_type=card_type)

    # input_number
    # number
    elif card_type == 'custom:mushroom-number-card':
      card = dashboard_entity_cards.number_card(entity, card_name, card_icon, card_type=card_type)

    # input_select
    elif card_type == 'custom:mushroom-select-card':
      card = {
        "type": card_type,
        "fill_container": True,
        "tap_action":      {"action": "more-info"},
        "icon_tap_action": {"action": "more-info"},
        "icon": "mdi:brightness-4" if card_icon is None else card_icon,
        "secondary_info": state if secondary_info is None else secondary_info,
        "name": card_name,
        "entity": entity
      }


    # input_select
    elif card_type == '页眉卡片1':
      card = dashboard_entity_cards.header_chips_card()
    return card

  def getCardMod(self, style='background_color_select', card_type=None, color=None, support_dark_mode=True):
    return dashboard_card_mod.build_card_mod(style, card_type, color, support_dark_mode)

  def getColor(self, color):
    return dashboard_colors.get_color(color)

  def getCardModColor(self, color):
    return self.getCardMod('background_color_select', color=color)

  def getTemplateCard(self, icon='mdi:head-alert-outline',
                            icon_color='blue',
                            primary=None,
                            secondary=None,
                            condition_entity=None,
                            tap_entity=None,
                            condition_state='on',
                            condition_state_not=None,
                            condition_states=None,
                            tap_action='more-info',
                            theme='default'):

    self.dashboard_view_path = "/" + self.dashboard_root + "/" + self.room_navi_path

    entity = dashboard_entity_cards.resolve_template_card_entity(
      tap_entity=tap_entity,
      condition_entity=condition_entity,
    )

    tap_action_dict = dashboard_entity_cards.template_card_tap_action(
      tap_action,
      self.dashboard_view_path,
    )
    template_card = dashboard_entity_cards.template_card(
      icon=icon,
      icon_color=icon_color,
      primary=primary,
      secondary=secondary,
      entity=entity,
      tap_action_dict=tap_action_dict,
      theme=theme,
    )

    if condition_entity == None:
      condition_card = template_card
    else:
      condition_card = {}

      # Use single condition
      if condition_states is None:
        condition_card = dashboard_entity_cards.conditional_template_card(
          template_card,
          condition_entity,
          condition_state=condition_state,
          condition_state_not=condition_state_not,
        )

      else: # Use multiple conditions
        condition_card = {
          "type": "custom:state-switch",
          "entity": condition_entity,
          states: {}}
        for state in condition_states:
          condition_card['states'] |= { state : template_card}

    if theme == 'ios':
      #condition_card |= self.getCardMod(style='ios16_toggle',color=("{% set entity = '"+entity+"' %}\n" + icon_color))
      condition_card |= dashboard_entity_cards.template_card_ios_mod(entity, icon_color)

    return condition_card


################################################################################################################################################################################
###################################       LOVELACE END          ################################################################################################################
################################################################################################################################################################################


  # Lighting Automations
  def get_automation_declarations(self):
    self.gen_motion_light_automations()
    self.gen_temp_control_automations()
    self.gen_button_automations()
    self.gen_media_automations()
    self.gen_camera_automations()
    self.gen_wall_button_single_automations()
    self.gen_wall_button_double_automations()
    self.gen_adaptive_lighting_automations()
    self.gen_mirror_light_automations()
    self.gen_occupancy_automations()
    self.gen_tv_automations()
    self.gen_room_specific_automations()
    self.gen_window_automations()

    automation_helpers.assign_automation_ids(self.automation_list, self.getIDFromAlias)


  def gen_room_specific_automations(self):
    pass


  # Generate user control group including automations and other controls.
  def implement_group_intf_for_gui(self):

    # Add light control entities to the control group based on the existence of different types of lights in the room
    self.gui_ctl_entity_list += gui_control_group.scene_control_entities(
      self.ceiling_lights,
      self.lamps,
      self.leds,
      self.curtains,
      self.ceiling_light_control_when,
      self.lamp_control_when,
      self.led_control_when,
      self.curtain_control_when,
    )

    # Generate automations group with disabled automation removed
    self.gui_ctl_entity_list += gui_control_group.automation_entities(self.entity_declarations['automation'])
    self.gui_ctl_entity_list += gui_control_group.extra_control_entities(
      self.wall_switches,
      self.decouple_wall_switches,
      self.cfg_adaptive_lighting,
      self.al_light_list,
      self.getEntityFromName,
      self.time_controls,
      self.light_sensor_controls,
      self.room_battery_entity,
      self.manual_added_automations,
      self.windows,
      self.window_group,
    )

    gui_control_group.merge_auto_group_declaration(
      self.entity_declarations,
      self.cfg_group_auto,
      lambda: self.gui_ctl_group,
      lambda: self.gui_ctl_entity_list,
      self.getPostfix,
      self.getNameFromEntity,
    )


  def implement_entity_intf(self):
      self.entity_declarations |= entity_interface_defaults.build_entity_declarations(
        self.al_light_list,
        self.automation_list,
        self.input_select_dict,
        self.input_boolean_dict,
        self.input_datetime_dict,
        self.input_number_dict,
        self.sensor_list,
        self.timer_dict,
        self.button_list,
        self.switch_list,
        self.cover_list,
        self.climate_list,
        self.template_list,
        self.binary_sensor_list,
        self.event_list,
        self.lock_list,
        self.light_list,
        self.group_dict,
      )

  def gen_motion_light_automations(self):
    self.automation_curtain_states = {"alias":"ZL-" + self.automation_room_name + "Curtain States When No Person Present" + "-" + self.room_name }
    self.automation_curtain_states['id'] = self.getIDFromAlias(self.automation_curtain_states['alias'])
    self.automation_list += [self.automation_curtain_states | {
        "configured" : self.cfg_motion_light,
        "trigger" :
        [
          { "platform": "state",
            "entity_id": self.room_occupancy,
            "to": "Outside",
            "for": "00:03:00",
          }
        ] + self.get_time_pattern_trigger(minutes=10),
        'conditions': [self.continueIf(self.room_occupancy, 'Outside', lastFor="00:03:00")],
        "action": [
          motion_light_automation_helpers.curtain_scene_choose(
            self.condition_list_is,
            self.callSceneService,
            automation_helpers.do_nothing_service,
          )
        ]
    }]

    self.automation_lights_on = {"alias":"ZL-" + self.automation_room_name + "Lights On If Entering to Room" + "-" + self.room_name }
    self.automation_lights_on['id'] = self.getIDFromAlias(self.automation_lights_on['alias'])
    self.automation_list += [self.automation_lights_on | {
        # Lights on automation are initially off until it is automatically turned on when no present detected
        "configured" : self.cfg_motion_light,
        "trigger" :
        {
            "entity_id": self.entrance_motion_sensors,
            "platform": "state",
            "to": "on",
            'from': 'off',
        },
        "action": [
          automation_helpers.automation_turn_off(self.automation_lights_on['id'], stop_actions=False),
          self.setNewSceneState("Idle"),
          motion_light_automation_helpers.light_scene_choose(
            self.condition_list_is,
            self.callSceneService,
            automation_helpers.do_nothing_service,
          ),
          # Trigger curtain states as well
          automation_helpers.automation_trigger(self.automation_curtain_states['id']),
        ]
    }]


    self.automation_lights_off = {"alias":"ZL-" + self.automation_room_name + "Lights Off If No Person" + "-" + self.room_name}
    self.automation_lights_off['id'] = self.getIDFromAlias(self.automation_lights_off['alias'])
    self.automation_list += [self.automation_lights_off | {
        "configured": self.cfg_motion_light,
        "trigger": [
          { "platform": "state",
            "entity_id": self.room_occupancy,
            "to": "Outside"
          }
        ] + self.get_time_pattern_trigger(),
        "condition": motion_light_automation_helpers.lights_off_conditions(
          self.room_occupancy,
          self.motion_group,
          self.room_type,
        ),
        "action": {
          'parallel': motion_light_automation_helpers.lights_off_parallel_actions(
            self.automation_lights_on['id'],
            self.tvs,
            self.extractor,
            self.set,
            self.setNewSceneState,
            self.callSceneService,
          )
        }
      }
    ]

    self.automation_list += [
      {
        "alias" : "ZL-" + self.automation_room_name + "Disable Entering Lights-on Automation If any People are in the Room" + "-" + self.room_name,
        "configured": self.cfg_motion_light,
        "trigger": [
          { "platform": "state",
            "entity_id": self.room_occupancy,
            "to": ["Just Entered", "In Sleep", "Stayed Inside"]
          }
        ],
        "action": motion_light_automation_helpers.disable_entering_lights_on_actions(
          self.automation_lights_on['id'],
          automation_helpers.automation_turn_off,
        )
      }
    ]

    self.automation_list += [
      {
        "alias" : "ZL-" + self.automation_room_name + "Turn on LED if Walking In the Dark" + "-" + self.room_name,
        "configured": self.cfg_motion_light and self.cfg_motion_bed_led,
        "mode": "single",
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
        ],
        "action": motion_light_automation_helpers.walking_in_dark_led_actions(
          self.room_entity,
          self.leds,
          self.ceiling_lights,
          self.lamps,
          self.non_bed_motion_sensors,
          self.set,
          self.callSceneService,
        )
      }
    ]


  def gen_tv_automations(self):
    self.automation_list += [
      tv_automation_helpers.reset_picture_mode_automation(
        self.automation_room_name,
        self.room_name,
        self.tvs,
        self.set,
      )
    ]

  def gen_window_automations(self):
    self.add_window_open_notification_when_leaving_zone_automations()
    self.add_window_open_notification_when_going_to_sleep_automations()
    self.add_window_open_notification_when_timeout_automations()

  def add_window_open_notification_when_leaving_zone_automations(self):
    self.automation_list += [{
      "alias": "ZN-" + self.automation_room_name + "Notify Window Left Open When Tai is Leaving Zone" + "-" + self.room_name,
      "configured": len(self.windows) > 0,
      "trigger": [
        {
          "platform": "zone",
          "entity_id": "device_tracker.tais_iphone_13",
          "zone": "zone.home",
          "event": "leave"
        }
      ],
      "condition": [
        window_automation_helpers.window_is_open_condition(self.window_group)
      ],
      "action": [
        window_automation_helpers.notify_windows_open_action(
          self.room_name + " windows or locks are left open. But you have left home. Is that ok?",
          notify_tai="yes",
        )
      ]
    }]

    self.automation_list += [{
      "alias": "ZN-" + self.automation_room_name + "Notify Window Left Open When Ke is Leaving Zone" + "-" + self.room_name,
      "configured": len(self.windows) > 0,
      "trigger": [
        {
          "platform": "zone",
          "entity_id": "device_tracker.kes_iphone_14_pro_max",
          "zone": "zone.home",
          "event": "leave"
        }
      ],
      "condition": [
        window_automation_helpers.window_is_open_condition(self.window_group)
      ],
      "action": [
        window_automation_helpers.notify_windows_open_action(
          self.room_name + " windows or locks are left open. But you have left home. Is that ok?",
          notify_ke="yes",
        )
      ]
    }]


  def add_window_open_notification_when_going_to_sleep_automations(self):
    self.automation_list += [{
      "alias": "ZN-" + self.automation_room_name + "Notify Window Left Open in Bedtime " + "-" + self.room_name,
      "configured": len(self.windows) > 0,
      "trigger": [
        {
          "platform": "time",
          "at": [
                  "21:00:00",
                  "22:00:00",
                  "23:00:00",
                  "00:00:00",
                  "01:00:00",
                  "02:00:00",
                  "03:00:00"
                ]
        }
      ],
      "condition": [
        window_automation_helpers.window_is_open_condition(self.window_group)
      ],
      "action": [
        window_automation_helpers.notify_windows_open_action(
          self.room_name + " windows or locks are left open. But it's almost bedtime time. Is that ok?",
          notify_tai="yes",
          notify_ke="yes",
          **window_automation_helpers.tenant_notify_flags_for_room(self.room_entity),
        )
      ]
    }]


  def add_window_open_notification_when_timeout_automations(self):
    pass
   #   self.automation_list += [{
   #     "alias": "ZN-" + self.automation_room_name + "Notify Window Left Open After Timeout"  + "-" + self.room_name,
   #     "configured": True,
   #     "trigger": [
   #       {
   #         "platform": "template",
   #         "value_template": "{{(now().timestamp() - states." + self.timeout_window_group + ".last_changed.timestamp()) > state_attr('input_datetime.qianjie_windows_open_timeout', 'timestamp')}}\n"
   #       }
   #     ],
   #     "condition": [
   #       {
   #         "condition": "state",
   #         "entity_id": self.timeout_window_group,
   #         "state": "on"
   #       }
   #     ],
   #     "action": [
   #       {
   #         "service": "script.notify_alexa_speakers_and_phones",
   #         "data": {
   #           "tts_message": self.room_name + " windows are left open for a while. Is that ok?",
   #           "notify_tai": "yes",
   #           "notify_ke": "yes"
   #         } | ({
   #           "notify_guest_room_tenant": "yes",
   #           "notify_en_suite_room_tenant": "yes"
   #         } if self.room_entity == 'kitchen' else {})
   #       }
   #     ],
   #     "mode": "single"
   #   }]


  def gen_temp_control_automations(self):
    self.automation_heating_on = {"alias":"ZH-" + self.automation_room_name + "Heating Schedule On If Staying In the Room" + "-" + self.room_name}
    self.automation_heating_on['id'] = self.getIDFromAlias(self.automation_heating_on['alias'])
    self.automation_list += [self.automation_heating_on | {
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
            "then": self.set('heating', 'on')
          }
        ]
      }
    ]

    self.automation_heating_off = {"alias":"ZH-"+self.automation_room_name+"Heating Schedule Off If People Left the Room"+"-"+self.room_name}
    self.automation_heating_off['id'] = self.getIDFromAlias(self.automation_heating_off['alias'])
    self.automation_list += [self.automation_heating_off | {
        "configured": self.cfg_temp_control and self.cfg_occupancy,
        "trigger": [
          { "platform": "state",
            "entity_id": self.room_occupancy,
            "to": "Outside"
          }
        ] + self.get_time_pattern_trigger(),
        "action":
            [
              { "condition": "state",
                "entity_id": self.room_occupancy,
                "state": "Outside"
              },
              self.set(self.demisters, 'off'),
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
              self.set('heating', 'off')
            ]
      }
    ]

    self.automation_list += [{
        "alias" : "ZH-" + self.automation_room_name + "Demister On When Taking Shower" + "-" + self.room_name,
        "configured": self.demisters != [] and self.shower_sensors != [],
        "trigger": [
          { "platform": "state",
            "entity_id": self.shower_sensors,
            "to": "on",
          }
        ],
        "action": [
          { "condition": "state",
            "entity_id": self.room_occupancy,
            "state": ["Just Entered", "In Sleep", "Stayed Inside"],
          },
          self.set(self.demisters, 'on'),
        ]
      }
    ]

    self.automation_list += [
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
              { "delay": {"hours": 4}
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
    self.automation_list += [
      offline_device_automation_helpers.offline_device_notification_automation(
        self.automation_room_name,
        self.room_name,
        device_type,
        offline_device,
        tts_message,
        gateway_power_switch,
        self.set,
      )
    ]

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
  TOGGLE_ALL_LIGHTS         = 'TOGGLE_ALL_LIGHTS'
  TOGGLE_LAMP_0             = 'TOGGLE_LAMP_0'
  INCREMENT_LAMP_0          = 'INCREMENT_LAMP_0'
  DECREMENT_LAMP_0          = 'DECREMENT_LAMP_0'
  CYCLE_LAMP_0              = 'CYCLE_LAMP_0'
  TOGGLE_LAMP_1             = 'TOGGLE_LAMP_1'
  INCREMENT_LAMP_1          = 'INCREMENT_LAMP_1'
  DECREMENT_LAMP_1          = 'DECREMENT_LAMP_1'
  CYCLE_LAMP_1              = 'CYCLE_LAMP_1'
  TOGGLE_LAMP_2             = 'TOGGLE_LAMP_2'
  INCREMENT_LAMP_2          = 'INCREMENT_LAMP_2'
  DECREMENT_LAMP_2          = 'DECREMENT_LAMP_2'
  CYCLE_LAMP_2              = 'CYCLE_LAMP_2'
  TOGGLE_CEILING_LIGHTS     = 'TOGGLE_CEILING_LIGHTS'
  INCREMENT_CEILING_LIGHTS  = 'INCREMENT_CEILING_LIGHTS'
  DECREMENT_CEILING_LIGHTS  = 'DECREMENT_CEILING_LIGHTS'
  CYCLE_CEILING_LIGHTS      = 'CYCLE_CEILING_LIGHTS'
  TOGGLE_SCREEN_LED         = 'TOGGLE_SCREEN_LED'
  TOGGLE_LEDS               = 'TOGGLE_LEDS'
  CYCLE_LEDS                = 'CYCLE_LEDS'
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
  TOGGLE_DEMISTER           = 'TOGGLE_DEMISTER'

  def get_trigger_action_list(self):
    return {
      "choose":
        ([{ "conditions": {"condition": "trigger","id": self.CYCLE_SCENES            }, "sequence": {"choose": self.get_scene_state_machine(), "default": self.setNewSceneState("All White")}}])  + \
        ([{ "conditions": {"condition": "trigger","id": self.DO_NOTHING              }, "sequence": [automation_helpers.do_nothing_service()]}])                                                   + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_AL_SLEEP_MODE    }, "sequence": [self.set(self.al_sleep_mode, 'toggle'                  )]}]                                              ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_CURTAINS         }, "sequence": [self.set(self.curtains,      'toggle'                  )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_CURTAIN_0        }, "sequence": [self.set(self.curtains[0],   'toggle'                  )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_CURTAIN_1        }, "sequence": [self.set(self.curtains[1],   'toggle'                  )]}] if len(self.curtains)       >= 2 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_CURTAINS      }, "sequence": [self.set(self.curtains,      'increment'               )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_CURTAINS      }, "sequence": [self.set(self.curtains,      'decrement'               )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_CURTAIN_0     }, "sequence": [self.set(self.curtains[0],   'increment'               )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_CURTAIN_0     }, "sequence": [self.set(self.curtains[0],   'decrement'               )]}] if len(self.curtains)       >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_CURTAIN_1     }, "sequence": [self.set(self.curtains[1],   'increment'               )]}] if len(self.curtains)       >= 2 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_CURTAIN_1     }, "sequence": [self.set(self.curtains[1],   'decrement'               )]}] if len(self.curtains)       >= 2 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_ALL_LIGHTS       }, "sequence": [self.set(self.lights,        'toggle'                  )]}] if len(self.lights)         >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_LAMP_0           }, "sequence": [self.set(self.lamps[0],      'toggle'                  )]}] if len(self.lamps)          >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_LAMP_0        }, "sequence": [self.set(self.lamps[0],      'increment', step_value=34)]}] if len(self.lamps)          >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_LAMP_0        }, "sequence": [self.set(self.lamps[0],      'decrement', step_value=34)]}] if len(self.lamps)          >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.CYCLE_LAMP_0            }, "sequence": [self.set(self.lamps[0],      'cycle'                   )]}] if len(self.lamps)          >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_LAMP_1           }, "sequence": [self.set(self.lamps[1],      'toggle'                  )]}] if len(self.lamps)          >= 2 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_LAMP_1        }, "sequence": [self.set(self.lamps[1],      'increment', step_value=34)]}] if len(self.lamps)          >= 2 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_LAMP_1        }, "sequence": [self.set(self.lamps[1],      'decrement', step_value=34)]}] if len(self.lamps)          >= 2 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.CYCLE_LAMP_1            }, "sequence": [self.set(self.lamps[1],      'cycle'                   )]}] if len(self.lamps)          >= 2 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_LAMP_2           }, "sequence": [self.set(self.lamps[2],      'toggle'                  )]}] if len(self.lamps)          >= 3 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_LAMP_2        }, "sequence": [self.set(self.lamps[2],      'increment', step_value=34)]}] if len(self.lamps)          >= 3 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_LAMP_2        }, "sequence": [self.set(self.lamps[2],      'decrement', step_value=34)]}] if len(self.lamps)          >= 3 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.CYCLE_LAMP_2            }, "sequence": [self.set(self.lamps[2],      'cycle'                   )]}] if len(self.lamps)          >= 3 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_CEILING_LIGHTS   }, "sequence": [self.set(self.ceiling_lights,'toggle'                  )]}] if len(self.ceiling_lights) >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_CEILING_LIGHTS}, "sequence": [self.set(self.ceiling_lights,'increment', step_value=34)]}] if len(self.ceiling_lights) >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_CEILING_LIGHTS}, "sequence": [self.set(self.ceiling_lights,'decrement', step_value=34)]}] if len(self.ceiling_lights) >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.CYCLE_CEILING_LIGHTS    }, "sequence": [self.set(self.ceiling_lights,'cycle'                   )]}] if len(self.ceiling_lights) >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_SCREEN_LED       }, "sequence": [self.set(self.screen_leds,   'toggle'                  )]}] if len(self.screen_leds)    >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_LEDS             }, "sequence": [self.set(self.leds,          'toggle'                  )]}] if len(self.leds)           >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.CYCLE_LEDS              }, "sequence": [self.set(self.leds,          'cycle'                   )]}] if len(self.leds)           >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_LEDS          }, "sequence": [self.set(self.leds,          'increment', step_value=34)]}] if len(self.leds)           >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_LEDS          }, "sequence": [self.set(self.leds,          'decrement', step_value=34)]}] if len(self.leds)           >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_TV_POWER         }, "sequence": [self.set(self.tvs,           'power_toggle'            )]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.CYCLE_TV_BRIGHTNESS     }, "sequence": [self.set(self.tvs,            tv_brightness='cycle'    )]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_TV_BRIGHTNESS }, "sequence": [self.set(self.tvs,            tv_brightness='increment')]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_TV_BRIGHTNESS }, "sequence": [self.set(self.tvs,            tv_brightness='decrement')]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_TV_VOLUME     }, "sequence": [self.set('tv_volumne',        'increment', step_value=3)]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_TV_VOLUME     }, "sequence": [self.set('tv_volumne',        'decrement', step_value=3)]}] if len(self.tvs)            >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_HEATING          }, "sequence": [self.set('heating',           'toggle'                 )]}] if len(self.thermostat)     >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.INCREMENT_HEATING       }, "sequence": [self.set('heating',           'increment', step_value=1)]}] if len(self.thermostat)     >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.DECREMENT_HEATING       }, "sequence": [self.set('heating',           'decrement', step_value=1)]}] if len(self.thermostat)     >= 1 else []     ) + \
        ([{ "conditions": {"condition": "trigger","id": self.TOGGLE_DEMISTER         }, "sequence": [self.set(self.demisters,      'toggle'                 )]}] if len(self.demisters)      >= 1 else []     ) + \
        ([])
          }

  def gen_button_automations(self):
    self.automation_list += [{
        "alias" : "ZLB-" + self.automation_room_name + "Single Button Control" + "-" + self.room_name,
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

    self.automation_list += [{
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
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": 'button_3_single',                                      "id": self.TOGGLE_HEATING         },
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ['button_3_double','button_3_hold'],                    "id": self.DO_NOTHING},
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_clockwise_after_toggling_button_3",
          #                                                                    "knob_clockwise_after_toggling_button_3_and_knob"],    "id": self.INCREMENT_HEATING},
          #{"platform":"state","entity_id": self.eight_key_knob_buttons,"to": ["knob_anticlockwise_after_toggling_button_3",
          #                                                                    "knob_anticlockwise_after_toggling_button_3_and_knob"],"id": self.DECREMENT_HEATING},
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



    self.automation_list += [{
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

    self.automation_list += [{
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


    self.automation_list += [{
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
            ]
          }
        ]
    }]


  def gen_media_automations(self):
    self.automation_list += [
      media_automation_helpers.sonos_pause_after_people_left_automation(
        self.automation_room_name,
        self.room_name,
        self.room_entity,
        self.room_occupancy,
        self.media_players,
        self.get_time_pattern_trigger(),
        self.set,
      )
    ]


  def gen_camera_automations(self):
    if self.room_entity == 'kitchen':
      self.automation_list += camera_automation_helpers.kitchen_camera_automations(
        self.automation_room_name,
        self.room_name,
        self.room_occupancy,
        self.get_time_pattern_trigger(),
      )


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

    self.automation_list += [
      button_automation_helpers.button_toggle_automation(
        self.automation_room_name,
        self.room_name,
        self.cfg_remote_light,
        switch_type,
        button_state_name,
        device_name,
        button_list,
        button_state_list,
        device_list,
        self.set,
      )
    ]


  def gen_flex_wall_switch_automations(self, flex_wall_switch_index, flex_wall_switch_entity):
    self.automation_list += [
      button_automation_helpers.flex_wall_switch_restore_automation(
        self.automation_room_name,
        self.room_name,
        flex_wall_switch_index,
        flex_wall_switch_entity,
        self.set,
      )
    ]

  def gen_wall_button_double_automations(self):
    self.automation_list += [
      button_automation_helpers.wall_button_double_leave_room_automation(
        self.automation_room_name,
        self.room_name,
        self.cfg_remote_light,
        self.wall_buttons,
        self.automation_lights_off['id'],
        self.automation_heating_off['id'],
        self.room_occupancy,
      )
    ]
  def gen_adaptive_lighting_automations(self):
    pass
  # Use scheduler card instead

  #  self.automation_list += [
  #    {
  #      "alias":"ZL-" + self.automation_room_name + "Turns On Sleep Mode In The Night" + "-" + self.room_name,
  #      "configured": self.cfg_adaptive_lighting,
  #      "trigger": [
  #        {
  #          "platform": "time",
  #          "at": self.start_of_sleep_time
  #        }
  #      ],
  #      "action": [self.set(self.al_sleep_mode, 'on')]
  #    }
  #  ]
  #
  #  self.automation_list += [
  #    {
  #      "alias":"ZL-" + self.automation_room_name + "Turns Off Sleep Mode In The Morning" + "-" + self.room_name,
  #      "configured": self.cfg_adaptive_lighting,
  #      "trigger": [
  #        {
  #          "platform": "time",
  #          "at": self.end_of_sleep_time
  #        }
  #      ],
  #      "action": [self.set(self.al_sleep_mode, 'off')]
  #    }
  #  ]


  def gen_mirror_light_automations(self):
    self.automation_list += [
      mirror_automation_helpers.mirror_sensor_on_automation(
        self.automation_room_name,
        self.room_name,
        self.mirror_sensors,
        self.ceiling_lights,
      )
    ]

    self.automation_list += [
      mirror_automation_helpers.mirror_sensor_off_automation(
        self.automation_room_name,
        self.room_name,
        self.mirror_sensors,
        self.room_occupancy,
        self.al_adapt_brightness,
      )
    ]


  def select_occupancy_state(self, occupancy_state):
    return automation_helpers.select_input_select_option(self.room_occupancy, occupancy_state)

  def state_duration_template_condition(self, entity_id, state, seconds, op=">="):
    return automation_helpers.state_duration_template_condition(entity_id, state, seconds, op=op)

  def get_occupancy_state_machine_actions(self):
    return occupancy_state_machine.get_occupancy_state_machine_actions(
      room_occupancy=self.room_occupancy,
      motion_group=self.motion_group,
      sleep_time=self.sleep_time,
      set_to_outside_when_no_motion=self.set_to_outside_when_no_motion,
      entered_to_inside_timeout=self.entered_to_inside_timeout,
      inside_to_sleep_timeout=self.inside_to_sleep_timeout,
      inside_to_outside_timeout=self.inside_to_outside_timeout,
      sleep_to_outside_timeout=self.sleep_to_outside_timeout
    )
  def gen_occupancy_automations(self):

    self.automation_occupancy_update = {"alias":"ZOc-" + self.automation_room_name + "Occupancy Update" + "-" + self.room_name}
    self.automation_occupancy_update['id'] = self.getIDFromAlias(self.automation_occupancy_update['alias'])
    self.automation_list += [self.automation_occupancy_update | {
        "configured": self.cfg_occupancy,
        "trigger": occupancy_automation_helpers.occupancy_update_triggers(
          self.motion_group,
          self.entered_to_inside_timeout,
          self.inside_to_sleep_timeout,
          self.inside_to_outside_timeout,
          self.sleep_to_outside_timeout,
          self.get_time_pattern_trigger(minutes=3),
        ),
        "action": self.get_occupancy_state_machine_actions()
      }
    ]

    self.automation_list += [
      occupancy_automation_helpers.occupancy_override_to_timer_automation(
        self.automation_room_name,
        self.room_name,
        self.cfg_occupancy_override,
        self.occupancy_override_entity,
        self.occupancy_override_timer_entity,
        self.room_occupancy,
        self.automation_occupancy_update['id'],
        self.set,
      )
    ]


    self.automation_list += [
      occupancy_automation_helpers.occupancy_override_from_timer_automation(
        self.automation_room_name,
        self.room_name,
        self.cfg_occupancy_override,
        self.occupancy_override_entity,
        self.occupancy_override_timer_entity,
        self.get_time_pattern_trigger(minutes=10),
      )
    ]


      #    self.automation_list += [{
      #        "alias":"ZoC-N-" + self.automation_room_name + "History Stat Reload On Timeout" + "-" + self.room_name,
      #        "configured": self.cfg_occupancy,
      #        "trigger": self.get_time_pattern_trigger(),
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



  # Create service call for turn on/off entities
  def set(self, entity_list, state=None, light_brightness=None, tv_brightness=None, inc_unavail=True, step_value=51):
    assert state in ['on', 'off', 'toggle', 'cycle', 'increment', 'decrement', 'power_toggle', 'single_device_volume_inc', 'single_device_volume_dec', 'press', None], "State has to be one of legal states, but it is " + state
    #assert type(entity_list) is list , "entity_list has to be a list, but it is " + entity_list

    if state in ['press']:
      action_service = {"service" : "button.press",
                        "target":{"entity_id" : entity_list},
                        }

    if state in ['increment', 'decrement']:
      step_value = -1 * step_value if state == 'decrement' else step_value

    is_light_list = service_action_helpers.is_light_entity_list(entity_list)

    if state == 'power_toggle':
      action_service = {#'alias': f'toggle {str(entity_list)}',
                        "if":   self.continueIf(entity_list, "off"),
                        "then": self.set(entity_list, 'on'),
                        "else": self.set(entity_list, 'off')}
    ##############################################
    # TV/Media players volumnes and brightness
    ##############################################
    elif tv_brightness != None:
      if tv_brightness in ['cycle', 'increment', 'decrement']:
        action_service = tv_automation_helpers.picture_mode_step_action(
          tv_brightness,
          self.tv_picture_mode,
          self.tvs,
          self.continueIf,
          self.set,
        )
      elif tv_brightness in [1,2,3,4,5,6,7,8,9]:
        action_service = tv_automation_helpers.set_picture_mode_action(
          entity_list,
          self.tv_picture_mode,
          tv_brightness,
        )
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
                            "then": self.set(self.tv_soundbars, single_device_state, step_value=step_value),
                            "else": self.set(self.tvs,          single_device_state, step_value=step_value)}
        else:
          action_service = self.set(self.tvs, single_device_state)
      else:
        self.error(f"turn({entity_list}, {state}) is not supported.")

    elif state in ['single_device_volume_inc', "single_device_volume_dec"] :
        action_service = media_automation_helpers.single_device_volume_action(
          entity_list,
          step_value,
        )

    elif entity_list == self.media_players or entity_list == self.tv_soundbars:
        action_service = media_automation_helpers.media_play_pause_action(
          entity_list,
          state,
          self.continueIf,
          self.set,
        )

    ##############################################
    # Curtains
    ##############################################
    elif entity_list == self.curtains:

      if state in ['increment', 'decrement']:
        action_service = {"service": "cover.set_cover_position",
                          "target":{"entity_id": self.curtains},
                          # making sure the final value saturated to range [0,100]
                          "data":  {"position": "{{ [[ (state_attr('" + self.curtains[0] + "', 'current_position')) + " + str(step_value) + " ,0]|max,100]|min}}"}}
      # Shutter blind
      elif self.aqara_shutter_blind == True and state in ['on', 'off', 'toggle']:
        if state == 'on':
          if self.room_entity == 'study':
            # open full blind for study
            action_service = {'if': {"condition": "numeric_state",
                                     "entity_id": self.curtains,
                                     "attribute": "current_position",
                                     "above": 95,},
                             'then': {"service": "cover.set_cover_position",
                                      "data":    {"position": 100},
                                      "entity_id": self.curtains}
                            }

          else:
            # open shutter for master toilet
            # Set to 0 position to open the shutter, blind full down
            action_service = {'if': {"condition": "numeric_state",
                                     "entity_id": self.curtains,
                                     "attribute": "current_position",
                                     "above": 0,},
                             'then': {"service": "cover.set_cover_position",
                                      "data":    {"position": 0},
                                      "entity_id": self.curtains}
                            }
        elif state == 'off':
          # Set to 2 position to close the shutter, blind full down
          action_service = {'if': {"condition": "numeric_state",
                                     "entity_id": self.curtains,
                                     "attribute": "current_position",
                                     "above": 2,},
                            'then': {"service": "cover.set_cover_position",
                                     "data":    {"position": 2},
                                     "entity_id": self.curtains}
                            }
        else:
          action_service = {"service":   "cover.toggle",
                            "entity_id": entity_list}
      # Normal blind or curtains
      elif state in ['on']:
        action_service = {'if': {"condition": "numeric_state",
                                 "entity_id": self.curtains,
                                 "attribute": "current_position",
                                 "below": 5},
                          'then': {"service":  "cover.open_cover",
                                  "entity_id": entity_list}
                          }
      elif state in ['off']:
        action_service = {'if': {"condition": "numeric_state",
                                 "entity_id": self.curtains,
                                 "attribute": "current_position",
                                 "above": 95},
                          'then': {"service":  "cover.close_cover",
                                   "entity_id": entity_list}
                          }
      elif state in ['toggle']:
        action_service =  {
                            "if": [
                              {
                                'alias': 'toggle all curtains together: if any of curtains is on, turn off all curtains, otherwise turn on all curtains',
                                "condition": "state",
                                "entity_id": entity_list,
                                "state": ['open', 'opening'],
                                "match": 'any'
                              }
                            ],
                            "then": self.set(entity_list, 'off'),
                            "else": self.set(entity_list, 'on')
                          }
      else:
        self.error(f"turn({entity_list}, state={state}) is not supported")

      # stop the curtain before any curtain actions - make sure the previous action is stopped
      action_service = self.convertToSingleService(
                      [{"service":  "cover.stop_cover",
                        "entity_id": entity_list},
                        action_service])

    ##############################################
    # Thermostats and heatings
    ##############################################
    # TODO make sure that it only turns a directory or a list.
    # use a different way to handle this case
    elif entity_list == self.thermostat :
      hvac_mode = "off" if state == 'off' else "heat"

      if state in ['on', 'off']:
        action_service = { "service": "climate.set_hvac_mode",
                           "data": {"hvac_mode": hvac_mode},
                           "entity_id": entity_list
                        }
      else:
        self.error(f"turn({entity_list}, state={state}) is not supported")


    elif entity_list == 'heating':
      if state in ['toggle']:
        action_service = {"if": self.continueIf(self.thermostat, "off"),
                          "then": self.set(entity_list, 'on'),
                          "else": self.set(entity_list, 'off')}
      elif state in ['on', 'off']:
        action_service = self.convertToSingleService(
                        [self.set(self.thermostat,          state),
                          self.set(self.thermostat_schedule, state)] + \
                          [])
                          #([] if self.room_entity != 'kitchen' else \
                          #[self.set('switch.kitchen_hot_water', state)])

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
          #                      "then": self.set(self.wall_switches,  state),
          #                      "else": self.set(self.ceiling_lights, state, inc_unavail=False)
          #                    }

    ##############################################
    # Lights and light switches
    ##############################################
    elif entity_list == self.wall_switches and state == 'on':
      action_service = self.convertToSingleService(
                        [{"service":"homeassistant.turn_off", "entity_id": entity_list},
                         {"delay": {"milliseconds": 200}},
                         {"service":"homeassistant.turn_on",  "entity_id": entity_list}],
                          alias='Everytime to turn on a wall switch, make sure to turn off it first to make sure the smart lights will be back on')

    elif light_brightness != None:
        action_service = {"service" : "light.turn_on",
                          "entity_id" : entity_list,
                          "data": {"brightness_pct": light_brightness}}

    # Adaptive light only applies when lights are turned on by light.turn_on instead of homeassistant.turn_on
    # that's not true.....
    elif is_light_list and (state == 'on' or state == 'off'):
      action_service = {"service":"light.turn_on"  if state == 'on'     else \
                                  "light.turn_off" if state == 'off'    else None,
                        "entity_id": entity_list}

    elif is_light_list and (state == 'increment' or state == 'decrement'):
      action_service = {
                          "if": [
                            {
                              'alias': 'increment brightness unless it is off, set the brightness to 1 percent',
                              "condition": "state",
                              "entity_id": entity_list,
                              "state": "off",
                            }
                          ],
                          # magic_home led cannot easily be turned on by set light_brightness=1 from off state.
                          "then":[self.set(entity_list, 'on')] if 'led' in entity_list[0] else [] + \
                                 [self.set(entity_list, 'on', light_brightness=1),],
                          "else": {"service":"light.turn_on",
                                  "target":{"entity_id":entity_list},
                                  "data":{"brightness_step_pct":step_value}},
                        }
    elif is_light_list and state == 'cycle':
        entity_id = entity_list[0] if type(entity_list) is list else entity_list
        if entity_id.startswith('light.'):
          action_service = {
                  "if":     self.continueIf(entity_list, "off"),
                  "then": [ {"service" : "light.turn_on",
                              "entity_id" : entity_list,
                              "data": {
                                "brightness": 3
                              }},
                          ],
                  "else": {"service" : "light.turn_on",
                            "entity_id" : entity_list,
                            "data_template": {
                              # unfortunately, I can only read brightness correctly and set brightness_pct correctly.
                              "brightness": "{% set brightness = state_attr('" + entity_id + "', 'brightness') | int(0) %}"
                                            "{% if brightness == 0 or is_state('" + entity_id + "', 'off') %}3"
                                            "{% elif brightness <= 83 %}84"
                                            "{% elif brightness <= 167 %}168"
                                            "{% elif brightness <= 254 %}255"
                                            "{% else %}0{% endif %}"
                            }}
                  }
        else:
          self.error('light brightness cycle does not support on entity ' + entity_id)
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
                          "then": self.set(entity_list, 'off'),
                          "else": self.set(entity_list, 'on')
                        }
    else:
      #(f"turn({entity_list}, state={state}) is not supported")
      action_service = {"service": "script.do_nothing"}

    ##############################################
    # Final wrapper
    ##############################################
    if entity_list != None and entity_list != []:
      return self.convertToSingleService( action_service,
                                          alias = service_action_helpers.service_action_alias(
                                            entity_list,
                                            state=state,
                                            light_brightness=light_brightness,
                                          ))
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
    return automation_helpers.wrap_service_sequence(service_list, alias=alias)

  def callSceneService(self, scene_name):
      parallel_enable = True
      scene_service = []
      if   scene_name == 'All White':
          scene_service += [self.set(self.lamps, "on"),
                            self.set(self.ceiling_lights, "on"),
                            self.set(self.leds, "on"),
                            self.set(self.tvs, tv_brightness=3)]
      elif scene_name == 'Ceiling Light White':
          scene_service += [self.set(self.lamps, "off"),
                            self.set(self.leds, "off"),
                            self.set(self.ceiling_lights, "on"),
                            self.set(self.tvs, tv_brightness=3)]
      #elif scene_name == 'Ceiling Light White with Curtain Open':
      #    scene_service += [self.set(self.leds + self.lamps, "off"),
      #                      self.set(self.ceiling_lights, "on"),
      #                      self.set(self.tvs, tv_brightness=3),
      #                      self.set(self.curtains, 'on')]
      elif scene_name == 'Lamp LED White':
          scene_service += [self.set(self.ceiling_lights, "off"),
                            self.set(self.lamps, "on"),
                            self.set(self.leds, "on")]
      elif scene_name == 'LED White':
          scene_service += [self.set(self.leds, "on")]
      elif scene_name == 'Hue':
          parallel_enable = False
          scene_service += [# turn off non rgb lights
                            { "service" : "pyscript.turn_rgb_light",
                              "data": {"light_list": self.lamps + self.ceiling_lights+ self.leds,
                              "state": 'off',
                              "rgb" : 'non_rgb_only'}},
                            # set hue colors
                            { "service" : "pyscript.turn_rgb_light",
                              "data": {"light_list": self.lamps + self.ceiling_lights+ self.leds}
                            },
                            self.set(self.tvs, tv_brightness=2),
                            ]
      elif scene_name == 'Night Mode':
          scene_service += [{ "service": "homeassistant.turn_on",
                              "entity_id": "scene." + self.room_entity + "_night_mode" },
                            self.set(self.tvs, tv_brightness=2)]
      elif scene_name == 'Dark Night Mode':
          scene_service += [{ "service": "homeassistant.turn_on",
                              "entity_id": "scene." + self.room_entity + "_dark_night_mode" },
                            self.set(self.tvs, tv_brightness=1)]
      elif scene_name == "Sleep Mode":
          scene_service += [{ "service": "homeassistant.turn_on",
                              "entity_id": "scene." + self.room_entity + "_sleep_mode"}]
      elif scene_name == 'All Off':
          scene_service += [self.set(self.ceiling_lights, "off"),
                            self.set(self.lamps, "off"),
                            self.set(self.leds, "off"),
                            self.set(self.tvs, tv_brightness=3)] # reset TV brightness for bright room in the day time
                                                                 # considering turn it to 1 for night
      elif scene_name in ['light states when intense light summer',
                          'light states when moderate light outdoor',
                          'light states when low light outdoor',
                          'light states when sleep mode',
                          ]:
        light_scene_state = scene_name.replace('light states when ', '')
        scene_service += [{"parallel":[
          {"if": self.continueIf(self.ceiling_light_control_when[light_scene_state], "on"), "then": self.set(self.ceiling_lights, "on"), "else": self.set(self.ceiling_lights, "off")},
          {"if": self.continueIf(self.lamp_control_when[light_scene_state]         , "on"), "then": self.set(self.lamps,          "on"), "else": self.set(self.lamps,          "off")},
          {"if": self.continueIf(self.led_control_when[light_scene_state]          , "on"), "then": self.set(self.leds,           "on"), "else": self.set(self.leds,           "off")},
          ]}]
      elif scene_name in ['curtain states when low light outdoor',
                          'curtain states when moderate light outdoor',
                          'curtain states when intense light summer',
                          'curtain states when sleep mode',
                          ]:
        curtain_scene_state = scene_name.replace('curtain states when ', '')
        scene_service += [{"parallel":[
          {"if": self.continueIf(self.curtain_control_when[curtain_scene_state]     , "on"), "then": self.set(self.curtains,       "on"), "else": self.set(self.curtains,       "off")}
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


  def alwaysOnCond(self):
    return automation_helpers.always_on_condition()


  def entity_is_on(self, entity):
    return automation_helpers.entity_is_on(entity)

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

  def continueIf(self, entity_id, state, attribute=None, lastFor=None):
    return automation_helpers.continue_if(entity_id, state, attribute=attribute, lastFor=lastFor)


  def condition_list_is(self, condition_name):
    if condition_name == 'Bright morning':
      return [{ 'alias': condition_name,
                "condition": "and",
                "conditions": [
                  { "condition": "or",
                    "conditions": [
                      {"condition": "numeric_state",
                        "entity_id": self.light_sensor,
                        "above": self.min_value_as_bright},
                      { "condition": "state",
                        "entity_id": self.light_sensor,
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
                    #"after": self.morning_start_time,
                    #"before": self.morning_end_time,
                    'before': self.noon_time,
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
                        "entity_id": self.light_sensor,
                        "above": self.min_value_as_bright},
                      { "condition": "state",
                        "entity_id": self.light_sensor,
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
                    'after': self.noon_time,
                    #"after": self.afternoon_start_time,
                    #"before": self.afternoon_end_time,
                  },
                ]
              }]

    elif condition_name == 'intense light summer' or \
         condition_name == 'moderate light outdoor' or \
         condition_name == 'low light outdoor' or \
         condition_name == 'sleep mode':

      # Common light intensity threshold
      if condition_name == 'intense light summer':
        cond = [{
          "condition": "template",
          "value_template": "{{ states('" + self.light_intensity_entity +  "') | float(0) > states('" + self.light_intensity_threshold_when['intense light summer'] + "') | float(0) }}"""
        }]
      elif condition_name == 'moderate light outdoor':
        cond = [{
          "condition": "template",
          "value_template": "{{ states('" + self.light_intensity_entity +  "') | float(0) > states('" + self.light_intensity_threshold_when['moderate light outdoor'] + "') | float(0) }}"""
        }]
      else:
        cond = [{
          "condition": "template",
          "value_template": "{{ states('" + self.light_intensity_entity +  "') | float(0) <= states('" + self.light_intensity_threshold_when['moderate light outdoor'] + "') | float(0) }}"""
        }]

      if condition_name == 'intense light summer':
        cond += [
                # Outdoor temp above certain temperature
                {
                  "condition": "numeric_state",
                  "entity_id": self.outside_temperature,
                  "above": "12" if self.west_face_windows else "15"
                },
                # Summer
                {
                  "condition": "template",
                  "value_template": "{{ now().month > 4 and now().month < 9 }}"
                },
              ]

      if condition_name != 'sleep mode':
        cond += [
          { "condition": "state",
            "entity_id": self.al_sleep_mode,
            "state": 'off'}
        ]
      else:
        cond = [
          { "condition": "state",
            "entity_id": self.al_sleep_mode,
            "state": 'on'}
        ]


      return cond

    else:
      raise error( "Condition " + condition_name + " is not supported.")



  def getDashboardSettings(self):
    settings = dashboard_settings.default_dashboard_settings()
    self.dashboard_default_root = settings["dashboard_default_root"]
    self.dashboard_view_name = settings["dashboard_view_name"]
    self.room_icon = settings["room_icon"]
    self.room_theme = settings["room_theme"]

  def addView(self, viewPath='',
                    cards=[],
                    theme="Mushroom Shadow",
                    title=''):
    self.views += [dashboard_view_helpers.build_view(
      view_path=viewPath,
      cards=cards,
      theme=theme,
      title=title
    )]

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
    return dashboard_view_helpers.layout_wrapper_cards(self.dashboard_type, cards=cards)

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
          "icon_tap_action": {
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
            ] + ([
              self.getTemplateCard(
                icon       = "mdi:battery-charging-outline",
                icon_color = "red",
                condition_state  = 'on',
                condition_entity = self.unavailable_entity
              )
            ]) + ([] if self.room_battery_entity_list == [] else [
              self.getTemplateCard(
                icon       = "{% if is_state('" + self.room_low_battery_entity + "', 'on') %}\n  mdi:battery-20-bluetooth \n{% else %}\n  mdi:battery-70\n{% endif %}",
                icon_color = "{% if is_state('" + self.room_low_battery_entity + "', 'on') %}\n  amber\n{% endif %}",
                tap_entity = self.room_battery_entity,
                #condition_state  = 'on',
                #condition_entity = self.room_low_battery_entity,
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
                tap_entity = self.tvs[0],
                condition_entity = self.tvs[0],
                condition_state  = 'on'
              )
            ]) + ([] if self.lights == [] else [
              self.getTemplateCard(
                icon       = "{% if is_state(entity, 'on') %}\n  mdi:floor-lamp\n{% else %}\n  mdi:floor-lamp-outline\n{% endif %}",
                icon_color = "{% if is_state(entity, 'on') %}\n  amber\n{% endif %}",
                tap_entity = self.light_group
              )
            ]) + ([] if self.cfg_occupancy_override == False else [
              self.getTemplateCard(
                icon       = "{% if is_state(entity, 'on') %}\n  mdi:timer-sand\n{% else %}\n  mdi:timer-sand-paused\n{% endif %}",
                icon_color = "{% if is_state(entity, 'on') %}\n  yellow\n{% endif %}",
                tap_entity = self.occupancy_override_entity
              )
            ]) + ([] if self.cfg_temp_control == False else [
              self.getTemplateCard(
                icon       = "{% if is_state(entity, 'heat') %}\n  mdi:heating-coil\n    {% else %}   \n  mdi:snowflake\n      {% endif %}",
                icon_color = "{% if is_state(entity, 'heat') %}\n  {% if state_attr(entity, 'temperature') > state_attr(entity, 'current_temperature') %}\n  red\n {% else %}\n blue\n  {% endif %}\n {% endif %}\n",
                condition_state  = 'heat',
                condition_entity = self.thermostat,
              )
            ]) + ([] if self.cfg_occupancy == False else [
             self.getTemplateCard(
               icon       = "{% if   is_state(entity, 'Outside') %}\n  mdi:door-closed\n{% elif is_state(entity, 'Just Entered') %}\n  mdi:arrow-right-circle\n{% elif is_state(entity, 'In Sleep') %}\n  mdi:sleep\n{% else %}\n  mdi:account-multiple\n{% endif %}",
               icon_color = "{% if   is_state(entity, 'Outside') %}                     {% elif is_state(entity, 'Just Entered') %}\n  green\n                 {% elif is_state(entity, 'In Sleep') %}\n  blue\n     {% else %}\n  purple\n              {% endif %}",
               tap_entity = self.room_occupancy,
               condition_state_not  = 'Outside',
               condition_entity     = self.room_occupancy,
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
        "icon_tap_action": {
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
    return dashboard_restrictions.restricted_access_card(user, inner_card)


  # Create a new yaml and write to it
  def writeConfig (self):
    write_result = package_writer.write_room_package(
      room_entity=self.room_entity,
      entity_declarations=self.entity_declarations,
      customize_dict=self.customize_dict,
      script_dir=SCRIPT_DIR,
      auto_generated_packages_dir=AUTO_GENERATED_PACKAGES_DIR,
      packages_dir=PACKAGES_DIR,
      write_yaml_file=write_yaml_file
    )

    self.script_dir = write_result["script_dir"]
    self.auto_gen_dir = write_result["auto_gen_dir"]
    self.auto_gen_config_path = write_result["auto_gen_config_path"]
    self.auto_gen_customize_dir = write_result["auto_gen_customize_dir"]
    self.customize_declaration = write_result["customize_declaration"]


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



  def remove_disabed_entities(self):
    self.entity_declarations = configured_entity_filter.remove_disabled_entities(self.entity_declarations)

#########################################################################
# Instantiate all the rooms with custom entities/automation override    #
#########################################################################
globals().update(rooms.define_room_classes(RoomBase))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
#    Shared Lovelace
#
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@





def create_package_rooms():
  return room_registry.create_package_rooms(globals())


def get_dashboard_room_classes():
  return room_registry.get_dashboard_room_classes(globals())



##################################################################
#  Add command line options and run based on options
##################################################################
parser = ''
args   = ''

def build_arg_parser():
  return generator_cli.build_arg_parser()


def parse_args(argv=None):
  global parser
  global args
  parser = build_arg_parser()
  args = parser.parse_args(argv)
  return args


def render_package_configs():
  create_package_rooms()


def check_entity_registry_config(parsed_args):
  if not parsed_args.check_auto_system_config:
    return

  ha_entity_registry.read_core_entity_entries_json(STORAGE_DIR)
  unexpected_entities = ha_entity_registry.find_unexpected_entities(
    check_all_suffix_duplicates=parsed_args.check_auto_system_config
  )

  for entity_id in unexpected_entities:
    print(entity_id)


def create_clean_entity_registry_config(parsed_args):
  if not parsed_args.create_system_config:
    return

  ha_entity_registry.read_core_entity_entries_json(STORAGE_DIR)
  ha_entity_registry.remove_auto_generated_automation_entities()
  core_entities_path = ha_entity_registry.write_core_entity_entries_json(SCRIPT_DIR)
  print ("A updated core.entity_registry with no duplicated automation is generated at: " + core_entities_path)
  print ("Please manually run cp " + core_entities_path + ' ~/config/.storage')


def get_dashboard_type(parsed_args):
  return generator_cli.get_dashboard_type(parsed_args)


def get_dashboard_language(parsed_args):
  return generator_cli.get_dashboard_language(parsed_args)


def render_dashboard_config(parsed_args):
  dashboard_type = get_dashboard_type(parsed_args)
  dashboard_language = get_dashboard_language(parsed_args)

  if parsed_args.render_dashboard_yaml:
    dashboard_generator.render_dashboard(
      format='yaml',
      dashboard_type=dashboard_type,
      dashboard_language=dashboard_language,
      room_base_class=RoomBase,
      room_classes=get_dashboard_room_classes(),
      dashboard_output_dir=DASHBOARD_OUTPUT_DIR,
      storage_dir=STORAGE_DIR,
      write_yaml_file=write_yaml_file,
      write_json_file=write_json_file
    )
  elif parsed_args.render_dashboard_json:
    dashboard_generator.render_dashboard(
      format='json',
      dashboard_type=dashboard_type,
      dashboard_language=dashboard_language,
      room_base_class=RoomBase,
      room_classes=get_dashboard_room_classes(),
      dashboard_output_dir=DASHBOARD_OUTPUT_DIR,
      storage_dir=STORAGE_DIR,
      write_yaml_file=write_yaml_file,
      write_json_file=write_json_file
    )


def run(parsed_args):
  if parsed_args.render_auto_config:
    render_package_configs()

  if parsed_args.check_auto_system_config:
    check_entity_registry_config(parsed_args)

  if parsed_args.create_system_config:
    create_clean_entity_registry_config(parsed_args)

  render_dashboard_config(parsed_args)


def main(argv=None):
  run(parse_args(argv))


if __name__ == "__main__":
  main()


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


#translation = translator.translate("This is a pen.")
#translation = translator.translate("Master Room Lamp 1")
#print (translation)
