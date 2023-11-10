import json
from pathlib import Path
from dataprocessing import *

data_dict = {}

def get_all_paper_names():
    directory_path = './papers/'  # Replace with the path to your directory

    # Get a list of all file names in the directory
    path = Path(directory_path)
    file_names = [f.name for f in path.iterdir() if f.is_file()]

    # make sure that papers with larger version rank ahead
    file_names.sort(reverse=True)

    # store paper names with the latest version number
    latest_version_papers = {}

    curr_id = None
    for file_name in file_names:
        paper_id, version = file_name[:-4].split('v')
        if paper_id != curr_id:
            curr_id = paper_id
            latest_version_papers[paper_id] = version
    
    # save result to json files instead of calculate everytime
    with open("latest_version_papers.json", "w") as file:
        json.dump(latest_version_papers, file)

"""
Extract given papers' full name 
"""
def extract_paper_from_json(sections=[]):
    # Open the JSON file for reading
    with open("latest_version_papers.json", "r") as file:
        # Load the data from the JSON file
        latest_version_papers = json.load(file)
    
    paper_names = []

    # by default, add all papers from validation.json
    if len(sections) == 0:
        for paper_id in data_dict:
            latest_version = latest_version_papers[paper_id]
            latest_paper_name = paper_id + "v" + latest_version + ".txt"
            paper_names.append(latest_paper_name)
    # when sections is given
    else:
        for section in sections:
            begin, end = section
            for num in range(begin, end + 1):
                padded_num_str = str(num).zfill(5)
                paper_id = "2201." + padded_num_str
                if paper_id in data_dict:
                    latest_version = latest_version_papers[paper_id]
                    latest_paper_name = paper_id + "v" + latest_version + ".txt"
                    paper_names.append(latest_paper_name)

    return paper_names

if __name__ == "__main__":

    init_trie()
    # Read the JSON file
    with open('./validation.json') as file:
        data = json.load(file)
        for key in data:
            data_dict[key] = data[key]

    # paper_names = extract_paper_from_json()
    paper_names = extract_paper_from_json([[1, 3], [9, 12]])

    print(paper_names)

    hit_cnt = 0
    miss_cnt = 0
    overshoot_cnt = 0

    size = 0

    for paper in paper_names:
        print("validation of paper:" + paper + "\n")

        pred = getresult("./papers/" + paper)
        true = data_dict[paper.split('v')[0]]

        common_inst = list(set(pred).intersection(true))
        overshoot_inst = list(set(pred) - set(true))
        missed_inst = list(set(true) - set(pred))
        
        size += len(true)
        hit_cnt += len(common_inst)
        miss_cnt += len(missed_inst)
        overshoot_cnt += len(overshoot_inst)

        print("paper name: ", paper)

        print("common: ", common_inst)
        print("overshoot: ", overshoot_inst)
        print("missed: ", missed_inst)

        print("\n")
    
    print("overall size = ", size)
    print("hit_cnt = ", hit_cnt)
    print("miss_cnt = ", miss_cnt)
    print("overshoot_cnt = ", overshoot_cnt)
        
    acc_rate = hit_cnt / size
    miss_rate = miss_cnt / size
    overshoot_rate = overshoot_cnt / size

    print("acc_rate = ", acc_rate)
    print("miss_rate = ", miss_rate)
    print("overshoot_rate = ", overshoot_rate)

    print("\n\n")
        