"""Run as `python3 -m speech.project4.segment_and_spellcheck`."""

from . import DATA_DIR, read_lines_stripped, write_split_lines
from .correct_story import correct_story_lines_stripped
from .dictionary import dictionary_trie
from .lextree import Trie
from .segment import compare_to_correct


def segment_and_spellcheck(dict_trie: Trie, text: str, beam_width=5) -> list[str]:
    return dict_trie.match_words(text, beam_width)


def main():
    dict_trie = dictionary_trie()
    lines = read_lines_stripped(f"{DATA_DIR}unsegmented.txt")
    segmented_result = [segment_and_spellcheck(dict_trie, line) for line in lines]
    write_split_lines("segment_unsegmented.txt", segmented_result)

    correct_lines = correct_story_lines_stripped()
    compare_to_correct(correct_lines, segmented_result)


main() if __name__ == "__main__" else None
