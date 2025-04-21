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

Below is the code snippet that shows how to extract institutions from a specific file:

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

Below is the code snippet that shows how to extract institutions in batch from a csv file:

```python
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
```
 

## Basic Evaluation

Scopus papers are already annotated with institution names. By matching the Scopus ID to ROR IDs with `test/extract_groundTruth.ipynb`, the process generates a `groundTruth.json` file (for example, under `data/2201.00_scopus_931`). 
In this JSON file, each key is an arXiv ID and the corresponding value is a list of institution names.


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

tester = Tester("data/2311_scopus_17416", "groundTruth.json", "result_trie.json")
metrics, mismatches = tester.evaluate()

print("Metrics:", metrics)
print(f"Number of mismatches: {len(mismatches)}")
```

## Basic Evaluation 
To further evaluate results from LLM or combined results from LLM and Trie, run `test/combine_results.ipynb` and `test/combine_results_vip.ipynb`. And use code snippet below to evaluate the result:

```python
import os
from test.tester import Tester

tester = Tester("data/2311_scopus_17416", "vip_groundTruth.json", "vip_result_combined.json")
metrics, mismatches = tester.evaluate()

print("Metrics:", metrics)
print(f"Number of mismatches: {len(mismatches)}")
```
