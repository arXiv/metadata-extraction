import os
import csv
import json
import re
import pandas as pd
from tqdm import tqdm
from utils import trie
from utils.normalization import normalize_text
from utils.build_blacklist import build_blacklist
from utils.file_reader import read_file
class TrieExtractor:
    def __init__(self, 
                 data_path: str, 
                 common_words_path: str,
                 paper_id_column: str = "paper_id", 
                 file_path_column: str = "file_path",
                 result_path: str = "extraction_result.json"):
        """
        Initialize the TrieExtractor instance.

        Args:
            data_path (str): Path to the CSV file containing whitelist data.
            common_words_path (str): Path to the CSV file for building the blacklist.
            paper_id_column (str): Name of the CSV column containing unique paper IDs.
            file_path_column (str): Name of the CSV column containing file paths to paper text files.
            result_path (str): Path to save the JSON file with extraction results.
        """
        self.trie = trie.Trie()
        self.common_words = build_blacklist(common_words_path)
        self.paper_id_column = paper_id_column
        self.file_path_column = file_path_column
        self.result_path = result_path

        # Load whitelist and auxiliary data into the trie.
        self.load_whitelist(data_path)
        self.load_data(data_path)

    def load_whitelist(self, data_path: str):
        """
        Load whitelist entries from a CSV file into the trie.
        Each row is expected to have the structure: [id, string, ...].
        """
        with open(data_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Insert using row[1] as the text and row[0] as its identifier.
                self.trie.insert(row[1], row[0])

    def load_data(self, data_path: str):
        """
        Load additional data from the CSV file and insert into the trie.
        This typically includes official names and any aliases.
        """
        with open(data_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.insertTrie(row)

    def insertTrie(self, elements):
        """
        Insert an entry with its various names (official and aliases) into the trie.

        Args:
            elements (list): List of elements where:
                             elements[0] is the identifier,
                             elements[1] is the official name, and
                             elements[2] contains alias names separated by ';'.
        """
        id = elements[0]
        official = elements[1]
        aliases = elements[2].split(';')
        names = [official] + aliases
        for c, name in enumerate(names):
            name = normalize_text(name)
            # Only insert if the name is non-empty, contains at least 2 words,
            # and meets additional conditions (like length and exclusion from common words).
            if name and len(name.split()) >= 2 and (c == 0 or len(name) > 11):
                if not self.common_words.search(name) and "FOUND" not in name:
                    self.trie.insert(name, id)
                    # If the name ends with 'S' and contains "UNIVERSITY", also insert without the trailing 'S'
                    if name.endswith('S') and "UNIVERSITY" in name:
                        self.trie.insert(name[:-1], id)
                    # If the name starts with "THE", insert an additional variant without "THE"
                    if name.startswith("THE ") and len(name.split()) >= 3:
                        name_without_the = " ".join(name.split()[1:])
                        self.trie.insert(name_without_the, id)

    def extract_affiliations_from_content(self, text: str) -> set:
        """
        Extract affiliation identifiers from a given text using the trie.

        Args:
            text (str): The text content to process.

        Returns:
            set: A set of affiliation identifiers found in the text.
        """
        result = set()
        text = text.upper()
        text = text.replace("Univ.", "University")
        text = text.replace(",", "")
        text = text.replace("-\n", "")
        text = text.replace("\n", " ")
        text = text.replace("-", "")
        text = text.replace("  ", " ")
        text = text.replace("∗", "")
        text = text.replace(".", "")
        words = text.split()
        
        # Iterate over all possible starting positions in the text.
        for i in range(len(words)):
            best_match = None  # Record the longest valid match from the starting word.
            # Check possible substrings up to a length of 10 words.
            for n in range(1, min(10, len(words) - i) + 1):
                substring = ' '.join(words[i:i + n])
                rlt = self.trie.search(substring)
                # If no match, try an alternative by dropping the first character of the starting word.
                if not rlt and n >= 1:
                    leading_word = words[i]
                    if len(leading_word) > 1:
                        alt_leading_word = leading_word[1:]
                        alt_words = [alt_leading_word] + words[i+1:i+n]
                        alt_substring = ' '.join(alt_words)
                        rlt = self.trie.search(alt_substring)
                if not rlt:
                    break  
                # Choose the match if it marks the end of a valid word and matches a single ID.
                if rlt.is_word and (len(rlt.matchedIds) <= 1):
                    best_match = rlt
            if best_match:
                result.update(best_match.matchedIds)
        
        return result

    def extract_affiliations(self, file_contents: str) -> set:
        """
        Given the contents of a text file, attempt to extract affiliation IDs.
        It first checks the first page, then the second last, and finally the last page.

        Args:
            file_contents (str): The full text content of the paper.

        Returns:
            set: A set of affiliation identifiers, or an empty set if none are found.
        """
        # Split the text by form feed (page break)
        contents = file_contents.split("\u000C")
        
        # Step 1: Try extracting from the first page
        text = contents[0]
        result = self.extract_affiliations_from_content(text)
        if result:
            return result
        
        # Step 2: If nothing found, try the second last page (if available)
        if len(contents) >= 2:
            text = contents[-2]
            result = self.extract_affiliations_from_content(text)
            if result:
                return result
        
        # Step 3: Finally, try the last page
        if len(contents) >= 1:
            text = contents[-1]
            result = self.extract_affiliations_from_content(text)
            if result:
                return result
        
        return set()
    
    def remove_version(self, key):
        """
        Remove the version suffix (e.g., "v1") from the key.
        This regex matches 'v' followed by one or more digits at the end of the string.
        """
        return re.sub(r'v\d+$', '', key)
    
    def extract_from_csv(self, scopus_csv_path: str, text_folder_path: str, default_output_dir: str):
        """
        Process the Scopus CSV file, extract affiliations from each paper's text file,
        and save a mapping from paper ID to extracted affiliation IDs as a JSON file.

        Args:
            scopus_csv_path (str): Path to the CSV file containing paper metadata.

        Returns:
            dict: Mapping of paper ID to a list of extracted affiliation IDs.
        """
        # Load the CSV file into a DataFrame.
        df = pd.read_csv(scopus_csv_path)
        tqdm.pandas(desc="Extracting ROR IDs")
        self.text_folder_path=text_folder_path

        df['Extracted ROR ID'] = df["ArXiv Id"].progress_apply(self._extract_ror_id)
        result_data = df.set_index("ArXiv Id")['Extracted ROR ID'].to_dict()

        result_path = os.path.join(default_output_dir, "result_trie.json")
        
        result_data = {self.remove_version(key): value for key, value in result_data.items()}

        with open(result_path, 'w') as f:
            json.dump(result_data, f, indent=4, sort_keys=True)
        print(f"Extraction complete. JSON saved as {result_path}.")
        return result_data
    
    def _extract_ror_id(self, paper_id):
        """Extract ROR ID(s) from the text file for a given paper ID."""
        file_path = os.path.join(self.text_folder_path, f"{paper_id}.txt")
        try:
            text = read_file(file_path)
            affiliations = self.extract_affiliations(text)
            return list(affiliations) if isinstance(affiliations, set) else affiliations
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None