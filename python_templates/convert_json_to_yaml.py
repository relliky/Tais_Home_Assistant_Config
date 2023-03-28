import yaml
import json

with open('example.json', 'r') as file:
    configuration = json.load(file)

with open('example.yaml', 'w') as yaml_file:
    yaml.dump(configuration, yaml_file, indent=2)

