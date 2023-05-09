import pandas as pd
import numpy as np
import regex as re
import matplotlib.pyplot as plt
import zipfile
import io
from fuzzywuzzy import fuzz
from collections import defaultdict
from TexSoup import TexSoup
import itertools
from geotext import GeoText

# tags 
# key == tag searched during extraction p
# value information category tag most likely belong to. Values of dictionary are not used in algorithm its just there for refenence
tags = {
    "IEEEauthorblockN": "author",
    "IEEEauthorblockA": "department",
    'IEEEcompsocitemizethanks': "all",
    'icmlauthor': 'name',
    'icmlaffiliation': 'institution',
    "affiliation": 'institution',
    'author': 'name',
    'email': 'email',
    'institution': "institution",
    'affiliations': "institution",
    'address': 'institution',
    'name':'author',
    "institute":"institution"
}   

# REGEX PATTERNS
# regex patterns used for imformation retrieval aka extraction functions
# list of words that places name in institution category. other names are classified as author
# detecting names
# PATTERN EXPLANATION
# detecting name of people and places
# \p{Lu}(\p{L}+|\.)(?:\s+\p{Lu}(\p{L}+|\.))* back to back upper case words
# (?:\s+\p{L}[\p{L}\-]{0,5}+){0,2}\s+\p{Lu}(\p{L}+|\.)(?:\s+\p{Lu}(\p{L}+|\.))*)") allows up to 2 lowercase words that are at most 5 characers in length (helpful for getting instiution names that include of, with)
name_pat = re.compile(r"(\p{Lu}(\p{L}+|\.)(?:\s+\p{Lu}(\p{L}+|\.))*(?:\s+\p{L}[\p{L}\-]{0,5}+){0,2}\s+\p{Lu}(\p{L}+|\.)(?:\s+\p{Lu}(\p{L}+|\.))*)")
# detecting emails
email_pat = re.compile(r"\b[\p{Lu}\p{L}0-9._%+-]+@[\p{Lu}\p{L}0-9.-]+\.[\p{Lu}|\p{L}]{2,7}\b")
# detecting location addresses
# EXPLANATION
# (((\p{Lu}\p{L}+\s)?[0-9]{5,7}(,?)(\s\p{Lu}\p{L}+)+)) mutiple captilaized words followed by zip code then more  captilaized words 
# ((\d{1,})[\p{L}\p{Lu}0-9\s]+(\.)?[\p{L}\p{Lu}]+(\s[\p{L}\p{Lu}]+)?(\,)?\s[\p{Lu}]{2}\s[0-9]{5,7})|((\d{1,})[\p{L}\p{Lu}0-9\s]+(\.)?)
        # traditional address format street number, name abbreviation state country zip code
# ((\d{1,})[\p{L}\p{Lu}0-9\s]+(\.)?[\p{L}\p{Lu}]+(\s[\p{L}\p{Lu}]+)?(\,)?\s[\p{Lu}]{2}\s[0-9]{5,7})|((\d{1,})[\p{L}\p{Lu}0-9\s]+(\.)?)
        # traditional address format street number, name abbreviation state country zip code
# ((\d{1,})[\p{LU}\p{L}0-9\s]+(\.)?)  street number and country/ location name then zip code
# ([\p{Lu}\p{L}]+(\s[\p{L}\p{Lu}]+)?(\,)?\s\p{Lu}{2}\s[0-9]{5,6})")  mutiple captilaized words optional commas then zip code
address_pat = re.compile(r"(((\p{Lu}\p{L}+\s)?[0-9]{5,7}(,?)(\s\p{Lu}\p{L}+)+))|((\d{1,})[\p{L}\p{Lu}0-9\s]+(\.)?[\p{L}\p{Lu}]+(\s[\p{L}\p{Lu}]+)?(\,)?\s[\p{Lu}]{2}\s[0-9]{5,7})|((\d{1,})[\p{Lu}\p{L}0-9\s]+(\.)?)|([\p{L}\p{Lu}]+(\s[\p{L}\p{Lu}]+)?(\,)?\s\p{Lu}{2}\s[0-9]{5,6})")
# detect markers. Makers are located next to authors and symbolize other infomation  that they are tied to like institution and emails
# begins and ends with special character
marker_pat = re.compile(r"([{$%^&#@]).*([}$%*#@])")
# files used to distingish author names from institution.
# If extracted name is simular to one of the names in list of organizations (orgs) its considered a institution
org_counts = pd.read_excel(r'arxiv_primary_org_counts_sample.xlsx')
members = pd.read_table('members11.tsv',sep='\t')
institution_list = pd.read_csv("ror.csv")
orgs = set(members['Institution'].unique()).union(set(org_counts['Org Name'].unique()))


# FUNCTION institution_search: checks if extracted info information is similar to list of organizations
# if it is then most likely a instiution and not a author name(returns true)
# extract: string of extracted information found
# orgs: set list of organizations 
def institution_search(extract, orgs):
    for i in orgs:
        if fuzz.token_set_ratio(extract.lower(),i.lower()) > 55:
            print(fuzz.token_sort_ratio(extract,i))
            return True
    return False

# FUNCTION extract_info
# extracts author, institution address and email from soup file based on a single tag name

# saves authors, institutions and other infomation from text and updates extaction dictionaries accordingly

# input:
# soup: texsoup file you want to extract
# tag (string) tag it will search through, mostly likely from tags dictionary
# extracts: previous extracted information that should be concatenated with new extracts found(empty if this is first iteration)
# marker_insti: previous marker institution matchings that should be concatenated with new matchings found (empty if this is first  iteration)
# marker_author: previous marker author matchings that should be concatenated with new matchings found (empty if this is first iteration)

# output:tuple
# output[0] = updated extracts dictionary
# output[1] = markers that are tied to insitutions according to soup text file
# output[2] = markers that are tied to authors according to soup text file


def extract_info(soup,tag,extracts,marker_insti,author_marker):
    
# we assume markers are less than 15 characters so it doesnt get mixed up with other text that match key
    marker_length = 15
    marker_extract = ""
    # tag may occur more than once in file, search through all instances
    groups = list(soup.find_all(tag))
    for group in groups:
        # some files are better broken up by lines some by a key word \and
        cluster = str(group).split('\\and') if  "\\and" in str(group) else  list(group.descendants)
        for j in range(len(cluster)):
            # files formated by \and are type str now
            info = info = cluster[j] if type(cluster[j]) == str else " ".join(str(cluster[j].text).split())  
            # removes comments 
            info = re.sub(r'%(.*)','', info)
            if(len(info) !=0):
                add_extract = ""
                email_extract = ""
                name_extract = ""
             # check for marker on current line.
                marker_extract =  marker_pat.search(str(cluster[j]))[0] if marker_pat.search(str(cluster[j])) and len(marker_pat.search(str(cluster[j]))[0]) < marker_length is not None else marker_extract
            # continues to search for infomation in this line while regex patterns are present
            while address_pat.search(info) or  email_pat.search(info) or name_pat.search(info):
                # check for possible authors, institutions (both in name)  address and emails
                add_extract = address_pat.search(info)
                email_extract = email_pat.search(info)
                name_extract = name_pat.search(info)
                # add extracted information to appropiate dictionary
                if email_extract:
                    extract = email_extract[0]
                    extracts['email'].append(extract)
                elif add_extract:
                    extract = add_extract[0] 
                    extracts['address'].append(extract)
                elif name_extract:
                    extract = name_extract[0]
                    # counts as institution if similar to institutions in our set
                    if institution_search(extract, orgs):
                        extracts['institution'].append(extract)
                        # assumes that marker should come before institution name. if found, this institution has that marker
                        if len(marker_extract) > 0:
                            marker_insti[marker_extract].append(extract)
                    else:
                         # no institutions in our set were similar to this extract, must be a author name
                        extracts['author'].append(extract)
                        # assumes that marker should come after author name
                        if len(marker_extract) > 0 and marker_extract in info and info.index(marker_extract) > info.index(extract):
                            author_marker[extract].append(marker_extract)
                        # checks next line in case marker went to next line
                        elif j+1 < len(cluster):
                            next_info = " ".join(str(cluster[j+1]).replace(",",'').split())  
                            next_marker_extract =  marker_pat.search(next_info)[0] if marker_pat.search(next_info) and len(marker_pat.search(next_info)[0]) < marker_length is not None else ""
                            if len(next_marker_extract ) > 0:
                                author_marker[extract].append(next_marker_extract)
                # removed already found extracted info
                info = info.replace(extract,'')
                # keeps track of all markers found
                # saves all markers found so we can use in matching function
                if len(marker_extract) > 0:
                    extracts['markers'].append(marker_extract.strip())
    return((extracts,marker_insti,author_marker))

# FUNCTION extraction
# get all extractions from soup, 
# iterating through all possible tags in tags dictionary
def extraction(soup):
    extracts = defaultdict(list)
    marker_insti = defaultdict(list)
    author_marker = defaultdict(list)
    marker_author = defaultdict(list)
    soup_str = str(soup)
    for tag in tags.keys():
        if soup.find(tag) is not None:
            extracts, marker_insti, author_marker= extract_info(soup,tag,extracts,marker_insti,marker_author)
    return((extracts,marker_insti,author_marker))


# FUNCTION nearest neighbor: matches authors to institutons and emaik, instututions to their addresses 
# runs on authors if no markers are found for them
# rule: assumes instutition addresses and emails will be located close to the authors they are associated with and after the author name is said (not necessarily right after but in close proximity compared to  other authors)

# input:
# authors list: list of author name (or institutions if need to me matched with address)
# extract_field: extracted information that need to matched  (institutions/addresss/email)
# soup (string) string form of text file
def nearest_neighbor(authors, extract_field, soup):
    author_field = {}
    field_locations_taken = []
    author_dis_field = np.zeros(len(authors))
    for i in extract_field:
        # gets next index location of extracted information. if occurred more than once, get next iteration that not found at yet
        field_location = [j.start() for j in re.finditer(pattern= i, string=soup) if j.start() not in field_locations_taken]
        if len(field_location) > 0:
            field_location = field_location[0]
            field_locations_taken.append(field_location)
            # get how close each authors location is to the extracted string. 
            for idx, author in enumerate(authors):
                distance = ([j.start() for j in re.finditer(pattern= author, string=soup) if j.start() < field_location ])
                distance = sorted(distance,reverse = True)[0] if len(distance) > 0 else 0
                author_dis_field[idx] = distance
            # choose author that is closes to extraction. assumes author must be named before extracted info so index author < extract
            closest_author = authors[np.argmax(author_dis_field)]
            # update dictionary to link author to extract
            if closest_author in author_field:
                author_field[closest_author].append(i)
            else:
                author_field[closest_author] = [i]
    return(author_field)



# FUNCTION create_matchings
# match names to institution and email, institutions to addresses:
# checks for markers to easy matching then  nearest neighbor rule: fields associated with author comes after name of author and is closest to the this authors name compared to other author names

# input:
# extraction_results: output of extract_info function
# soup: soup file
# output:
# output[0]: list of authors in matching (useful for next step)
# output[1]: author_institution dictionary [key] = author name [value] = institution they associate with
# output[2]: insti_address dictionary [key] = institution name [value] = address they associate with
# output[3]: author_email dictionary [key] = author name [value] = email they associate with

def create_matchings(extraction_results, soup):
    author_institution =  defaultdict(list)
    author_email =  defaultdict(list)
    insti_address = defaultdict(list)
    extracts = extraction_results[0]
    marker_insti = extraction_results[1]
    author_marker = extraction_results[2]
    # if authors has markers, link to instituton and emails that have same marker
    for author in author_marker.keys():
        for marker in set(author_marker[author]):
            if author in author_institution:
                author_institution[author].append(marker_insti[marker])
            else:
                author_institution[author] = [marker_insti[marker]]
    unmarked_authors = list(set(extracts['author']) - set(list(author_marker.keys())))
    # string version of soup used for finding index in nearest neighbor
    str_soup = " ".join(str(soup).split())  
    if len(unmarked_authors) > 0:
        # if some authors are not marker, find instituton, address and email based on nearest neighbor
        author_institution.update(nearest_neighbor(unmarked_authors,extracts['institution'],str_soup))
        # for each instituton always find address  based on nearest neighbor
    if extracts["address"]:
        insti_address = nearest_neighbor(list(set(extracts['institution'])),list(set(extracts['address'])),str_soup)
        # for each author always find email based on nearest neighbor
    if extracts["email"]:
        author_email = nearest_neighbor(list(set(extracts['author'])),list(set(extracts['email'])),str_soup)
    return ((list(set(extracts['author'])),author_institution, insti_address,author_email))   


# FUNCTION flat: reformats list to 1D
def flat(lst):
    if lst == None:
        return None
    if lst == []:
        return []
    if type(lst) == str:
        return lst
    lst = np.array(lst)
    print("NEW")
    print(lst)
    return list(itertools.chain.from_iterable(lst)) if type(lst[0]) != np.str_  else lst.flatten()


# FUNCTION save_extractions: saves extractions as a set
# output[0] set of extracted authors
# output[1] set of extracted institutions
# output[2] set of extracted addresses
# output[3] set of extracted emails
def save_extractions(extraction_results):
    return (set(extraction_results[0]['author']),set(extraction_results[0]['institution']),set(extraction_results[0]['address']),set(extraction_results[0]['email']))


# final matching dictionary
matches_dict = {}

#FUNCTION  update_matching_dict: update matching dictionary to add matchings found in this file(soup)
# input: soup: file we want to get matchings from
# input: matches_dict empty dictionary or dictionary of previous matchings from other files

# output: matches_dict
# key: author name(string)
# value: dictionary {  instituion: "", email: "", address: ""}
def update_matching_dict(soup,matches_dict):
    extraction_results = extraction(soup)
    matchings = create_matchings(extraction_results,str(soup))
    authors = matchings[0]
    author_institution = matchings[1]
    insti_address = matchings[2]
    author_email = matchings[3]
    for i in authors:
        institutions = ""
        institution_list = []
        address = []
        # authors may have mutiple institutions, so we must concatenate all addresses that belong to them
        if author_institution.get(i,"") != "":
            institution_list = flat(author_institution.get(i,""))
            for insti in institution_list:
                institutions += insti
                if insti_address.get(insti) != None:
                    address.append(insti_address[insti])
        # reformats lists to a single string
        address = " ".join([i for i in flat(address)])
        email  = " ".join([i for i in  flat(author_email.get(i,""))])
        matches_dict.update({i:{"institution":institutions,"email":email,"address":address }})
    return matches_dict

