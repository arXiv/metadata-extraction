import csv

def extract_columns(input_file, output_file, selected_columns):
    extracted_data = []

    with open(input_file, 'r') as file, open(output_file, 'w', newline='') as output_csv:
        reader = csv.DictReader(file)
        writer = csv.DictWriter(output_csv, fieldnames=selected_columns)

        writer.writeheader()
        
        for row in reader:
            selected_data = {col: row[col] for col in selected_columns}
            writer.writerow(selected_data)

# Example usage
csv_file = 'v1.33-2023-09-21-ror-data.csv'  # Replace with the path to your CSV file

columns = ['id', 'name', 'aliases', 'acronyms']  # Replace with the names of the columns you want to extract
output_file = "extracted_ror_data.csv"

extract_columns(csv_file, output_file, columns)