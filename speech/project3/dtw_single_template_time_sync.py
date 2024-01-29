"""With time-synchronous dynamic time warping, use `0`s in `recordings/` as
templates to recognize the 5 recordings with odd indexes.
Run as `python3 -m speech.project3.dtw_single_template_time_sync`."""

from ..project2.main import NUMBERS
from . import TEST_INDEXES, boosted_mfcc_from_file
from .dtw import time_sync_dtw_search


def recognize_number(number: str, template_mfcc_s):
    n_correct = 0
    for i in TEST_INDEXES:
        test_mfcc = boosted_mfcc_from_file(f"recordings/{number}{i}.wav")
        least_cost, prediction = time_sync_dtw_search(template_mfcc_s, test_mfcc)
        assert prediction is not None

        print(
            f"Prediction for `{number}`[{i}] is `{prediction}` with cost {least_cost:.2f}."
        )

        if prediction == number:
            n_correct += 1
    return n_correct


def main():
    template_mfcc_s = [
        (boosted_mfcc_from_file(f"recordings/{number}0.wav"), number)
        for number in NUMBERS
    ]

    accuracies = [
        recognize_number(number, template_mfcc_s) / len(TEST_INDEXES)
        for number in NUMBERS
    ]
    print(
        f"""Number|{"|".join(NUMBERS)}
{"|".join("-"for _ in range(len(NUMBERS) + 1))}
Accuracy|{"|".join(str(a) for a in accuracies)}"""
    )


main() if __name__ == "__main__" else None
