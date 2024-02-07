from collections import deque
from typing import List

from speech.project4 import DATA_DIR, read_file
from speech.project4.lextree import Trie, TrieNode
from typing import Deque, List, Tuple


def bfs(root):
    if not root:
        return []

    queue: Deque[Tuple[TrieNode, List[str]]] = deque()
    queue.append((root, []))
    result = []

    while queue:
        node, path = queue.popleft()
        path.append(node.value)
        for child in node.children.inner.items():
            path_copy = path.copy()
            current_word = "".join(path_copy[1:])
            print(current_word)
            if child[0][0]:
                path_copy.append(child[1].value)
                result.append(path_copy)
            else:
                queue.append((child[1], path_copy))

    return result


def main():
    trie = Trie()
    assert trie.insert("bat")[1]
    assert trie.insert("battle")[1]
    assert trie.insert("banana")[1]
    print(trie)
    print(bfs(trie.root))


main() if __name__ == "__main__" else None
