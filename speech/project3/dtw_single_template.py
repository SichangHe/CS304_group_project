"""With dynamic time warping, use `0`s in `recordings/` as templates to
recognize the 5 recordings with odd indexes.
Run as `python3 -m speech.project3.dtw_single_template`."""

from ..project2.main import NUMBERS
from . import INF_FLOAT32, boosted_mfcc_from_file, single_dtw_search


def recognize_number(number: str, template_mfcc_s):
    test_mfcc_s = [
        boosted_mfcc_from_file(f"recordings/{number}{i}.wav")
        for i in range(1, 5, 2)  # TODO: Change to 1 through 10
    ]

    for test_index, test_mfcc in enumerate(test_mfcc_s):
        least_cost = INF_FLOAT32
        prediction = None
        for template_mfcc, associated_number in template_mfcc_s:
            current_cost = single_dtw_search(template_mfcc, test_mfcc)
            if current_cost is None:
                print(f"Search for `{number}` did not finish on `{associated_number}`.")
            elif current_cost < least_cost:
                least_cost = current_cost
                prediction = associated_number
                print(
                    f"Updated prediction for `{number}` to be `{associated_number}` with new cost {current_cost}."
                )
        assert prediction is not None
        print(
            f"Prediction for `{number}`[{test_index}] is `{prediction}` with cost {least_cost}."
        )


def main():
    template_mfcc_s = [
        (boosted_mfcc_from_file(f"recordings/{number}0.wav"), number)
        for number in NUMBERS
    ]
    recognize_number(NUMBERS[0], template_mfcc_s)


main() if __name__ == "__main__" else None
