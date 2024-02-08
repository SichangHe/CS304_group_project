"""Run as `python3 -m speech.project4.accuracy_vs_beam_alt2`."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from . import DATA_DIR, read_lines_stripped
from .accuracy_vs_beam import experiment_inaccuracy
from .correct_story import correct_story_lines_stripped
from .dictionary import dictionary_trie
from .segment_and_spellcheck_alt2 import alter_dict_trie_losses

plt.rcParams["font.size"] = 24


def main() -> None:
    dict_trie = dictionary_trie()
    alter_dict_trie_losses(dict_trie)

    lines = read_lines_stripped(f"{DATA_DIR}unsegmented.txt")
    correct_lines = correct_story_lines_stripped()

    beam_widths = tuple(width * 0x10 for width in (1, 2, 5, 10))
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
    ax.ticklabel_format(style="plain")
    plt.show(block=True)
    fig.savefig("accuracy_vs_beam_alt2.png", bbox_inches="tight")


main() if __name__ == "__main__" else None
