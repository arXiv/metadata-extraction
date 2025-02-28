from extractors.trie_extractor import TrieExtractor
from extractors.llm_extractor import LLMExtractor
from utils.file_reader import read_file

def main(file_path: str, method: str = "trie"):
    text = read_file(file_path)

    if method == "trie":
        extractor = TrieExtractor(data_path="data/1.34_extracted_ror_data.csv", common_words_path="data/common_english_words.txt")
    elif method == "llm":
        extractor = LLMExtractor()
    else:
        raise ValueError("Unsupported extraction method")

    affiliations = extractor.extract_affiliations(text)
    print(affiliations)

if __name__ == "__main__":
    main("data/2201_00_text/2201.00001v1.txt", method="trie")
