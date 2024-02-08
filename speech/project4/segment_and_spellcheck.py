"""Run as `python3 -m speech.project4.segment_and_spellcheck`."""

from . import DATA_DIR, read_file, write_split_lines
from .correct_story import correct_story_lines
from .dictionary import dictionary_trie
from .lextree import Trie


def segment_and_spellcheck(dict_trie: Trie, text: str, beam_width=5) -> list[str]:
    return dict_trie.match_words(text, beam_width)


def longest_common_subsequence_diff(word_list0, word_list1):
    m, n = len(word_list0), len(word_list1)
    loss_matrix = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            node_loss = 0 if word_list0[i - 1] == word_list1[j - 1] else 1
            loss_matrix[i][j] = max(
                loss_matrix[i - 1][j] + 1,
                loss_matrix[i][j - 1] + 1,
                loss_matrix[i - 1][j - 1] + node_loss,
            )

    return loss_matrix[-1][-1]


def main():
    dict_trie = dictionary_trie()
    lines = read_file(f"{DATA_DIR}unsegmented.txt").splitlines()
    segmented_result = [segment_and_spellcheck(dict_trie, line) for line in lines]
    write_split_lines("segment_unsegmented.txt", segmented_result)

    correct_lines = correct_story_lines()
    inaccuracy = sum(
        longest_common_subsequence_diff(correct, spell_checked)
        for correct, spell_checked in zip(correct_lines, segmented_result)
    )
    print(f"Inaccuracy: {inaccuracy}.")


main() if __name__ == "__main__" else None
