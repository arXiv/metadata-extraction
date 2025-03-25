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
                    if name.endswith('S') and "UNIVERSITY" in name:
                        self.trie.insert(name[:-1], id)
                    # If name starts with "THE", also insert name without the beginning "THE"
                    if name.startswith("THE ") and len(name.split()) >= 3:
                        name_without_the = " ".join(name.split()[1:])
                        self.trie.insert(name_without_the, id)


    def extract_affiliations_from_content(self, text: str) -> set:
        result = set()
        text = text.upper()
        text = text.replace("Univ.", "University")
        text = text.replace(",", "")
        text = text.replace("-\n", "")
        text = text.replace("\n", " ")
        text = text.replace("-", "")
        text = text.replace("  ", " ")
        text = text.replace("  ", " ")
        text = text.replace("∗", "")
        text = text.replace(".", "")
        # text = re.sub(r'[^A-Za-z0-9 ]', '', text) 
        words = text.split()
        
        # Iterate through all starting positions in the text
        for i in range(len(words)):
            best_match = None  # Track the longest valid match from this starting position
            # Check sub-sentences of length 1 up to 10 (or until the end of the words list)
            for n in range(1, min(10, len(words) - i) + 1):
                substring = ' '.join(words[i:i + n])
                rlt = self.trie.search(substring)
                # If no match is found and we're at the first word, try dropping its first character
                if not rlt and n >= 1:
                    leading_word = words[i]
                    if len(leading_word) > 1:
                        # Create an alternative version for the first word
                        alt_leading_word = leading_word[1:]
                        alt_words = [alt_leading_word] + words[i+1:i+n]
                        alt_substring = ' '.join(alt_words)
                        rlt = self.trie.search(alt_substring)
                # If still no match, break out (since longer substrings likely won’t match either)
                if not rlt:
                    break  
                # Record the best match if the result is a valid word (based on your matching criteria)
                if rlt.is_word and (len(rlt.matchedIds) <= 1):
                    best_match = rlt  # Continue to see if a longer substring produces a better match
            if best_match:
                result.update(best_match.matchedIds)
        
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
