from collections import deque
from typing import Deque, List, Tuple

import numpy as np

from speech.project4 import DATA_DIR, read_file
from speech.project4.lextree import Trie, TrieNode


def levenshtein_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = np.zeros((m + 1, n + 1))

    for i in range(m + 1):
        dp[i][0] = i

    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1

    return dp[m][n]


def bfs(root, s, pruning=3):
    if not root:
        return []

    queue: Deque[Tuple[TrieNode, List[str]]] = deque()
    queue.append((root, []))
    result = []

    current_length = 0
    pending = []
    while queue:
        node, path = queue.popleft()
        path.append(node.value)
        for child in node.children.inner.items():
            path_copy = path.copy()
            if current_length != len(path_copy[1:]):
                current_length = len(path_copy[1:])
                pending = []
            current_word = "".join(path_copy[1:])
            dist = levenshtein_distance(s[: len(current_word)], current_word)
            print(current_word, dist)
            if child[0][0]:
                path_copy.append(child[1].value)
                result.append(path_copy)
            else:
                pending.append(((child[1], path_copy), dist))

        if len(queue) == 0 and len(pending) > 0:
            pending.sort(key=lambda x: x[1])
            threshold = pending[:pruning][-1][1]
            queue.extend(
                map(lambda x: x[0], filter(lambda x: x[1] <= threshold, pending))
            )

    result = list(map(lambda x: "".join(x[1:]), result))
    min_dist = 99999
    best_word = ""
    for w in result:
        dist = levenshtein_distance(s, w)
        if dist < min_dist:
            best_word = w
            min_dist = dist

    return best_word


def main():
    trie = Trie()
    dictionary = read_file(f"{DATA_DIR}dict_1.txt").split()
    for word in dictionary:
        trie.insert(word)
    print(trie)
    print(bfs(trie.root, "yoursselves", pruning=3))


main() if __name__ == "__main__" else None
