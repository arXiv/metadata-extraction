import os
from test.tester import GenericTester
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
tester = GenericTester(
    scopus_csv_path=scopus_csv_path,
    extractor=extractor,
    text_folder_path=text_folder_path,
    paper_id_column="ArXiv Id"
)

# Extract the ground truth.
tester.extract_ground_truth(
    mapping_csv_path=mapping_csv_path,
    blacklist_path=blacklist_path,
    institution_col="Primary Org Name"
)

# Run extraction.
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
