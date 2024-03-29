"""Run as `python3 -m speech.project4.segment`."""

import numpy as np

from speech.project4 import DATA_DIR, read_lines_stripped, write_split_lines
from speech.project4.correct_story import correct_story_lines_stripped
from speech.project4.dictionary import dictionary_trie
from speech.project4.lextree import Trie


def segment_text(text, dictionary):
    n = len(text)
    dp = np.full((n, n), 0)
    prev = np.full((n, n), -1)

    for i in range(n):
        word = text[: i + 1]
        if word not in dictionary:
            min_distance = float("inf")
            for w in dictionary:
                distance = levenshtein_distance(w, word)
                if distance < min_distance:
                    min_distance = distance
            dp[0][i] = min_distance
            prev[0][i] = 0

    for i in range(1, n):
        for j in range(i, n):
            word = text[i : j + 1]
            if word in dictionary:
                score = 0
                dp[i][j] = np.min(dp[:i, i - 1]) + score
                prev[i][j] = np.argmin(dp[:i, i - 1])
            else:
                min_distance = float("inf")
                closest_word = None
                for w in dictionary:
                    distance = levenshtein_distance(w, word)
                    if distance < min_distance:
                        min_distance = distance
                        closest_word = w
                dp[i][j] = np.min(dp[:i, i - 1]) + min_distance
                prev[i][j] = np.argmin(dp[:i, i - 1])

    # print(np.array(dp))
    # print(np.array(prev))

    last = np.argmin(dp[:, -1])
    result = [len(prev), last]

    for t in range(len(prev) - 1, 0, -1):
        if prev[result[-1], t] == 0:
            break
        result.append(prev[result[-1], t])

    result.reverse()
    result = [0] + result
    return result


def levenshtein_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = np.zeros((m + 1, n + 1))

    for i in range(m + 1):
        dp[i][0] = i

    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1

    return dp[m][n]


def longest_common_subsequence_diff(word_list0: list[str], word_list1: list[str]):
    m, n = len(word_list0), len(word_list1)
    loss_matrix = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            node_loss = 0 if word_list0[i - 1] == word_list1[j - 1] else 1
            loss_matrix[i][j] = min(
                loss_matrix[i - 1][j] + 1,
                loss_matrix[i][j - 1] + 1,
                loss_matrix[i - 1][j - 1] + node_loss,
            )

    return loss_matrix[-1][-1]


def segment(dict_trie: Trie, text: str, beam_width=5) -> list[str]:
    return dict_trie.match_words(text, beam_width)


def compare_to_correct(
    correct_lines: list[list[str]], segmented_result: list[list[str]]
):
    inaccuracy = 0
    for correct, spell_checked in zip(correct_lines, segmented_result):
        if correct != spell_checked:
            print(f"{' '.join(correct)} !=\n{' '.join(spell_checked)}")
            inaccuracy += longest_common_subsequence_diff(correct, spell_checked)

    print(f"Inaccuracy: {inaccuracy}.")


def main():
    dict_trie = dictionary_trie()
    lines = read_lines_stripped(f"{DATA_DIR}unsegmented0.txt")
    segmented_result = [segment(dict_trie, line) for line in lines]
    write_split_lines("segment_unsegmented0.txt", segmented_result)

    correct_lines = correct_story_lines_stripped()
    compare_to_correct(correct_lines, segmented_result)


main() if __name__ == "__main__" else None
