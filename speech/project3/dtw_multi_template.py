"""With time-synchronous dynamic time warping, use a variable number of
recordings in `recordings/` among 10~19 with even indexes as
templates to recognize the 5 recordings among 10~19 with odd indexes.
Run as `python3 -m speech.project3.dtw_multi_template`."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from ..project2.main import NUMBERS
from . import TEMPLATE_INDEXES, TEST_INDEXES, boosted_mfcc_from_file
from .dtw import BEST_PRUNING_THRESHOLD
from .dtw_single_template_time_sync import recognize_number


def main():
    template_mfcc_s = []
    ns_templates = []
    average_accuracies = []

    n_template = 0
    for template_index in TEMPLATE_INDEXES:
        n_template += 1
        ns_templates.append(n_template)
        for number in NUMBERS:
            template_mfcc = boosted_mfcc_from_file(
                f"recordings/{number}{template_index}.wav"
            )
            template_mfcc_s.append((template_mfcc, number))

        accuracies = [
            recognize_number(number, template_mfcc_s, BEST_PRUNING_THRESHOLD)
            / len(TEST_INDEXES)
            for number in NUMBERS
        ]
        average_accuracy = sum(accuracies) / len(accuracies)
        average_accuracies.append(average_accuracy)
        print(
            f"""\n{n_template} templates:
Number|{"|".join(NUMBERS)}|Average
{"|".join("-"for _ in range(len(NUMBERS) + 2))}
Accuracy|{"|".join(str(a) for a in accuracies)}|{average_accuracy:.2f}"""
        )

    ax: Axes
    fig, ax = plt.subplots()
    ax.plot(ns_templates, average_accuracies)
    ax.grid()
    ax.set_xlabel("Number of Templates")
    ax.set_ylabel("Average Accuracy")
    plt.show(block=True)
    fig.savefig("dtw_n_template_vs_accuracy.png", bbox_inches="tight")


main() if __name__ == "__main__" else None
