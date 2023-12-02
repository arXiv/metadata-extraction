import compare
import csv

trie = compare.Trie()
commonWords = compare.Trie()
full_text = ''
def normalization(s:str):
    return (s.upper().replace("-", " ").replace("–", " ").replace("\"","").replace(",","").strip())
def process_line(elements):
    id = elements[0]
    official = elements[1]
    aliases = elements[2].split(';')
    names = []
    names.append(official)
    #names.extend(aliases)
    c = 0
    for name in names:
        if name != '':
            name = normalization(name)
            # filter out the alasis
            if (c==0 or len(name) > 11):
                if (not commonWords.search(name) or not commonWords.search(name).is_word) and (name != "ORCID") and ("FOUND" not in name) and ("FUND" not in name) and(name != "CHINA SCHOLARSHIP COUNCIL") and name != "EUROPEAN PARLIAMENT":
                    trie.insert(name, id)
                    if (name[-1] == 's' or name[-1] == 'S') and ("university" in name.lower()):
                        trie.insert(name[:-1],id)
        c += 1

def test_paper(file_path, jdugeFirst: bool):
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
    text = text.replace("-\n", "")
    text = text.replace("\n", " ")
    text = text.replace("-", " ")
    text = text.replace("  ", " ")
    text = text.replace("  "," ")
    #print(text)
    # with open('paper.txt', 'a', encoding='utf-8') as file:
    #     file.write(text)
    #     file.write("\n")  # 如果需要在字符串后添加换行符
    #     file.write("-------------------------------------------------------------------------------------------------\n")

    result = set()
    i = 0
    startIdx = 2
    while i < len(text):
        for k in range(i,i+startIdx):
            tempResult = []
            for j in range(k+1, len(text)+1):
                substring = text[k:j]
                #print(substring)
                rlt = trie.search(substring)
                if rlt:
                    if rlt.is_word:
                        if len(rlt.matchedIds) > 1:
                            #get country and conduct fuzzy match on ES
                            continue
                        print(f"Match found for substring: '{substring}'")
                        print(rlt.matchedIds)
                        tempResult.clear()
                        tempResult.extend(rlt.matchedIds)

                else:
                    if len(tempResult) > 0:
                        result.update(tempResult)
                        i = j-1
                    else:
                        while i < len(text) and text[i] != ' ':
                            i += 1
                    break
            if len(tempResult) > 0:
                break
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
                    name = parts[0].upper().replace("-", " ").replace("–", " ")
                    commonWords.insert(name, 0)

    RorDataPath = '1.34_extracted_ror_data.csv'
    with open(RorDataPath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            process_line(row)


if __name__ == "__main__":
    init_trie()
    file_path = 'papers/2201.00555v1.txt'
    testResult = test_paper(file_path,True)
    if not testResult:
        testResult = test_paper(file_path,False)
    print(testResult)


def getresult(file_path):
    testResult = test_paper(file_path, True)
    if not testResult:
        testResult = test_paper(file_path, False)
    return testResult