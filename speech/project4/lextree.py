"""Run as `python3 -m speech.project4.lextree`."""

from collections import deque
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

    def __hash__(self) -> int:
        return id(self)

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
    trie_node: TrieNode
    prev_end_loss_node: "LossNode | None" = None
    loss: int = 0

    def copying_update(
        self,
        trie_node: TrieNode | None = None,
        prev_end_loss_node: "LossNode | None" = None,
        loss: int | None = None,
    ):
        if trie_node is None:
            trie_node = self.trie_node
        if prev_end_loss_node is None:
            prev_end_loss_node = self.prev_end_loss_node
        if loss is None:
            loss = self.loss

        return LossNode(trie_node, prev_end_loss_node, loss)

    def backtrack(self) -> list[str]:
        reversed_words = []
        current: "LossNode | None" = self
        while current is not None:
            reversed_words.append(current.trie_node.backtrack())
            current = current.prev_end_loss_node
        return list(reversed(reversed_words))


class Trie:
    def __init__(self, left_loss=1, diag_loss=1, down_loss=1, transition_loss=0):
        self.root = TrieNode(children=TrieNodeChildren())
        self.len = 0
        self.left_loss = left_loss
        self.diag_loss = diag_loss
        self.down_loss = down_loss
        self.transition_loss = transition_loss

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

    def _match_word_round(
        self,
        char: str,
        trie_node: TrieNode,
        round_min_loss: int,
        prev_losses: dict[TrieNode, LossNode],
        current_losses: dict[TrieNode, LossNode],
        beam_width: int,
        single_word: bool,
    ):
        min_loss = 0x7FFFFFFF
        min_loss_node = None

        if left := prev_losses.get(trie_node):
            if (left_loss := left.loss + self.left_loss) < min_loss:
                min_loss = left_loss
                min_loss_node = left

        if parent := trie_node.parent:
            if diag := prev_losses.get(parent):
                node_loss = self.diag_loss
                if trie_node.value is None or trie_node.value == char:
                    node_loss = 0

                if (diag_loss := diag.loss + node_loss) < min_loss:
                    min_loss = diag_loss
                    min_loss_node = diag

            if down := current_losses.get(parent):
                if (down_loss := down.loss + self.down_loss) < min_loss:
                    min_loss = down_loss
                    min_loss_node = down

        if min_loss_node is not None:
            if min_loss <= round_min_loss + beam_width:
                round_min_loss = min(round_min_loss, min_loss)
                new_loss_node = min_loss_node.copying_update(
                    trie_node=trie_node, loss=min_loss
                )

                if trie_node.is_leaf() and not single_word:
                    loss = min_loss + self.transition_loss
                    if current_root_loss_node := current_losses.get(self.root):
                        if current_root_loss_node.loss < loss:
                            return round_min_loss

                    current_losses[self.root] = new_loss_node.copying_update(
                        trie_node=self.root,
                        prev_end_loss_node=new_loss_node,
                        loss=loss,
                    )
                else:
                    current_losses[trie_node] = new_loss_node

        return round_min_loss

    def _match_word(self, word: str, beam_width: int, single_word=False):
        nodes = self.flatten()
        prev_losses: dict[TrieNode, LossNode] = {self.root: LossNode(self.root)}

        for index, char in enumerate(word):
            current_losses: dict[TrieNode, LossNode] = {}
            round_min_loss = 0x7FFFFFFF

            for node in nodes:
                round_min_loss = self._match_word_round(
                    char,
                    node,
                    round_min_loss,
                    prev_losses,
                    current_losses,
                    beam_width,
                    single_word or index == len(word) - 1,
                )

            debug(
                f"char: {char}, {len(current_losses)} current losses, round min loss {round_min_loss}, {len(prev_losses)} previous losses."
            )

            filtered_current_losses = {}
            for node, loss_node in current_losses.items():
                round_threshold = round_min_loss + beam_width
                if loss_node.loss <= round_threshold:
                    filtered_current_losses[node] = loss_node

            prev_losses = filtered_current_losses

        return prev_losses

    def match_word_single(self, word: str, beam_width: int):
        min_last_loss = 0x7FFFFFFF
        min_last_loss_node = None
        last_losses = self._match_word(word, beam_width, True)

        for node, last_loss_node in last_losses.items():
            if node.is_leaf():
                if last_loss_node.loss < min_last_loss:
                    min_last_loss = last_loss_node.loss
                    min_last_loss_node = last_loss_node

        assert min_last_loss_node is not None, (word, last_losses)
        return min_last_loss_node.backtrack()[0]

    def match_words(self, words: str, beam_width: int):
        min_last_loss = 0x7FFFFFFF
        min_last_loss_node = None
        last_losses = self._match_word(words, beam_width, False)

        for node, last_loss_node in last_losses.items():
            if node.is_leaf():
                if last_loss_node.loss < min_last_loss:
                    min_last_loss = last_loss_node.loss
                    min_last_loss_node = last_loss_node

        assert min_last_loss_node is not None, (words, last_losses)
        return min_last_loss_node.backtrack()

    def flatten(self) -> list[TrieNode]:
        """Guaranteed to return parent nodes first."""
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

    def flatten_w_parent_index(self) -> list[tuple[int | None, TrieNode]]:
        result: list[tuple[int | None, TrieNode]] = []
        result.append((None, self.root))

        nodes: deque[tuple[int, TrieNode]] = deque()
        """(index, node)"""
        nodes.append((0, self.root))

        while len(nodes) > 0:
            parent_index, node = nodes.popleft()
            if node.children is not None:
                for child in node.children.inner.values():
                    index = len(result)
                    result.append((parent_index, child))
                    nodes.append((index, child))

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
    print(trie.flatten_w_parent_index())

    assert trie.insert("and")[1]
    assert trie.insert("a")[1]
    assert trie.insert("an")[1]
    assert trie.insert("apple")[1]
    print(trie)
    print(trie.flatten_w_parent_index())


main() if __name__ == "__main__" else None
