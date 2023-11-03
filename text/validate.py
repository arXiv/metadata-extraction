import json
from dataprocessing import *

data_dict = {}

if __name__ == "__main__":
    # Read the JSON file
    with open('./validation.json') as file:
        data = json.load(file)
        for key in data:
            data_dict[key] = data[key]
    init_trie()

    paper_names = [
        "2201.00001v3.txt",
        "2201.00002v1.txt",
        "2201.00003v1.txt",
        "2201.00004v1.txt",
        "2201.00005v1.txt",
        "2201.00006v2.txt",
        "2201.00007v3.txt",
        "2201.00008v3.txt",
        "2201.00009v3.txt",
        "2201.00010v1.txt"
    ]

    for paper in paper_names:
        print("validation of paper:"+paper+"\n")
        test_result = getresult("./samples/" + paper)
        expect_result = data_dict[paper.split('v')[0]]
        common_elements = list(set(test_result).intersection(expect_result))
        test_diff_elements = list(set(test_result) - set(expect_result))
        expect_diff_elements = list(set(expect_result) - set(test_result))

        print("paper name: ", paper)

        print("common: ", common_elements)
        print("test_diff: ", test_diff_elements)
        print("expect_diff: ", expect_diff_elements)

        print("\n\n")
        