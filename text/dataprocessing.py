import compare
import csv
import re
nameMap = {}
trie = compare.Trie()
commonWords = compare.Trie()

def normalization(s:str):
    return (s.upper().replace("-", " ").replace("–", " ").replace("\"","").replace(",","").strip())
def process_line(elements):
    id = elements[0]
    official = elements[1]
    aliases = elements[2].split(';')
    names = []
    names.append(official)
    names.extend(aliases)
    c = 0
    for name in names:
        if name != '':
            name = normalization(name)
            # filter out the alasis
            if (c==0 or len(name) > 11):
                if (not commonWords.search(name) or not commonWords.search(name).is_word) and (name != "ORCID") and ("FOUND" not in name) and ("FUND" not in name):
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
    text = text.replace("∗","")
    text = re.sub(r'[^A-Za-z0-9 ]', '', text) 
    #print(text)
    # with open('paper.txt', 'a', encoding='utf-8') as file:
    #     file.write(text)
    #     file.write("\n")  # 如果需要在字符串后添加换行符
    #     file.write("-------------------------------------------------------------------------------------------------\n")

    result = set()
    words = text.split()
    
    # Iterate over possible lengths from max_len down to min_len
    for i in range(len(words) - 1):  # Outer loop for starting index
        for n in range(2, min(10, len(words) - i), 1):  # Inner loop for sub-sentence length
            substring = ' '.join(words[i:i+n])  # Join the n contiguous words into a sub-sentence
            rlt = trie.search(substring)
            if rlt and rlt.is_word and len(rlt.matchedIds) <= 1:
                result.update(rlt.matchedIds)
                break
            if(rlt):
                continue
            else:
                break
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