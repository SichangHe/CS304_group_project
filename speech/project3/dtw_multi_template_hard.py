"""With time-synchronous dynamic time warping, use a variable number of
recordings in `recordings/` among 10~19 with even indexes as
templates to recognize the 5 recordings among 10~19 with odd indexes.
Run as `python3 -m speech.project3.dtw_multi_template_hard`."""

import argparse

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from speech.project2.main import NUMBERS
from speech.project3 import HARD_TEMPLATE_INDEXES, HARD_TEST_INDEXES, boosted_mfcc_from_file
from speech.project3.dtw_single_template_time_sync import recognize_number

BEST_PRUNING_THRESHOLD = 13.0


def main():
    parser = argparse.ArgumentParser(
        description="Time-synchronous DTW test with multiple templates in hard mode"
    )
    parser.add_argument(
        "-t",
        "--pruning-threshold",
        help="Path cost pruning threshold.",
    )
    parser.add_argument(
        "-o",
        "--output-path",
        help="Path for output figure.",
    )
    args = parser.parse_args()
    pruning_threshold = float(args.pruning_threshold or BEST_PRUNING_THRESHOLD)
    output_path = args.output_path or "dtw_n_template_vs_accuracy_hard.png"

    template_mfcc_s = []
    ns_templates = []
    average_accuracies = []

    n_template = 0
    for template_index in HARD_TEMPLATE_INDEXES:
        n_template += 1
        ns_templates.append(n_template)
        for number in NUMBERS:
            template_mfcc = boosted_mfcc_from_file(
                f"recordings/{number}{template_index}.wav"
            )
            template_mfcc_s.append((template_mfcc, number))

        accuracies = [
            recognize_number(number, template_mfcc_s, pruning_threshold)
            / len(HARD_TEST_INDEXES)
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
    ax.ticklabel_format(style="plain")
    plt.show(block=True)
    fig.savefig(output_path, bbox_inches="tight")


main() if __name__ == "__main__" else None
