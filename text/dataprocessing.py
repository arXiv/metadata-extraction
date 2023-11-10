import compare
import csv

nameMap = {}
trie = compare.Trie()
commonWords = compare.Trie()

def process_line(elements):
    id = elements[0]
    # names = elements[1:]
    # for name in names:
    #     if name != '':

    # only use the full name to compare

    name = elements[1].upper()
    name = name.replace("-", " ")
    name = name.replace("–", " ")
    # if it is not a common english word
    if not commonWords.search(name) or not commonWords.search(name).is_word:
        trie.insert(name, id)

def test_paper(file_path,jdugeFirst: bool):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()

    contents = file_contents.split("\u000C")

    if jdugeFirst:
        text = contents[0]
    else:
        text = contents[-2]
    text = text.replace("Univ.", "University")
    text = text.upper()
    text = text.replace(",", "")
    text = text.replace("\n", " ")
    text = text.replace("-", "")
    text = text.replace("  ", " ")

    result = set()
    i = 0
    while i < len(text):
        for j in range(i+1, len(text)+1):
            substring = text[i:j]
            #print("check string:"+substring)
            rlt = trie.search(substring)
            if rlt:
                if rlt.is_word:
                    if len(rlt.matchedIds) > 3:
                        continue
                    print(f"Match found for substring: '{substring}'")
                    print(rlt.matchedIds)
                    result.update(rlt.matchedIds)
            else:
                break
        while text[i] != ' ':
            i += 1
        i += 1
    return result

def init_trie():
    # build trie of common english words
    CommonEnglishWords = './addtdata/common englist words.txt'
    with open(CommonEnglishWords, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                if int(parts[1]) >= 0:
                    commonWords.insert(parts[0].upper(), 0)

    RorDataPath = '1.34_extracted_ror_data.csv'
    with open(RorDataPath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            process_line(row)


if __name__ == "__main__":
    init_trie()
    file_path = './samples/2201.00004v1.txt'
    testResult = test_paper(file_path,True)
    if not testResult:
        testResult = test_paper(file_path,False)
    print(testResult)


def getresult(file_path):
    testResult = test_paper(file_path, True)
    if not testResult:
        testResult = test_paper(file_path, False)
    return testResult