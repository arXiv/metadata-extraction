import requests
import urllib.parse

ROR_API_ENDPOINT = "https://api.dev.ror.org/organizations"
ES_RESERVED_CHARS = ["+", "-", "&", "|", "!", "(", ")", "{", "}", "[", "]", "^", '"', "~", "*", "?", ":", "\\", "/"]

def search_institution(name):
    for char in ES_RESERVED_CHARS:
        name = name.replace(char, "\\" + char)
    
    params = {'query': name}
    response = requests.get(f"{ROR_API_ENDPOINT}?{urllib.parse.urlencode(params)}").json()
    print(response['items'][0]['country']['country_name'])
    if response['number_of_results'] > 0:
        best_match = response['items'][0]['id']
        return best_match
    
    return "No match found"

best_match = search_institution("Politechnika Krakowska")
print(best_match)
