---
presentation:
  width: 1920
  height: 1080
---

<!-- slide -->

# COMPSCI 304 group project 4: Text Segmentation and Spell Check with Lexical Tree

Steven Hé (Sīchàng), Luyao Wang

Instructor: Prof. Ming Li, Haoxu Wang

Duke Kunshan University

<!-- slide -->

### Contents

- Lexical tree
  - DTW With Single Templates
  - Pruning for DTW
  - DTW With Five Templates
- Hidden Markov Model (HMM)
  - Segmental K-means for training HMM
  - HMM with Gaussian mixture
- Demo

<!-- slide -->

### Dataset

- Hard dataset
  - Labeled with indexes 0 through 9
  - We intentionally recorded each instance differently
- Easy dataset
  - Labeled with indexes 10 through 19
  - The instances are very similar to each other

<!-- slide -->

### Lexical tree

- Each trie node represents a character
- Trie node data type
  - Parent node
  - Children, `None` if leaf
  - an associated value, `None` if beginning as dummy value

 - The children dictionary uses `(is_leaf, value)`
 - Allow querying either leaf or non-leaf nodes in $O(1)$
 - Enhance the speed of the insertion process

<!-- slide -->

### Lexical tree

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

</br>

<!-- slide -->

### Spell checking

- Perform procedures similar to Levenshtein distance with dynamic programming
- Flatten the lexical tree, transforming the tree structure into a linear sequence.

From

```
*─b─a─n─a─n─a
    ├─t
    └─t─t─l─e
```

To `[root, b, a1, n, t1, t2, a2, t3, n2, l, a3, e]`

- Breadth-first to ensure each node's parent node appears before the node itself

<!-- slide -->

### Matching

During the process of generating the target word, we consider three possible operations at each character position:

1. Stay (move from _left_ in the trellis): The tree remains at the current position with loss `left_loss`.
2. Advance (move *diag*onal in the trellis): The tree moves to the next layer or level with loss `diag_loss` if character does not match.
3. Skip (move from _down_ in the trellis): The tree skips that particular character with loss `down_loss`.

These loss parameters can be adjusted to obtain better result.

<!-- slide -->

### Matching

- New data type "loss node" to keep track of the trelis
  - A loss node contains the current loss value and the references to the corresponding trie node
- Maintain a dictionary from trie nodes to loss nodes during each round of traversal

<!-- slide -->

### Beam search

Only consider the loss nodes that have a loss value smaller than the minimum loss of the current iteration plus the specified beam width at each iteration of the target word.

![Inaccuracy vs beam width](./accuracy_vs_beam_alt2.png)

<!-- slide -->

### Backtracking

- Optimal loss obtained at the end of the target word
- Backtrack the loss node to identify the best matching string
- Iteratively finding the parent of the trie node associated with each loss node

<!-- slide -->

### 

<!-- slide -->

## Demo
