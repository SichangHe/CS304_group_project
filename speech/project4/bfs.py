from collections import deque
from typing import List
from speech.project4 import DATA_DIR, read_file
from speech.project4.lextree import Trie, TrieNode
from typing import Deque, List, Tuple


trie = Trie()
assert trie.insert("bat")[1]
assert trie.insert("battle")[1]
assert trie.insert("banana")[1]


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
            if child[0][0]:
                path.append(child[1].value)
                result.append(path)
            else:
                queue.append((child[1], path.copy()))

    return result


print(bfs(trie.root))
