"""Run as `python3 -m speech.project4.accuracy_vs_beam`."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from . import DATA_DIR, read_file
from .correct_story import correct_story_lines
from .dictionary import dictionary_trie
from .lextree import Trie
from .segment_and_spellcheck import (
    longest_common_subsequence_diff,
    segment_and_spellcheck,
)

plt.rcParams["font.size"] = 24


def experiment_inaccuracy(
    dict_trie: Trie, lines: list[str], correct_lines: list[list[str]], beam_width: int
) -> int:
    segmented_result = [
        segment_and_spellcheck(dict_trie, line, beam_width) for line in lines
    ]
    return sum(
        longest_common_subsequence_diff(correct, spell_checked)
        for correct, spell_checked in zip(correct_lines, segmented_result)
    )


def main() -> None:
    dict_trie = dictionary_trie()
    lines = read_file(f"{DATA_DIR}unsegmented.txt").splitlines()
    correct_lines = correct_story_lines()

    beam_widths = range(50)
    inaccuracies = [
        experiment_inaccuracy(dict_trie, lines, correct_lines, beam_width)
        for beam_width in beam_widths
    ]

    ax: Axes
    fig, ax = plt.subplots()
    ax.plot(beam_widths, inaccuracies)
    ax.grid()
    ax.set_xlabel("Beam Width")
    ax.set_ylabel("Inaccuracy")
    plt.show(block=True)
    fig.savefig("accuracy_vs_beam.png", bbox_inches="tight")


main() if __name__ == "__main__" else None
