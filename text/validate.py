import json

# Read the JSON file
with open('./text/validation.json') as file:
    data = json.load(file)
    
    data_dict = {}

    for key in data:
        data_dict[key] = data[key]
    
    print(data_dict)