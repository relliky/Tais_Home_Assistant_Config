import yaml
import json

with open('example.yaml', 'r') as file:
    configuration = yaml.safe_load(file)

with open('example.json', 'w') as json_file:
    json.dump(configuration, json_file, indent=2)
