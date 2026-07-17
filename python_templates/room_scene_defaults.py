def default_post_room_config(room_entity, cfg_group_auto):
  config = {
    "room_scene_ctl": "input_select." + room_entity + "_scene",
    "cur_scene": "unintialized_cur_scene",
  }

  if cfg_group_auto:
    config["gui_ctl_group"] = "group." + room_entity + "_auto_gen_automations"

  return config
