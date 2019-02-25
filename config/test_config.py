import json


with open('config.json') as config_file:
    data = json.load(config_file)

print(data['my_elem']['q1'][2])
