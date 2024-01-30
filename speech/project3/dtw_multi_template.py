"""With time-synchronous dynamic time warping, use a variable number of
recordings in `recordings/` among 10~19 with even indexes as
templates to recognize the 5 recordings among 10~19 with odd indexes.
Run as `python3 -m speech.project3.dtw_multi_template`."""

from ..project2.main import NUMBERS
from . import TEST_INDEXES, boosted_mfcc_from_file
from .dtw_single_template_time_sync import recognize_number

BEST_PRUNING_THRESHOLD = 13.0


def main():
    # TODO: Change the templates.
    template_mfcc_s = [
        (boosted_mfcc_from_file(f"recordings/{number}10.wav"), number)
        for number in NUMBERS
    ]

    accuracies = [
        recognize_number(number, template_mfcc_s, BEST_PRUNING_THRESHOLD)
        / len(TEST_INDEXES)
        for number in NUMBERS
    ]
    print(
        f"""Number|{"|".join(NUMBERS)}|Average
{"|".join("-"for _ in range(len(NUMBERS) + 2))}
Accuracy|{"|".join(str(a) for a in accuracies)}|{sum(accuracies) / len(accuracies):.2f}"""
    )

    # TODO: Plot graphs.


main() if __name__ == "__main__" else None
