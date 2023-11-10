import csv
import json

def extract_columns(input_file, output_file, selected_columns):
    extracted_data = []

    with open(input_file, 'r') as file, open(output_file, 'w', newline='') as output_csv:
        reader = csv.DictReader(file)
        writer = csv.DictWriter(output_csv, fieldnames=selected_columns)

        writer.writeheader()
        
        for row in reader:
            selected_data = {col: row[col] for col in selected_columns}
            writer.writerow(selected_data)

def extract_relation(input_file, output_file):
    relation_dict = {}

    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            inst_id = row["id"]
            relation_dict[inst_id] = {}

            relation_inst = row["relationships"]

            if relation_inst == None:
                continue

            for one_relation in relation_inst.split("; "):
                if "Child" in one_relation:
                    relation_dict[inst_id]["Child"] = one_relation.split("Child: ")[1].split(", ")
                elif "Related" in one_relation:
                    relation_dict[inst_id]["Related"] = one_relation.split("Related: ")[1].split(", ")
                elif "Parent" in one_relation:
                    relation_dict[inst_id]["Parent"] = one_relation.split("Parent: ")[1].split(", ")
    
    # Save the dictionary to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(relation_dict, json_file, indent=4)



def get_name_subform():
    # Example usage
    csv_file = 'v1.34-2023-10-12-ror-data.csv'  # Replace with the path to your CSV file

    columns = ['id', 'name', 'aliases', 'acronyms']  # Replace with the names of the columns you want to extract
    output_file = "1.34_extracted_ror_data.csv"

    extract_columns(csv_file, output_file, columns)

def get_relation_json():
    csv_file = 'v1.34-2023-10-12-ror-data.csv'
    output_file = "1.34_relations.json"

    extract_relation(csv_file, output_file)


if __name__ == "__main__":
    get_relation_json()