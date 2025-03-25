import utils.trie as trie_module

def build_blacklist(file_path: str):
    words_trie = trie_module.Trie()
    with open(file_path, 'r') as file:
        for line in file:
            word = line.strip().upper()
            words_trie.insert(word, 0)
    return words_trie
