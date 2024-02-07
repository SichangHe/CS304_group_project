"""Run as `python3 -m speech.project4.lextree`."""

from collections import deque
from dataclasses import dataclass
from logging import debug
from typing import Iterable


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
        key = (node.is_leaf(), node.value)
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

    def is_leaf(self) -> bool:
        return self.children is None

    def backtrack(self) -> str:
        reversed_chars = []
        current: "TrieNode | None" = self
        while current is not None:
            if current.value is not None:
                reversed_chars.append(current.value)
            current = current.parent
        return "".join(reversed(reversed_chars))

    def __repr__(self) -> str:
        if self.children is None:
            return f"Leaf TrieNode({self.value})"
        else:
            return f"TrieNode({self.value}, {len(self.children.inner)} children)"


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

    if len(sub_trie_strs) == 1:
        result.extend(f"  {line}" for line in sub_trie_strs[0][1:])
        return result

    result.extend(f"│ {line}" for line in sub_trie_strs[0][1:])

    for lines in sub_trie_strs[1:-1]:
        result.append(f"├─{lines[0]}")
        result.extend(f"│ {line}" for line in lines[1:])

    if len(sub_trie_strs) > 1:
        result.append(f"└─{sub_trie_strs[-1][0]}")
        result.extend((f"  {line}" for line in sub_trie_strs[-1][1:]))

    return result


@dataclass
class LossNode:
    to_be_matched: str
    trie_node: TrieNode
    prev_end_loss_node: "LossNode | None" = None
    loss: int = 0

    def copying_update(
        self,
        to_be_matched: str | None = None,
        trie_node: TrieNode | None = None,
        prev_end_loss_node: "LossNode | None" = None,
        loss: int | None = None,
    ):
        if to_be_matched is None:
            to_be_matched = self.to_be_matched
        if trie_node is None:
            trie_node = self.trie_node
        if prev_end_loss_node is None:
            prev_end_loss_node = self.prev_end_loss_node
        if loss is None:
            loss = self.loss

        return LossNode(to_be_matched, trie_node, prev_end_loss_node, loss)

    def backtrack(self) -> list[str]:
        reversed_words = []
        current: "LossNode | None" = self
        while current is not None:
            reversed_words.append(current.trie_node.backtrack())
            current = current.prev_end_loss_node
        return list(reversed(reversed_words))


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

    def match_word(self, word: str, beam_width: int):
        current_losses: list[LossNode] = [LossNode(word, self.root)]
        finished_losses: list[LossNode] = []

        while len(current_losses) > 0:
            debug(f"{len(current_losses)} current losses.")
            next_losses: list[LossNode] = []
            round_min_loss = 0x7FFFFFFF

            for loss_node in current_losses:
                loss = loss_node.loss
                if loss > round_min_loss + beam_width:
                    continue

                to_be_matched = loss_node.to_be_matched
                trie_node = loss_node.trie_node

                can_right = True
                if len(to_be_matched) == 0:
                    if trie_node.is_leaf():
                        finished_losses.append(loss_node)
                        round_min_loss = min(round_min_loss, loss)
                        continue
                    can_right = False

                if can_right:
                    move_right = loss_node.copying_update(
                        to_be_matched=to_be_matched[1:],
                        loss=loss + 1,
                    )
                    next_losses.append(move_right)
                    round_min_loss = min(round_min_loss, loss + 1)

                prev_end_loss_node = loss_node.prev_end_loss_node
                next_nodes: Iterable[TrieNode]
                if trie_node.children is None:
                    # Leaf node
                    next_nodes = (self.root,)
                    prev_end_loss_node = loss_node
                else:
                    next_nodes = trie_node.children.inner.values()

                observation_increment = 1
                if trie_node.value is None:
                    # Root node.
                    observation_increment = 0

                for next_node in next_nodes:
                    move_up = loss_node.copying_update(
                        trie_node=next_node,
                        prev_end_loss_node=prev_end_loss_node,
                        loss=loss + 1,
                    )
                    next_losses.append(move_up)
                    round_min_loss = min(round_min_loss, loss + 1)

                    if can_right:
                        node_loss = 1
                        if (
                            next_node.value is None  # Root node.
                            or next_node.value == to_be_matched[0]
                        ):
                            node_loss = 0
                            round_min_loss = min(round_min_loss, loss)
                        move_diag = loss_node.copying_update(
                            to_be_matched=to_be_matched[observation_increment:],
                            prev_end_loss_node=prev_end_loss_node,
                            loss=loss + node_loss,
                        )
                        next_losses.append(move_diag)

                round_threshold = round_min_loss + beam_width
                current_losses = [
                    next_loss
                    for next_loss in next_losses
                    if next_loss.loss <= round_threshold
                ]

        final_min_loss = 0x7FFFFFFF
        best_loss_node = finished_losses[0]
        for loss_node in finished_losses[1:]:
            if loss_node.loss < final_min_loss:
                final_min_loss = loss_node.loss
                best_loss_node = loss_node

        return best_loss_node.backtrack()

    def flatten(self) -> list[TrieNode]:
        result = []
        result.append(self.root)

        nodes: deque[TrieNode] = deque()
        nodes.append(self.root)

        while len(nodes) > 0:
            node = nodes.popleft()
            if node.children is not None:
                result.extend(node.children.inner.values())
                nodes.extend(node.children.inner.values())

        return result

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
    print(trie.flatten())

    assert trie.insert("and")[1]
    assert trie.insert("a")[1]
    assert trie.insert("an")[1]
    assert trie.insert("apple")[1]
    print(trie)
    print(trie.flatten())


main() if __name__ == "__main__" else None
