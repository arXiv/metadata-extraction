import csv
import re
from utils import trie
from utils.normalization import normalize_text
from utils.build_blacklist import build_blacklist

class TrieExtractor:
    def __init__(self, data_path: str, common_words_path: str):
        self.trie = trie.Trie()
        self.common_words = build_blacklist(common_words_path)
        self.load_whitelist("data/whitelist.csv")
        self.load_data(data_path)
       
        
    def load_whitelist(self, data_path: str):
        with open(data_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.trie.insert(row[1], row[0])


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
            # Ensure name is non-empty, contains at least 2 words, and meets other conditions
            if name and len(name.split()) >= 2 and (c == 0 or len(name) > 11):
                if not self.common_words.search(name) and "FOUND" not in name:
                    self.trie.insert(name, id)
                    if('UNIVERSITY OF CALIFORNIA' in name):
                        self.trie.insert(name, "https://ror.org/00pjdza24")
                    if name.endswith('S') and "UNIVERSITY" in name:
                        self.trie.insert(name[:-1], id)



    def extract_affiliations_from_content(self, text: str) -> set:
        result = set()
        text = text.upper()
        text = text.replace("Univ.", "University")
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
            for n in range(1, min(10, len(words) - i), 1):  # Inner loop for sub-sentence length
                substring = ' '.join(words[i:i + n])  # Join the n contiguous words into a sub-sentence
                rlt = self.trie.search(substring)
                if rlt and rlt.is_word and (len(rlt.matchedIds) <= 1 or "https://ror.org/00pjdza24" in rlt.matchedIds):
                    result.update(rlt.matchedIds)
                    break
                if rlt:
                    continue
                else:
                    break
        return result

    def extract_affiliations(self, file_contents: str) -> set:
        # Split the file contents by form feed character (page break)
        contents = file_contents.split("\u000C")
        
        # Step 1: Search in the first page
        text = contents[0]
        result = self.extract_affiliations_from_content(text)
        
        if result:
            return result
        
        # Step 2: If no affiliations found in the first page, search the second last page
        if len(contents) >= 2:
            text = contents[-2]  # Second last page
            result = self.extract_affiliations_from_content(text)
            if result:
                return result
        
        # Step 3: If still no affiliations found, search the last page
        if len(contents) >= 1:
            text = contents[-1]  # Last page
            result = self.extract_affiliations_from_content(text)
            if result:
                return result
        
        # If no affiliations are found in any of the pages, return an empty set
        return set()
