"""Use dictionary `dict_1.txt` to spellcheck against `typos.txt`, and calculate
accuracy against `storycorrect.txt`.
Run as `python3 -m speech.project4.spellcheck`."""

from speech.project4 import DATA_DIR, read_lines_stripped, write_split_lines
from speech.project4.correct_story import correct_story_lines
from speech.project4.dictionary import dictionary_trie
from speech.project4.lextree import Trie


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
        assert len(correct_line) == len(spell_checked_line), (
            correct_line,
            spell_checked_line,
        )
        for correct, spell_checked in zip(correct_line, spell_checked_line):
            n_total += 1
            if correct == spell_checked:
                n_correct += 1
    print(f"Accuracy: {n_correct/n_total:.2%}")


main() if __name__ == "__main__" else None
