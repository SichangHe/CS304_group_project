"""With dynamic time warping, use `0`s in `recordings/` as templates to
recognize the 5 recordings with odd indexes.
Run as `python3 -m speech.project3.dtw_single_template`."""

import argparse

from ..project2.main import NUMBERS
from . import INF_FLOAT32, boosted_mfcc_from_file, TEST_INDEXES
from .dtw import single_dtw_search


def recognize_number(number: str, template_mfcc_s, cost_interpretation="min"):
    n_correct = 0
    for i in TEST_INDEXES:
        test_mfcc = boosted_mfcc_from_file(f"recordings/{number}{i}.wav")
        min_cost = INF_FLOAT32
        prediction = None
        for template_mfcc, associated_number in template_mfcc_s:
            current_costs = single_dtw_search(template_mfcc, test_mfcc)
            if len(current_costs) == 0:
                continue
            match cost_interpretation:
                case "first":
                    current_cost = current_costs[-1]
                case "last":
                    current_cost = current_costs[-1]
                case _:
                    current_cost = min(current_costs)

            if current_cost < min_cost:
                min_cost = current_cost
                prediction = associated_number
                print(
                    f"\tUpdated prediction for `{number}` to be `{associated_number}` with new cost {current_cost:.2f}."
                )

        assert prediction is not None
        print(
            f"Prediction for `{number}`[{i}] is `{prediction}` with cost {min_cost:.2f}."
        )

        if prediction == number:
            n_correct += 1
    return n_correct


def main():
    parser = argparse.ArgumentParser(description="DTW test with single templates")
    parser.add_argument(
        "-i",
        "--cost-interpretation",
        help="How the path cost is interpreted. Could be `min`, `first`, or `last`. Defaults to `min`.",
    )
    args = parser.parse_args()
    cost_interpretation = args.cost_interpretation or "min"

    template_mfcc_s = [
        (boosted_mfcc_from_file(f"recordings/{number}0.wav"), number)
        for number in NUMBERS
    ]

    accuracies = [
        recognize_number(number, template_mfcc_s, cost_interpretation) / 5
        for number in NUMBERS
    ]
    print(
        f"""Number|{"|".join(NUMBERS)}
{"|".join("-"for _ in range(len(NUMBERS) + 1))}
Accuracy|{"|".join(str(a) for a in accuracies)}"""
    )


main() if __name__ == "__main__" else None
