class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False
        self.matchedIds = []

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, id):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
        node.matchedIds.append(id)

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def get_all_words(self, prefix=''):
        results = []
        node = self.root
        for char in prefix:
            if char not in node.children:
                return results
            node = node.children[char]
        self._dfs(node, prefix, results)
        return results

    def _dfs(self, node, prefix, results):
        if node.is_word:
            results.append(prefix)
        for char, child_node in node.children.items():
            self._dfs(child_node, prefix + char, results)
