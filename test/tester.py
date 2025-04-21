import os
import json
import pandas as pd
from collections import Counter

class Tester:
    def __init__(
        self,
        data_root: str,
        ground_truth_filename: str = "vip_groundTruth.json",
        predicted_filename: str   = "vip_result_combined_v3.json",
        mismatches_filename: str  = "mismatches.csv"
    ):
        """
        :param data_root:               Path to the folder containing your JSON files,
                                        e.g. "data/2311_scopus_17416"
        :param ground_truth_filename:   Name of the ground‑truth JSON file in that folder
        :param predicted_filename:      Name of the predicted‑results JSON file in that folder
        :param mismatches_filename:     Name of the CSV file to save mismatches
        """
        gt_path   = os.path.join(data_root, ground_truth_filename)
        pred_path = os.path.join(data_root, predicted_filename)
        self.mismatches_csv_path = os.path.join(data_root, mismatches_filename)

        with open(gt_path,   'r') as f:
            self.ground_truth = json.load(f)
        with open(pred_path, 'r') as f:
            self.predicted    = json.load(f)

    def evaluate(self):
        """
        Compare ground truth vs. predicted ROR IDs.

        :returns: (metrics, mismatches)
          - metrics: dict with
              total_ground_truth_ROR_IDs,
              correct_extractions,
              wrong_extractions,
              accuracy,
              wrong_extraction_rate
          - mismatches: list of dicts, each with
              ArXiv Id,
              Ground Truth ROR IDs,
              Extracted ROR IDs,
              Missing ROR IDs,
              Extra ROR IDs
        """
        total, correct, wrong = 0, 0, 0
        mismatches = []

        for paper_id, gt_val in self.ground_truth.items():
            # Normalize ground truth to a set
            gt_set = set(gt_val) if isinstance(gt_val, list) else ({gt_val} if gt_val else set())
            total += len(gt_set)

            # Normalize predicted to a set
            res_val = self.predicted.get(paper_id, [])
            extracted_set = set(res_val) if isinstance(res_val, list) else ({res_val} if res_val else set())

            correct += len(gt_set & extracted_set)
            wrong   += len(extracted_set - gt_set)

            missing = gt_set - extracted_set
            extra   = extracted_set - gt_set
            if missing or extra:
                mismatches.append({
                    'ArXiv Id':               paper_id,
                    'Ground Truth ROR IDs':   sorted(gt_set),
                    'Extracted ROR IDs':      sorted(extracted_set),
                    'Missing ROR IDs':        sorted(missing),
                    'Extra ROR IDs':          sorted(extra),
                })

        accuracy              = correct / total if total else 0.0
        wrong_extraction_rate = wrong   / total if total else 0.0

        metrics = {
            'total_ground_truth_ROR_IDs': total,
            'correct_extractions':        correct,
            'wrong_extractions':          wrong,
            'accuracy':                   accuracy,
            'wrong_extraction_rate':      wrong_extraction_rate,
        }

        return metrics, mismatches

    def save_mismatches_to_csv(self, mismatches):
        """
        Save mismatches to a CSV file at self.mismatches_csv_path.
        """
        df = pd.DataFrame(mismatches)
        df.to_csv(self.mismatches_csv_path, index=False)
        print(f"Mismatched cases CSV saved as {self.mismatches_csv_path}")

    def get_top_common_mismatches(self, mismatches, top_n=5):
        """
        Get top N most common missing and extra ROR IDs.

        :param mismatches: list of mismatch dicts returned by evaluate()
        :param top_n:      number of top items to return
        :returns:          (most_common_missing, most_common_extra)
        """
        missing_counter = Counter()
        extra_counter   = Counter()
        for row in mismatches:
            missing_counter.update(row['Missing ROR IDs'])
            extra_counter.update(row['Extra ROR IDs'])
        most_common_missing = missing_counter.most_common(top_n)
        most_common_extra   = extra_counter.most_common(top_n)
        return most_common_missing, most_common_extra

# Example usage:
if __name__ == "__main__":
    tester = Tester("data/2311_scopus_17416")
    metrics, mismatches = tester.evaluate()

    print("Metrics:", metrics)
    print(f"Number of mismatches: {len(mismatches)}")

    # Save mismatches
    tester.save_mismatches_to_csv(mismatches)

    # Show top common mismatches
    top_missing, top_extra = tester.get_top_common_mismatches(mismatches, top_n=5)
    print("Top missing ROR IDs:", top_missing)
    print("Top extra ROR IDs:  ", top_extra)
