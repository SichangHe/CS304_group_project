"""Run as `python3 -m speech.project4.lextree`."""

from dataclasses import dataclass
from logging import debug


@dataclass
class TrieNodeChildren:
    inner: dict[tuple[bool, str], "TrieNode"]
    """The key is (is_leaf, value)."""

    def __init__(self):
        self.inner = {}

    def get_non_leaf(self, value: str) -> "TrieNode | None":
        return self.inner.get((False, value))

    def get_leaf(self, value: str) -> "TrieNode | None":
        return self.inner.get((True, value))

    def insert(self, node: "TrieNode"):
        assert node.value is not None, (node, "Should not insert root node")
        key = (node.children is None, node.value)
        assert key not in self.inner, (self, node, "key already exists")
        self.inner[key] = node


@dataclass
class TrieNode:
    parent: "TrieNode | None" = None
    """The node is a root node if the `parent` is `None`."""
    children: TrieNodeChildren | None = None
    """The node is a leaf node if the `children` is `None`."""
    value: str | None = None
    """The node is a root node if the `value` is `None`."""


def _insert_new_chain_into_trie(node: TrieNode, value: str):
    debug(f"Inserting `{value}` into node with value {node.value}")
    current_node: TrieNode = node
    for char in value[:-1]:
        new_node = TrieNode(
            parent=current_node, children=TrieNodeChildren(), value=char
        )
        assert current_node.children is not None, (
            current_node,
            "`current_node` should be non-leaf",
        )
        current_node.children.insert(new_node)
        current_node = new_node

    last_node = TrieNode(parent=current_node, children=None, value=value[-1])
    assert current_node.children is not None, (
        current_node,
        "`current_node` should be non-leaf",
    )
    current_node.children.insert(last_node)
    return last_node


def _trie_strs(node: TrieNode) -> list[str]:
    """Traverse the subset of the trie recursively and produce one line for each
    branch."""
    value = node.value if node.value is not None else "*"
    children = node.children
    if children is None:
        return [value]
    sub_trie_strs = [_trie_strs(child) for child in children.inner.values()]
    if len(sub_trie_strs) == 0:
        return [value]
    sub_trie_strs.sort(key=lambda lines: (len(lines), lines[0]))

    result = [f"{value}─{sub_trie_strs[0][0]}"]
    for line in sub_trie_strs[0][1:]:
        result.append(f"│ {line}")

    for lines in sub_trie_strs[1:-1]:
        result.append(f"├─{lines[0]}")
        result.extend((f"│ {line}" for line in lines[1:]))

    if len(sub_trie_strs) > 1:
        result.append(f"└─{sub_trie_strs[-1][0]}")
        result.extend((f"  {line}" for line in sub_trie_strs[-1][1:]))

    return result


class Trie:
    def __init__(self):
        self.root = TrieNode(children=TrieNodeChildren())
        self.len = 0

    def insert(self, value: str) -> tuple[TrieNode, bool]:
        """Return the leaf node associated with `value` and whether it is new."""
        debug(f"Inserting `{value}`")
        assert len(value) > 0, (value, "Should not insert empty value")
        current_node: TrieNode = self.root
        current_value = value

        while len(current_value) > 1:
            assert current_node.children is not None, (
                current_node,
                "`current_node` should be non-leaf",
            )
            child = current_node.children.get_non_leaf(current_value[0])
            if child is not None:
                # Non-leaf node matching first character.
                current_node = child
                debug(
                    f"Traversed to node with value `{child.value}` for `{current_value}`."
                )
                current_value = current_value[1:]
            else:
                self.len += 1
                new_node = _insert_new_chain_into_trie(current_node, current_value)
                return (new_node, True)

        assert current_node.children is not None, (
            current_node,
            "`current_node` should be non-leaf",
        )
        assert len(current_value) == 1
        child = current_node.children.get_leaf(value)
        if child is None:
            self.len += 1
            new_node = _insert_new_chain_into_trie(current_node, current_value)
            return (new_node, True)
        else:
            return (child, False)

    def __len__(self):
        return self.len

    def __repr__(self):
        drawing = "\n".join(_trie_strs(self.root))
        return f"Trie(len={self.len}):\n{drawing}"


def main() -> None:
    trie = Trie()
    assert trie.insert("bat")[1]
    assert trie.insert("battle")[1]
    assert trie.insert("banana")[1]
    print(trie)

    assert trie.insert("and")[1]
    assert trie.insert("a")[1]
    assert trie.insert("an")[1]
    assert trie.insert("apple")[1]
    print(trie)


main() if __name__ == "__main__" else None
