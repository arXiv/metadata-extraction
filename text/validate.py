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


def extract_paper_from_json(sections=[]):
    # Open the JSON file for reading
    with open("latest_version_papers.json", "r") as file:
        # Load the data from the JSON file
        latest_version_papers = json.load(file)
    
    paper_names = []

    if len(sections) == 0:
        for paper_id in data_dict:
            latest_version = latest_version_papers[paper_id]
            latest_paper_name = paper_id + "v" + latest_version + ".txt"
            paper_names.append(latest_paper_name)

    return paper_names
    # TODO: implement conditions when sections is given

if __name__ == "__main__":

    init_trie()
    # Read the JSON file
    with open('./validation.json') as file:
        data = json.load(file)
        for key in data:
            data_dict[key] = data[key]

    # paper_names = [
    #     "2201.00001v3.txt",
    #     "2201.00002v1.txt",
    #     "2201.00003v1.txt",
    #     "2201.00004v1.txt",
    #     "2201.00005v1.txt",
    #     "2201.00006v2.txt",
    #     "2201.00007v3.txt",
    #     "2201.00008v3.txt",
    #     "2201.00009v3.txt",
    #     "2201.00010v1.txt"
    # ]

    paper_names = extract_paper_from_json()

    print(paper_names)

    for paper in paper_names:
        print("validation of paper:"+paper+"\n")
        test_result = getresult("./papers/" + paper)
        expect_result = data_dict[paper.split('v')[0]]

        common_elements = list(set(test_result).intersection(expect_result))
        overshoot_elements = list(set(test_result) - set(expect_result))
        missed_elements = list(set(expect_result) - set(test_result))

        print("paper name: ", paper)

        print("common: ", common_elements)
        print("overshoot: ", overshoot_elements)
        print("missed: ", missed_elements)

        print("\n\n")
        