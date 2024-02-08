"""Use dictionary `dict_1.txt` to spell check against `typos.txt`, and calculate
accuracy against `storycorrect.txt`.
Run as `python3 -m speech.project4.spell_check`."""

from . import DATA_DIR, read_lines_stripped, write_split_lines
from .correct_story import correct_story_lines
from .dictionary import dictionary_trie
from .lextree import Trie


def correct_word(dict_trie: Trie, word: str, beam_width=3) -> str:
    return dict_trie.match_word_single(word, beam_width)


def main() -> None:
    dict_trie = dictionary_trie()

    typo_lines = [line.split() for line in read_lines_stripped(f"{DATA_DIR}typos.txt")]
    spell_checked_lines = [
        [correct_word(dict_trie, word) for word in line] for line in typo_lines
    ]
    write_split_lines(f"typos_correction.txt", spell_checked_lines)

    correct_lines = correct_story_lines()
    n_correct = 0
    n_total = 0
    for correct_line, spell_checked_line in zip(correct_lines, spell_checked_lines):
        for correct, spell_checked in zip(correct_line, spell_checked_line):
            n_total += 1
            if correct == spell_checked:
                n_correct += 1
    print(f"Accuracy: {n_correct/n_total:.2%}")


main() if __name__ == "__main__" else None
