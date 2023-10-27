import compare
import csv

nameMap = {}
trie = compare.Trie()

def process_line(elements):
    id = elements[0]
    # names = elements[1:]
    # for name in names:
    #     if name != '':

    # only use the full name to compare
    name = elements[1]
    trie.insert(name, id)

def test_paper(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()

    contents = file_contents.split("\u000C")
    text = contents[0]

    result = []
    for i in range(len(text)):
        for j in range(i+1, len(text)+1):
            substring = text[i:j]
            #print("check string:"+substring)
            rlt = trie.search(substring)
            if rlt:
                if rlt.is_word:
                    if len(rlt.matchedIds) > 3:
                        continue
                    # print(f"Match found for substring: '{substring}'")
                    # print(rlt.matchedIds)
                    result.extend(rlt.matchedIds)
            else:
                break
    return result

def init_trie():
    RorDataPath = '1.34_extracted_ror_data.csv'
    with open(RorDataPath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            process_line(row)

if __name__ == "__main__":
    init_trie()
    file_path = './samples/2201.00001v1.txt'  
    print(test_paper(file_path))