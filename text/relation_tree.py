import json

relation_dict = {}

# Read the JSON file
with open('./1.34_relations.json') as file:
    relation_dict = json.load(file)
    for inst, values in relation_dict:
        if "Child" not in values:
            pass