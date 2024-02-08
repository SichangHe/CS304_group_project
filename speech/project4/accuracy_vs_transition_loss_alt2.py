"""Run as `python3 -m speech.project4.accuracy_vs_transition_loss_alt2`."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from speech.project4 import DATA_DIR, read_lines_stripped
from speech.project4.accuracy_vs_beam import experiment_inaccuracy
from speech.project4.correct_story import correct_story_lines_stripped
from speech.project4.dictionary import dictionary_trie
from speech.project4.segment_and_spellcheck_alt2 import alter_dict_trie_losses

plt.rcParams["font.size"] = 24


def main() -> None:
    dict_trie = dictionary_trie()
    alter_dict_trie_losses(dict_trie)

    lines = read_lines_stripped(f"{DATA_DIR}unsegmented.txt")
    correct_lines = correct_story_lines_stripped()

    transition_losses = (0x1, 0x2, 0x4, 0x6, 0x8, 0xA, 0xC, 0x10)
    inaccuracies = []
    for transition_loss in transition_losses:
        dict_trie.transition_loss = transition_loss
        inaccuracy = experiment_inaccuracy(dict_trie, lines, correct_lines, 0x20)
        inaccuracies.append(inaccuracy)

    ax: Axes
    fig, ax = plt.subplots()
    ax.plot(transition_losses, inaccuracies)
    ax.grid()
    ax.set_xlabel("Transition Loss")
    ax.set_ylabel("Inaccuracy")
    ax.ticklabel_format(style="plain")
    plt.show(block=True)
    fig.savefig("accuracy_vs_transition_loss_alt2.png", bbox_inches="tight")


main() if __name__ == "__main__" else None
