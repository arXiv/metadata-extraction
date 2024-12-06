import csv
import re
from utils import trie
from utils.normalization import normalize_text
from utils.common_words import build_common_words_trie

class TrieExtractor:
    def __init__(self, data_path: str, common_words_path: str):
        self.trie = trie.Trie()
        self.common_words = build_common_words_trie(common_words_path)
        self.load_data(data_path)

    def load_data(self, data_path: str):
        with open(data_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.insertTrie(row)

    def insertTrie(self, elements):
        id = elements[0]
        official = elements[1]
        aliases = elements[2].split(';')
        names = [official] + aliases
        for c, name in enumerate(names):
            name = normalize_text(name)
            if name and (c == 0 or len(name) > 11):
                if not self.common_words.search(name) and "FOUND" not in name:
                    self.trie.insert(name, id)
                    if name.endswith('S') and "UNIVERSITY" in name:
                        self.trie.insert(name[:-1], id)

    def extract_affiliations(self, text: str) -> set:
        result = set()
        text = text.split("\u000C")
        text = text[0]
        print(text)
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
        words = text.split()
        for i in range(len(words) - 1):  # Outer loop for starting index
            for n in range(2, min(10, len(words) - i), 1):  # Inner loop for sub-sentence length
                substring = ' '.join(words[i:i + n])  # Join the n contiguous words into a sub-sentence
                rlt = self.trie.search(substring)
                if rlt and rlt.is_word and len(rlt.matchedIds) <= 1:
                    print((substring))
                    result.update(rlt.matchedIds)
                    break
                if rlt:
                    continue
                else:
                    break
        return result
