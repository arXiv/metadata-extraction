import csv
import pandas as pd

manual_blacklist = [
    "China Scholoarship Council"
]

# Replace 'your_input_file.csv' and 'your_output_file.csv' with the actual file names
input_file = '1.34_extracted_ror_data.csv'
output_file = '1.34_extracted_filtered_ror_data.csv'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(input_file)

# Add a new column 'blacklist' based on the condition
df['blacklist'] = df['name'].apply(
    lambda x: 1 if 'fund' in x.lower().split(' ') or 'foundation' in x.lower().split(' ') else 0
)

# Write the modified DataFrame to a new CSV file
df.to_csv(output_file, index=False)

print("Processing complete. Check", output_file)