from speech.project4 import DATA_DIR, read_file
from speech.project4.lextree import Trie, TrieNode


def _find_first_layer(flat_trienode_list: list[TrieNode]):
    root = flat_trienode_list[0]
    first = []
    for _ in flat_trienode_list:
        if _.parent == root:
            first.append(_)
    return first


def match_single(word, ft: list[TrieNode]):
    costs = []
    first = _find_first_layer(ft)
    first_cost = []
    for node in first:
        if node.value == word[0]:
            first_cost.append((0, node))
        else:
            first_cost.append((1, node))
    costs.append(first_cost)

    for i in range(1, len(word)):
        cost = []
        for t in costs[-1]:
            if t[1].children is not None:
                for c in t[1].children.inner.values():
                    if c.value == word[i]:
                        cost.append((t[0], c))
                    else:
                        cost.append((t[0] + 1, c))
        costs.append(cost)

    last_cost = last = costs[-1]
    last_cost.sort(key=lambda x: x[0])
    last = last_cost[0][1]
    result = last.value
    while last := last.parent:
        if last.value is not None:
            result = last.value + result
    print(result)


def main():
    trie = Trie()
    dictionary = read_file(f"{DATA_DIR}dict_1.txt").split()
    for word in dictionary:
        trie.insert(word)
    match_single("abaddon", trie.flatten())


main() if __name__ == "__main__" else None
