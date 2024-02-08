"""Run as `python3 -m speech.project4.demo`."""

from speech.project4.dictionary import dictionary_trie
from speech.project4.lextree import Trie
from speech.project4.segment_and_spellcheck import segment_and_spellcheck


def alter_dict_trie_losses(dict_trie: Trie):
    dict_trie.left_loss = 0x10
    dict_trie.diag_loss = 0x10
    dict_trie.down_loss = 0x10
    dict_trie.transition_loss = 0x8


def main():
    dict_trie = dictionary_trie()
    alter_dict_trie_losses(dict_trie)

    input_line = input("Please type a line of text and press enter:\n").lower()
    segmented_result = [
        segment_and_spellcheck(dict_trie, split, 0x20) for split in input_line.split()
    ]

    result_str = " ".join(word for split in segmented_result for word in split)
    print(f"\nSegmented and spellchecked:\n{result_str}")


main() if __name__ == "__main__" else None
