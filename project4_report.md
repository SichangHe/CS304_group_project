# Project 4 Report

## Lexical tree

We construct a trie structure for the lexical tree.

Each trie node represents a character. A node has a parent, a list of children, and an associated value. We use `None` in place of the children list to indicate that the node is a leaf node corresponding to the end of a word. We use `None` in place of the value for the dummy node prepended at the beginning of all words.

Leaf nodes and non-leaf nodes are distinguished within each node's children. We assign keys composed of whether the child node is a leaf node and the child node's value to the parent's children dictionary. This allows us to query either leaf or non-leaf nodes in $O(1)$.

### Debugging the trie

To check the correctness of the trie, we implemented a `__repr__` method to print the trie in a human-readable format. For example, one of the test cases is a trie containing the words `banana`, `bat`, `battle`, `a`, `an`, `and`, and `apple`. The trie is printed as follows:

```
Trie(len=7):
*─a
├─a─n
│ ├─n─d
│ └─p─p─l─e
└─b─a─n─a─n─a
    ├─t
    └─t─t─l─e
```

## Spell checking

In order to facilitate techniques similar to Levenshtein distance with dynamic programming, we employ a process of flattening the lexical tree. This involves transforming the tree structure into a linear sequence. For instance, the given tree:
```
*─b─a─n─a─n─a
    ├─t
    └─t─t─l─e
```
would be flattened as [root, b, a1, n, t1, t2, a2, t3, n2, l, a3, e]. Each node in the flattened structure is represented by a character, and connections between nodes are denoted by references. For example, 'b' points to 'a1', 'a1' points to 'n', 't', and 't', and so on.

During the process of generating the target word, we consider three possible operations at each character position:

1. Stay: The tree remains at the current position.
2. Advance: The tree moves to the next layer or level.
3. Skip: The tree skips that particular character.

At each round, we generate a list of `LossNode`s, which contain the current loss value as well as references to the previous `LossNode` and `TrieNode`. These nodes help us keep track of the progress made during the search.

To improve efficiency and reduce computational complexity, we employ beam search for pruning at each round. This means that we only consider the `LossNode`s that have a loss value smaller than the minimum loss of the current round plus the specified beam width.