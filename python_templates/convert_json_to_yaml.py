import yaml
import json
import os

script_dir  = os.path.dirname(os.path.realpath(__file__))


with open(script_dir + '/example.json', 'r') as file:
    configuration = json.load(file)

with open(script_dir + '/example.yaml', 'w') as yaml_file:
    yaml.dump(configuration, yaml_file, indent=2)

