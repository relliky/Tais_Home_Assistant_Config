import os


def write_room_package(room_entity,
                       entity_declarations,
                       customize_dict,
                       script_dir,
                       auto_generated_packages_dir,
                       packages_dir,
                       write_yaml_file):
  auto_gen_config_path = os.path.join(auto_generated_packages_dir, "auto_gen_" + room_entity + ".yaml")
  write_yaml_file(auto_gen_config_path, entity_declarations, include_header=True)

  customize_declaration = {'homeassistant': {'customize': customize_dict}}
  customize_config_path = os.path.join(packages_dir, "auto_gen_customize_" + room_entity + ".yaml")
  write_yaml_file(customize_config_path, customize_declaration, include_header=True)

  return {
    "script_dir": script_dir,
    "auto_gen_dir": auto_generated_packages_dir,
    "auto_gen_config_path": customize_config_path,
    "auto_gen_customize_dir": packages_dir,
    "customize_declaration": customize_declaration,
    "package_config_path": auto_gen_config_path,
  }
