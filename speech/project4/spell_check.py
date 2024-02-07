"""Use dictionary `dict_1.txt` to spell check against `typos.txt`, and calculate
accuracy against `storycorrect.txt`.
Run as `python3 -m speech.project4.spell_check`."""

from . import DATA_DIR, read_file, write_file
from .correct_story import correct_story
from .lextree import Trie


def correct_word(dict_trie: Trie, word: str) -> str:
    # TODO: Use the trie to spell-check the word.
    return word.lower()


def main() -> None:
    dictionary = read_file(f"{DATA_DIR}dict_1.txt").split()
    dict_trie = Trie()
    for word in dictionary:
        dict_trie.insert(word)

    typo_lines = [
        line.split() for line in read_file(f"{DATA_DIR}typos.txt").splitlines()
    ]
    spell_checked_lines = [
        [correct_word(dict_trie, word) for word in line] for line in typo_lines
    ]
    spell_checked = "\n".join(" ".join(line) for line in spell_checked_lines)
    write_file(f"typos_correction.txt", spell_checked)

    spell_checked_words = (word for line in spell_checked_lines for word in line)
    correct_words = correct_story()
    n_correct = 0
    n_total = 0
    for correct, spell_checked in zip(correct_words, spell_checked_words):
        n_total += 1
        if correct == spell_checked:
            n_correct += 1
    print(f"Accuracy: {n_correct/n_total:.2%}")


main() if __name__ == "__main__" else None
