"""Plot recognition accuracy vs pruning threshold, tested against the 5
recordings with odd indexes using `0`s in `recordings/` as templates.
Run as `python3 -m speech.project3.dtw_accuracy_vs_threshold`."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from ..project2.main import NUMBERS
from . import TEST_INDEXES, boosted_mfcc_from_file
from .dtw_single_template_time_sync import recognize_number

PRUNING_THRESHOLDS = range(40)


def all_numbers_recognition_accuracy(template_mfcc_s, pruning_threshold):
    accuracies = [
        recognize_number(number, template_mfcc_s, pruning_threshold) / len(TEST_INDEXES)
        for number in NUMBERS
    ]
    average_accuracy = sum(accuracies) / len(accuracies)
    print(
        f"""\nPruning threshold: {pruning_threshold}
Number|{"|".join(NUMBERS)}|Average
{"|".join("-"for _ in range(len(NUMBERS) + 2))}
Accuracy|{"|".join(str(a) for a in accuracies)}|{average_accuracy:.2f}"""
    )
    return average_accuracy


def main():
    template_mfcc_s = [
        (boosted_mfcc_from_file(f"recordings/{number}0.wav"), number)
        for number in NUMBERS
    ]

    average_accuracies = [
        all_numbers_recognition_accuracy(template_mfcc_s, pruning_threshold)
        for pruning_threshold in PRUNING_THRESHOLDS
    ]

    ax: Axes
    fig, ax = plt.subplots()
    ax.plot(PRUNING_THRESHOLDS, average_accuracies)
    ax.grid()
    ax.set_xlabel("Pruning Threshold")
    ax.set_ylabel("Accuracy")
    plt.show(block=True)
    fig.savefig("dtw_accuracy_vs_threshold.pdf", bbox_inches="tight")


main() if __name__ == "__main__" else None
