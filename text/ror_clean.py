import csv
import json

def get_namesake_insts():
    csv_file = 'v1.34-2023-10-12-ror-data.csv'
    # output_file = "1.34_relations.json"

    inst_name_id_dict = {}

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            inst_id = row["id"]
            inst_name = row["name"]

            if inst_name in inst_name_id_dict:
                inst_name_id_dict[inst_name].append(inst_id)
            else:
                inst_name_id_dict[inst_name] = [inst_id]
    
    namesake_inst_dict = {}
    
    for inst_name, inst_ids in inst_name_id_dict.items():
        if len(inst_ids) > 1:
            namesake_inst_dict[inst_name] = inst_ids
    
    sorted_namesake_inst_dict = dict(sorted(namesake_inst_dict.items(), key=lambda item: len(item[1])))

    len_cnt_dict = {}
    
    for inst_name, inst_ids in sorted_namesake_inst_dict.items():
        curr_len = len(inst_ids)
        if curr_len in len_cnt_dict:
            len_cnt_dict[curr_len] += 1
        else:
            len_cnt_dict[curr_len] = 1

    # Write the dictionary to the JSON file
    with open("namesake_insts.json", "w") as json_file:
        json.dump(sorted_namesake_inst_dict, json_file, indent=4)
    
    with open("namesake_inst_cnt.json", "w") as json_file:
        json.dump(len_cnt_dict, json_file, indent=4)


def test():
    # Your dictionary
    my_dict = {
        'apple': ['red', 'green', 'yellow'],
        'banana': ['yellow'],
        'cherry': ['red'],
        'date': ['brown', 'sweet'],
        'fig': ['purple', 'sweet', 'green', 'white']
    }

    # Sort the dictionary by the length of each value
    sorted_dict = dict(sorted(my_dict.items(), key=lambda item: len(item[1])))

    # Print the sorted dictionary
    print(sorted_dict)


if __name__ == "__main__":
    get_namesake_insts()