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
        "2201.00010v1.txt",
        "2201.00011v1.txt",
        "2201.00012v1.txt",
        "2201.00013v1.txt",
        "2201.00014v1.txt",
        "2201.00015v1.txt",
        "2201.00016v2.txt",
        "2201.00017v1.txt",
        "2201.00018v1.txt",
        "2201.00019v2.txt"
    ]

    hit_cnt = 0
    miss_cnt = 0
    excess_cnt = 0

    size = 0

    for paper in paper_names:
        # print("validation of paper:"+paper+"\n")
        pred = getresult("./samples/" + paper)
        true = data_dict[paper.split('v')[0]]

        common_inst = list(set(pred).intersection(true))
        excess_inst = list(set(pred) - set(true))
        missed_inst = list(set(true) - set(pred))
        
        size += len(true)
        hit_cnt += len(common_inst)
        miss_cnt += len(missed_inst)
        excess_cnt += len(excess_inst)

        print("paper name: ", paper)

        print("common_inst: ", common_inst)
        print("excess_inst: ", excess_inst)
        print("missed_inst: ", missed_inst)

        print("\n")
    
    print("overall size = ", size)
    print("hit_cnt = ", hit_cnt)
    print("miss_cnt = ", miss_cnt)
    print("excess_cnt = ", excess_cnt)
    
    acc_rate = hit_cnt / size
    miss_rate = miss_cnt / size
    excess_rate = excess_cnt / size

    print("acc_rate = ", acc_rate)
    print("miss_rate = ", miss_rate)
    print("excess_rate = ", excess_rate)