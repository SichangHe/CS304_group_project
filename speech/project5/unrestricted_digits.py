"""Unrestricted number of digits.
Run as `python3 -m speech.project5.unrestricted_digits`."""

from logging import debug

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from speech.project3 import boosted_mfcc_from_file
from speech.project4.segment import levenshtein_distance
from speech.project5.hmm import match_sequence_against_hmm_states
from speech.project5.phone_rand import build_digit_hmms, recording_for_number
from speech.project5.unrestricted_hmm import build_hmm_graph

plt.rcParams["font.size"] = 24
DIGIT_STRINGS = [
    "911385",
    "826414052002",
    "8212176342",
    "7343332190377",
    "2212",
    "123456",
    "6890372344",
    "72184347924",
    "55555",
    "37274921",
]


def main() -> None:
    digit_hmms = build_digit_hmms()
    # TODO: Determine the  optimal insertion penalty empirically
    non_emitting_states, emitting_states = build_hmm_graph(digit_hmms)
    debug(
        "non_emitting_states=%s",
        [(state, state.transition_loss) for state in non_emitting_states],
    )
    debug("emitting_states=%s", emitting_states)

    distances = []
    normalized_distances = []
    for number in DIGIT_STRINGS:
        print(f"Recognizing `{number}`.")
        mfcc = boosted_mfcc_from_file(recording_for_number(number))
        recognition = match_sequence_against_hmm_states(
            mfcc, non_emitting_states, emitting_states, beam_width=1500.0
        )
        recognition = "".join(map(str, recognition))
        print(f"Recognized as `{recognition}`.")
        distance = levenshtein_distance(number, recognition)
        normalized_distance = distance / len(number)
        distances.append(distance)
        normalized_distances.append(normalized_distance)
        print(
            f"Levenshtein distance: {distance}, distance per digit: {normalized_distance}"
        )
    n_correct_sentence = sum(1 for d in distances if d == 0)
    sentence_accuracy = n_correct_sentence * 100.0 / len(DIGIT_STRINGS)
    n_correct_digits = sum(
        len(number) - d for number, d in zip(DIGIT_STRINGS, distances)
    )
    word_accuracy = (
        n_correct_digits * 100.0 / sum(len(number) for number in DIGIT_STRINGS)
    )
    print(
        f"""
Sentence accuracy: {sentence_accuracy:.2f}%—{n_correct_sentence} digit string were recognized correctly.
Word error rate: {word_accuracy:.2f}%."""
    )

    ax: Axes
    fig, ax = plt.subplots()
    ax.bar(DIGIT_STRINGS, normalized_distances)
    ax.grid()
    ax.set_xlabel("Digit String")
    ax.set_ylabel("Word Error Rate")
    plt.xticks(rotation=70, ha="right")
    plt.show(block=True)
    fig.savefig("digit_string_recognition.png", bbox_inches="tight")


main() if __name__ == "__main__" else None
