# Institution Name Extractor for arXiv Papers

This project extracts institution names from arXiv papers using two different methods:
- **TrieExtractor**: Uses a prefix trie data structure to store institution names, and then performs exact matching with a sliding window approach over the paper text. This method leverages a CSV file containing institution data and a list of common English words to help filter out non-institutional terms.
- **LLMExtractor**: Leverages a language model-based approach.

## Prerequisites

- **Python**
- Required data files:
  - `data/1.34_extracted_ror_data.csv` (institution data for TrieExtractor)
  - `data/common_english_words.txt` (blacklist of common words)
  - A sample arXiv text file (e.g., `data/2201_00_text/2201.00001v1.txt`)

## Usage

Below is the code snippet that shows how to use the extractor:

```python
from extractors.trie_extractor import TrieExtractor
from extractors.llm_extractor import LLMExtractor
from utils.file_reader import read_file

def main(file_path: str, method: str = "trie"):
    text = read_file(file_path)

    if method == "trie":
        extractor = TrieExtractor(
            data_path="data/1.34_extracted_ror_data.csv", 
            common_words_path="data/common_english_words.txt"
        )
    elif method == "llm":
        extractor = LLMExtractor()
    else:
        raise ValueError("Unsupported extraction method")

    affiliations = extractor.extract_affiliations(text)
    print(affiliations)

if __name__ == "__main__":
    main("data/2201_00_text/2201.00001v1.txt", method="trie")
```

## Evaluation

The evaluation of the extractor is performed in two key steps:

1. **Extract Ground Truth:**  
   Scopus papers are already annotated with institution names. By matching the Scopus ID to ROR IDs, the process generates a `groundTruth.json` file (for example, under `data/2201.00_scopus_931`). In this JSON file, each key is an arXiv ID and the corresponding value is a list of institution names.

2. **Run Extraction:**  
   The extraction process runs over the arXiv paper texts and generates a `result.json` file. Here, the key is the arXiv ID and the value is a list of institution names extracted from the text.

By comparing `result.json` and `groundTruth.json`, the following metrics are calculated:
- **Accuracy:** The proportion of correctly extracted institution names compared to the ground truth.
- **Wrong Extraction Rate:** The proportion of extraction errors relative to the total ground truth.

Additionally, a comprehensive CSV file is generated containing all mismatched cases. This CSV includes the following columns:
- **ArXiv Id**
- **Ground Truth ROR IDs**
- **Extracted ROR IDs**
- **Missing ROR IDs**
- **Extra ROR IDs**

Below is the complete code snippet illustrating these steps:

```python
import os
from test.tester import Tester
from extractors.trie_extractor import TrieExtractor

# Define required file paths.
scopus_csv_path = os.path.join("data", "2201.00_scopus_931.csv")
text_folder_path = os.path.join("data", "2201_00_text")
mapping_csv_path = os.path.join("matching_data", "matched_results_ror_api.csv")
blacklist_path = os.path.join("data", "blacklist_parent_organizations.txt")

# Initialize your extractor (example: TrieExtractor).
extractor = TrieExtractor(
    data_path=os.path.join("data", "1.34_extracted_ror_data.csv"),
    common_words_path=os.path.join("data", "common_english_words.txt")
)

# Instantiate the tester.
tester = Tester(
    scopus_csv_path=scopus_csv_path,
    extractor=extractor,
    text_folder_path=text_folder_path,
    paper_id_column="ArXiv Id"
)

# Step 1: Extract Ground Truth
# Scopus papers are annotated with institution names, which are matched to ROR IDs.
# This generates a groundTruth.json file (e.g., under data/2201.00_scopus_931) where the key is the arXiv id
# and the value is a list of institution names.
tester.extract_ground_truth(
    mapping_csv_path=mapping_csv_path,
    blacklist_path=blacklist_path,
    institution_col="Primary Org Name"
)

# Step 2: Run Extraction
# This step extracts institution names from the paper texts and generates a result.json file,
# where each key is the arXiv id and the value is a list of institution names.
result_data = tester.run_extraction()

# Compare extraction results with ground truth.
metrics, mismatches = tester.compare_results(result_data)

# Display evaluation metrics.
print("Evaluation Metrics:")
print("Total ground truth ROR IDs:", metrics['total_ground_truth_ROR_IDs'])
print("Correct extractions:", metrics['correct_extractions'])
print("Wrong extractions:", metrics['wrong_extractions'])
print("Accuracy: {:.2%}".format(metrics['accuracy']))
print("Wrong extraction rate: {:.2%}".format(metrics['wrong_extraction_rate']))

# Save mismatches to CSV.
tester.save_mismatches_to_csv(mismatches)

# Report the top 5 most common missing and extra ROR IDs.
most_common_missing, most_common_extra = tester.get_top_common_mismatches(mismatches, top_n=5)
print("\nMost frequent missing ROR IDs (Top 5):")
for ror_id, count in most_common_missing:
    print(f"ROR ID: {ror_id}, Count: {count}")
print("\nMost frequent extra ROR IDs (Top 5):")
for ror_id, count in most_common_extra:
    print(f"ROR ID: {ror_id}, Count: {count}")
```


