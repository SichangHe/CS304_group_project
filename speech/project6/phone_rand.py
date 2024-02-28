"""Recognize 25 valid random telephone numbers and report accuracy.
Run as `python3 -m speech.project6.phone_rand`."""

from logging import debug

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from speech.project3 import boosted_mfcc_from_file
from speech.project4.segment import levenshtein_distance
from speech.project5.hmm import match_sequence_against_hmm_states
from speech.project5.phone_hmm import build_hmm_graph
from speech.project5.phone_rand import (
    TELEPHONE_NUMBERS,
    avg,
    load_silence_hmms,
    recording_for_number,
)
from speech.project6.trncontspch import train_digit_sequences


def main() -> None:
    digit_hmm_dict = train_digit_sequences()
    digit_hmms = [digit_hmm_dict[digit] for digit in range(10)]
    silence_single_hmm = load_silence_hmms()

    non_emitting_states, emitting_states = build_hmm_graph(
        digit_hmms, silence_single_hmm
    )
    debug(
        "non_emitting_states=%s",
        [(state, state.transition_loss) for state in non_emitting_states],
    )
    debug("emitting_states=%s", emitting_states)

    recognitions = []
    distances = []
    word_accuracies = []
    for number in TELEPHONE_NUMBERS:
        print(f"Recognizing `{number}`.")
        mfcc = boosted_mfcc_from_file(recording_for_number(number))
        recognition = match_sequence_against_hmm_states(
            mfcc, non_emitting_states, emitting_states, beam_width=4000.0
        )
        recognition = "".join(map(str, recognition))
        print(f"Recognized as `{recognition}`.")
        recognitions.append(recognition)
        distance = levenshtein_distance(number, recognition)
        word_accuracy = max(0.0, (len(number) - distance) * 100.0 / len(number))
        distances.append(distance)
        word_accuracies.append(word_accuracy)
        print(f"Levenshtein distance: {distance}, word accuracy: {word_accuracy:.2f}")
    n_correct_sentence = sum(1 for d in distances if d == 0)
    sentence_accuracy = n_correct_sentence * 100.0 / len(TELEPHONE_NUMBERS)
    n_correct_digits = sum(
        len(number) - d for number, d in zip(TELEPHONE_NUMBERS, distances)
    )
    print(
        f"""
Sentence accuracy: {sentence_accuracy:.2f}%—{n_correct_sentence} telephone numbers were recognized correctly.
Average word accuracy: {avg(word_accuracies):.2f}%—{n_correct_digits} digits were recognized correctly."""
    )

    ax: Axes
    fig, ax = plt.subplots()
    bars = ax.bar(TELEPHONE_NUMBERS, word_accuracies)
    for bar, recognition in zip(bars, recognitions):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            recognition,
            ha="center",
            va="bottom",
            rotation=60,
        )
    ax.grid()
    ax.set_xlabel("Telephone Number")
    ax.set_ylabel("% Accurate Word")
    plt.xticks(ha="center", rotation=60)
    plt.show(block=True)
    fig.savefig("telephone_number_recognition.png", bbox_inches="tight")


main() if __name__ == "__main__" else None
