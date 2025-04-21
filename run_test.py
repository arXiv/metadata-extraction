import os
from test.tester import Tester

tester = Tester("data/2311_scopus_17416", "vip_groundTruth.json", "vip_result_combined.json")
metrics, mismatches = tester.evaluate()

print("Metrics:", metrics)
print(f"Number of mismatches: {len(mismatches)}")