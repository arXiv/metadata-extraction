

# LaTeX Institution Extraction and ROR Matching Pipeline

This project extracts institution affiliations from LaTeX source files, processes them, and matches them to [ROR (Research Organization Registry)](https://ror.org/) entries. It is designed to evaluate the affiliation extraction accuracy for academic papers.

## Overview

- Extract LaTeX source files from `.zip` archives.
- Parse pre-abstract sections to extract institution macros.
- Match extracted institutions to ROR records via API.
- Evaluate the extraction against ground truth ROR IDs.

## Workflow

1. **Preprocessing**
   - Extract the main `.tex` file from each paper.
   - Parse LaTeX content before the abstract.
   - If no abstract found, fallback to using the first 1/3 content.

2. **Macro Extraction**
   - Detect institution macros like `\affiliation`, `\institute`, `\address`, etc.
   - If macros are missing, fallback to using raw pre-abstract text.

3. **Affiliation Matching**
   - Clean LaTeX text and standardize institution names.
   - Query ROR API and cache the matched results.
   - Smart matching based on top candidates and exact substring presence.

4. **Evaluation**
   - Compare extracted RORs against ground truth.
   - Paper-level and affiliation-level accuracy computation.
   - Handle parent-child ROR relationships when judging correctness.

## Folder Structure

```
data/
    2311_with_ror.csv        # Ground truth ROR data
    1.34_extracted_ror_data.csv  # ROR Trie data for extractor
    common_english_words.txt    # Common words for filtering
tagged_outputs/
    all_extracted_tags_cleaned.txt  # Extracted LaTeX macros content
2311_tex.zip                # Raw LaTeX paper archive
output.txt                  # Extracted pre-abstract content
filtered_files_with_content_macro.txt # Filtered valid papers
institution_output_with_ror.json # Predicted ROR results
final_affiliations_2000_parallel.json # Parallel results to compare
evaluation_details.json      # Detailed evaluation results
```

## Setup

- Python 3.8+
- Install dependencies:

```bash
pip install pandas tqdm requests texsoup pylatexenc spacy tenacity
python -m spacy download en_core_web_sm
```

## Key Scripts

- `source_from_zip()` — Find and extract main LaTeX file.
- `extract_before_abstract()` — Capture pre-abstract text.
- `extract_and_store_tags()` — Parse macros or fallback to full content.
- `query_ror()` — Match institution names to ROR via API.
- `is_match()` — Smart ROR matching considering parent/child relations.
- Evaluation scripts — Accuracy computation at paper and affiliation levels.

## Outputs

- `institution_output_with_ror.json`: Your method's extracted RORs.
- `evaluation_details.json`: Detailed paper-by-paper evaluation.
- Paper-level and affiliation-level accuracy statistics printed.

---

Would you also like me to help you generate a `.md` file **ready for download** directly? 🎯
Or a **slightly longer** one with screenshots/example JSON structure inside? (some people prefer that) — just tell me!