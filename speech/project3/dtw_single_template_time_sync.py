"""With time-synchronous dynamic time warping, use `10`s in `recordings/` as
templates to recognize the 5 recordings among 10~19 with odd indexes.
Run as `python3 -m speech.project3.dtw_single_template_time_sync`."""

import argparse

from ..project2.main import NUMBERS
from . import TEST_INDEXES, boosted_mfcc_from_file
from .dtw import time_sync_dtw_search


def recognize_number(number: str, template_mfcc_s, pruning_threshold=10.0):
    n_correct = 0
    for i in TEST_INDEXES:
        test_mfcc = boosted_mfcc_from_file(f"recordings/{number}{i}.wav")
        min_cost, prediction = time_sync_dtw_search(
            template_mfcc_s, test_mfcc, pruning_threshold
        )
        if prediction is None:
            print(
                f"Prediction for `{number}`[{i}] failed because the test sample was too short."
            )
            continue

        print(
            f"Prediction for `{number}`[{i}] is `{prediction}` with cost {min_cost:.2f}."
        )

        if prediction == number:
            n_correct += 1
    return n_correct


def main():
    parser = argparse.ArgumentParser(
        description="Time-synchronous DTW test with single templates"
    )
    parser.add_argument(
        "-t",
        "--pruning-threshold",
        help="Path cost pruning threshold.",
    )
    args = parser.parse_args()
    pruning_threshold = float(args.pruning_threshold or "10")

    template_mfcc_s = [
        (boosted_mfcc_from_file(f"recordings/{number}10.wav"), number)
        for number in NUMBERS
    ]

    accuracies = [
        recognize_number(number, template_mfcc_s, pruning_threshold) / len(TEST_INDEXES)
        for number in NUMBERS
    ]
    print(
        f"""Number|{"|".join(NUMBERS)}|Average
{"|".join("-"for _ in range(len(NUMBERS) + 2))}
Accuracy|{"|".join(str(a) for a in accuracies)}|{sum(accuracies) / len(accuracies):.2f}"""
    )


main() if __name__ == "__main__" else None
