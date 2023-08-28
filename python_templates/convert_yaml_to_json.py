import yaml
import json
import os

script_dir  = os.path.dirname(os.path.realpath(__file__))

with open(script_dir + '/example.yaml', 'r') as file:
    configuration = yaml.safe_load(file)

with open(script_dir + '/example.json', 'w') as json_file:
    json.dump(configuration, json_file, indent=2)
