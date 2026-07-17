import copy
import json
import os


orig_core_entities_dict = {}
updated_core_entities_dict = {}


def read_core_entity_entries_json(storage_dir):
  global orig_core_entities_dict
  global updated_core_entities_dict

  core_entities_path = os.path.join(storage_dir, "core.entity_registry")

  with open(core_entities_path, encoding="utf-8") as registry_file:
    orig_core_entities_dict = json.load(registry_file)
    updated_core_entities_dict = copy.deepcopy(orig_core_entities_dict)

  return orig_core_entities_dict


def find_unexpected_entities(check_all_suffix_duplicates=True):
  unexpected_entities = []

  for entity in orig_core_entities_dict['data']['entities']:
    entity_id = entity['entity_id']

    if entity_id.startswith('automation.z') and entity_id.endswith('_2'):
      unexpected_entities += [entity_id]
    elif check_all_suffix_duplicates and entity_id.endswith('_2'):
      unexpected_entities += [entity_id]

  return unexpected_entities


def remove_auto_generated_automation_entities():
  global updated_core_entities_dict

  updated_core_entities_dict['data']['entities'] = []

  for entity in orig_core_entities_dict['data']['entities']:
    if not entity['entity_id'].startswith('automation.z'):
      updated_core_entities_dict['data']['entities'] += [entity]

  return updated_core_entities_dict


def write_core_entity_entries_json(output_dir):
  core_entities_path = os.path.join(output_dir, "core.entity_registry")

  with open(core_entities_path, 'w', encoding="utf-8") as json_file:
      json.dump(updated_core_entities_dict, json_file, indent=2)

  return core_entities_path
