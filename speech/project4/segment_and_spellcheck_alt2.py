"""Run as `python3 -m speech.project4.segment_and_spellcheck_alt2`."""

from speech.project4 import DATA_DIR, read_lines_stripped, write_split_lines
from speech.project4.correct_story import correct_story_lines_stripped
from speech.project4.dictionary import dictionary_trie
from speech.project4.lextree import Trie
from speech.project4.segment import compare_to_correct
from speech.project4.segment_and_spellcheck import segment_and_spellcheck


def alter_dict_trie_losses(dict_trie: Trie):
    dict_trie.left_loss = 0x10
    dict_trie.diag_loss = 0x10
    dict_trie.down_loss = 0x10
    dict_trie.transition_loss = 0x8


def main():
    dict_trie = dictionary_trie()
    alter_dict_trie_losses(dict_trie)

    lines = read_lines_stripped(f"{DATA_DIR}unsegmented.txt")
    segmented_result = [segment_and_spellcheck(dict_trie, line, 0x50) for line in lines]
    write_split_lines("segment_unsegmented_alt2.txt", segmented_result)

    correct_lines = correct_story_lines_stripped()
    compare_to_correct(correct_lines, segmented_result)


main() if __name__ == "__main__" else None
