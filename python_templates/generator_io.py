import os

import yaml


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_ROOT = None
PACKAGES_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "packages"))
AUTO_GENERATED_PACKAGES_DIR = os.path.join(PACKAGES_DIR, "_auto_generated_packages")
STORAGE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".storage"))
DASHBOARD_OUTPUT_DIR = SCRIPT_DIR


AUTO_GENERATED_HEADER = (
  "#############################################################################\n"
  "# DO NOT MODIFY. This is an automatically generated file.                   # \n"
  "#############################################################################\n"
)


def configure_output_root(output_root=None):
  global OUTPUT_ROOT
  global PACKAGES_DIR
  global AUTO_GENERATED_PACKAGES_DIR
  global STORAGE_DIR
  global DASHBOARD_OUTPUT_DIR

  if output_root == None:
    OUTPUT_ROOT = None
    PACKAGES_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "packages"))
    AUTO_GENERATED_PACKAGES_DIR = os.path.join(PACKAGES_DIR, "_auto_generated_packages")
    STORAGE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".storage"))
    DASHBOARD_OUTPUT_DIR = SCRIPT_DIR
  else:
    OUTPUT_ROOT = os.path.abspath(output_root)
    PACKAGES_DIR = os.path.join(OUTPUT_ROOT, "packages")
    AUTO_GENERATED_PACKAGES_DIR = os.path.join(PACKAGES_DIR, "_auto_generated_packages")
    STORAGE_DIR = os.path.join(OUTPUT_ROOT, ".storage")
    DASHBOARD_OUTPUT_DIR = os.path.join(OUTPUT_ROOT, "python_templates")


def write_yaml_file(path, data, include_header=False):
  yaml.Dumper.ignore_aliases = lambda *args : True

  os.makedirs(os.path.dirname(path), exist_ok=True)
  with open(path, "w") as yaml_file:
    if include_header:
      yaml_file.write(AUTO_GENERATED_HEADER)
    yaml_file.write(yaml.dump(data, sort_keys=False, width=float("inf")))


def write_json_file(path, data):
  os.makedirs(os.path.dirname(path), exist_ok=True)
  with open(path, "w") as json_file:
    import json
    json.dump(data, json_file, sort_keys=False, indent=2)
