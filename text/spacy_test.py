import spacy
from pathlib import Path

nlp = spacy.load("en_core_web_sm")

def get_possible_institution(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()
        contents = file_contents.split("\u000C")[0]
        
        doc = nlp(contents)
        institutions = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        return institutions

if __name__ == "__main__":
    directory_path = './papers/' 
    # Get a list of all file names in the directory
    path = Path(directory_path)
    file_names = [f.name for f in path.iterdir() if f.is_file()]

    file_names.sort()

    # print(file_names)

    for file_name in file_names:
        full_file_path = "./papers/" + file_name
        result = get_possible_institution(full_file_path)
        print(full_file_path)
        print(result)
        print("\n")