import os
from test.tester import Tester
from extractors.trie_extractor import TrieExtractor

# Define required file paths.
scopus_csv_path = os.path.join("data", "2311_scopus_17416.csv")
text_folder_path = os.path.join("data", "2311_text")
default_output_dir = os.path.join("data", "2311_scopus_17416")

# Initialize your extractor (example: TrieExtractor).
extractor = TrieExtractor(
    data_path=os.path.join("data", "1.34_extracted_ror_data.csv"),
    common_words_path=os.path.join("data", "common_english_words.txt")
)

extractor.extract_from_csv(scopus_csv_path, text_folder_path, default_output_dir)