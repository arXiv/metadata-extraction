import os
import json
import pandas as pd
from collections import Counter
from tqdm import tqdm

# Import extractor and file reader functions.
from extractors.trie_extractor import TrieExtractor
from utils.file_reader import read_file

class GenericTester:
    """
    Tester for extraction tasks.
    - Extracts ground truth from a CSV.
    - Runs extractor on text files.
    - Compares results to ground truth.

    Parameters:
        scopus_csv_path (str): CSV file with paper data.
        extractor (object): Has extract_affiliations(text) method.
        text_folder_path (str): Folder with paper text files.
        paper_id_column (str): CSV column for paper ID (default "ArXiv Id").
        ground_truth_path (str, optional): JSON path for ground truth.
        result_path (str, optional): JSON path for results.
        mismatches_csv_path (str, optional): CSV path for mismatches.
    """
    def __init__(self, scopus_csv_path, extractor, text_folder_path, paper_id_column="ArXiv Id",
                 ground_truth_path=None, result_path=None, mismatches_csv_path=None):
        self.scopus_csv_path = scopus_csv_path
        self.extractor = extractor
        self.text_folder_path = text_folder_path
        self.paper_id_column = paper_id_column
        
        # Set output directory from CSV path.
        base_dir = os.path.dirname(scopus_csv_path)
        base_name = os.path.splitext(os.path.basename(scopus_csv_path))[0]
        default_output_dir = os.path.join(base_dir, base_name)
        os.makedirs(default_output_dir, exist_ok=True)
        
        # Set default file paths.
        self.ground_truth_path = ground_truth_path or os.path.join(default_output_dir, "groundTruth.json")
        self.result_path = result_path or os.path.join(default_output_dir, "result.json")
        self.mismatches_csv_path = mismatches_csv_path or os.path.join(default_output_dir, "mismatched_cases.csv")
        
        self.ground_truth_data = None
        if os.path.exists(self.ground_truth_path):
            self.ground_truth_data = self._load_json(self.ground_truth_path)
    
    def _load_json(self, file_path):
        """Load JSON data."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def extract_ground_truth(self, mapping_csv_path, blacklist_path, institution_col="Primary Org Name"):
        """
        Extract ground truth from the CSV and merge with a mapping file.

        Filtering:
          - Exclude blacklisted institutions.
          - Exclude institutions with both "university" and "system".
          - Exclude institutions containing "Government of India".

        Groups non-null 'ROR ID's by paper ID.

        Parameters:
            mapping_csv_path (str): CSV with ROR mappings.
            blacklist_path (str): Text file with blacklisted organizations.
            institution_col (str): Institution name column (default "Primary Org Name").

        Returns:
            dict: Mapping of paper ID to list of ROR IDs.
        """
        df = pd.read_csv(self.scopus_csv_path)
        
        # Read blacklist.
        with open(blacklist_path, "r", encoding="utf-8") as f:
            blacklist = [line.strip() for line in f if line.strip()]
        blacklist_lower = [org.lower() for org in blacklist]
        
        # Create filters.
        mask_blacklist = df[institution_col].str.lower().isin(blacklist_lower)
        mask_university_system = (
            df[institution_col].str.lower().str.contains('university', na=False) &
            df[institution_col].str.lower().str.contains('system', na=False)
        )
        mask_govt_india = df[institution_col].str.lower().str.contains('government of india', na=False)
        mask_remove = mask_blacklist | mask_university_system | mask_govt_india
        
        # Remove unwanted records.
        df_filtered = df[~mask_remove].copy()
        df_filtered.reset_index(drop=True, inplace=True)
        
        # Merge with mapping file.
        mapping_df = pd.read_csv(mapping_csv_path)
        merged_data = pd.merge(
            df_filtered,
            mapping_df,
            on='Primary Org Id',
            how='left'
        )
        
        # Group ROR IDs by paper.
        ground_truth = merged_data.groupby('ArXiv Id')['ROR ID'].apply(lambda x: x.dropna().tolist()).to_dict()
        
        # Save ground truth JSON.
        with open(self.ground_truth_path, 'w') as f:
            json.dump(ground_truth, f, indent=4)
        print(f"Ground truth JSON saved as '{self.ground_truth_path}'.")
        
        self.ground_truth_data = ground_truth
        return ground_truth
    
    def run_extraction(self):
        """
        Run the extractor on each paper's text file.

        Returns:
            dict: Mapping of paper ID to extracted ROR IDs.
        """
        df = pd.read_csv(self.scopus_csv_path)
        tqdm.pandas(desc="Extracting ROR IDs")
        df['Extracted ROR ID'] = df[self.paper_id_column].progress_apply(self._extract_ror_id)
        result_data = df.set_index(self.paper_id_column)['Extracted ROR ID'].to_dict()
        
        with open(self.result_path, 'w') as f:
            json.dump(result_data, f, indent=4, sort_keys=True)
        print(f"Extraction complete. JSON saved as {self.result_path}.")
        return result_data
    
    def _extract_ror_id(self, paper_id):
        """Extract ROR ID(s) from the text file for a given paper ID."""
        file_path = os.path.join(self.text_folder_path, f"{paper_id}.txt")
        try:
            text = read_file(file_path)
            affiliations = self.extractor.extract_affiliations(text)
            return list(affiliations) if isinstance(affiliations, set) else affiliations
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
    
    def compare_results(self, result_data):
        """
        Compare extracted results to ground truth.

        Returns:
            tuple: Metrics dictionary and list of mismatched cases.
        """
        if self.ground_truth_data is None:
            raise ValueError("Ground truth data is not available. Run extract_ground_truth() first.")
        
        total_ror_ids = 0
        correct_extractions = 0
        wrong_extractions = 0
        mismatches = []
        
        for paper_id, gt_val in self.ground_truth_data.items():
            # Normalize ground truth to a set.
            gt_set = set(gt_val) if isinstance(gt_val, list) else {gt_val} if gt_val else set()
            total_ror_ids += len(gt_set)
            
            # Normalize extraction result to a set.
            res_val = result_data.get(paper_id)
            extracted_set = set(res_val) if isinstance(res_val, list) else {res_val} if res_val else set()
            
            correct_extractions += len(gt_set & extracted_set)
            wrong_extractions += len(extracted_set - gt_set)
            
            missing = gt_set - extracted_set
            extra = extracted_set - gt_set
            if missing or extra:
                mismatches.append({
                    'ArXiv Id': paper_id,
                    'Ground Truth ROR IDs': sorted(list(gt_set)),
                    'Extracted ROR IDs': sorted(list(extracted_set)),
                    'Missing ROR IDs': sorted(list(missing)),
                    'Extra ROR IDs': sorted(list(extra))
                })
        
        accuracy = correct_extractions / total_ror_ids if total_ror_ids > 0 else 0
        wrong_extraction_rate = wrong_extractions / total_ror_ids if total_ror_ids > 0 else 0
        
        metrics = {
            'total_ground_truth_ROR_IDs': total_ror_ids,
            'correct_extractions': correct_extractions,
            'wrong_extractions': wrong_extractions,
            'accuracy': accuracy,
            'wrong_extraction_rate': wrong_extraction_rate
        }
        return metrics, mismatches
    
    def save_mismatches_to_csv(self, mismatches):
        """Save mismatches to a CSV file."""
        df = pd.DataFrame(mismatches)
        df.to_csv(self.mismatches_csv_path, index=False)
        print(f"Mismatched cases CSV saved as {self.mismatches_csv_path}")
    
    def get_top_common_mismatches(self, mismatches, top_n=5):
        """
        Get top N common missing and extra ROR IDs.

        Returns:
            tuple: Lists of most common missing and extra ROR IDs.
        """
        missing_counter = Counter()
        extra_counter = Counter()
        for row in mismatches:
            missing_counter.update(row['Missing ROR IDs'])
            extra_counter.update(row['Extra ROR IDs'])
        most_common_missing = missing_counter.most_common(top_n)
        most_common_extra = extra_counter.most_common(top_n)
        return most_common_missing, most_common_extra
