"""Unrestricted number of digits.
Run as `python3 -m speech.project5.unrestricted_digits`."""

from logging import debug

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from speech.project3 import boosted_mfcc_from_file
from speech.project4.segment import levenshtein_distance
from speech.project5.hmm import HMM_Single, match_sequence_against_hmm_states
from speech.project5.phone_rand import avg, build_digit_hmms, recording_for_number
from speech.project5.unrestricted_hmm import HALF_LOSS, build_hmm_graph

plt.rcParams["font.size"] = 24
plt.rcParams["lines.linewidth"] = 4
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
TRANSITION_LOSSES = HALF_LOSS / 10_000 * np.linspace(1, 1_000_000, 11)


def test(digit_hmms: list[HMM_Single], transition_loss: float):
    print(f"\nTesting with transition loss {transition_loss}.")
    non_emitting_states, emitting_states = build_hmm_graph(digit_hmms, transition_loss)
    debug(
        "non_emitting_states=%s",
        [(state, state.transition_loss) for state in non_emitting_states],
    )
    debug("emitting_states=%s", emitting_states)

    recognitions: list[str] = []
    distances: list[float] = []
    word_error_rates: list[float] = []
    for number in DIGIT_STRINGS:
        print(f"Recognizing `{number}`.")
        mfcc = boosted_mfcc_from_file(recording_for_number(number))
        recognition = match_sequence_against_hmm_states(
            mfcc, non_emitting_states, emitting_states, beam_width=4000.0
        )
        recognition = "".join(map(str, recognition))
        print(f"Recognized as `{recognition}`.")
        recognitions.append(recognition)
        distance = levenshtein_distance(number, recognition)
        word_error_rate = distance * 100.0 / len(number)
        distances.append(distance)
        word_error_rates.append(word_error_rate)
        print(
            f"Levenshtein distance: {distance}, distance per digit: {word_error_rate}"
        )
    n_correct_sentence = sum(1 for d in distances if d == 0)
    sentence_accuracy = n_correct_sentence * 100.0 / len(DIGIT_STRINGS)
    print(
        f"""
Sentence accuracy: {sentence_accuracy:.2f}%—{n_correct_sentence} digit string were recognized correctly.
Avg word error rate: {avg(word_error_rates):.2f}%."""
    )
    return (
        recognitions,
        distances,
        word_error_rates,
        sentence_accuracy,
    )


def main() -> None:
    ax: Axes
    digit_hmms = build_digit_hmms()

    metrics_list: list[tuple[list[str], list[float], list[float], float]] = []
    for transition_loss in TRANSITION_LOSSES:
        metrics = test(digit_hmms, transition_loss)
        metrics_list.append(metrics)

    fig, ax = plt.subplots()
    ax.plot(
        TRANSITION_LOSSES,
        [sentence_accuracy for _, _, _, sentence_accuracy in metrics_list],
        label="% Accurate Sentence",
    )
    ax.plot(
        TRANSITION_LOSSES,
        [avg(word_error_rates) for _, _, word_error_rates, _ in metrics_list],
        label="Average % Accurate Word",
    )
    ax.grid()
    ax.set_xlabel("Transition Loss")
    ax.legend()
    plt.xticks(ha="center", rotation=60)
    plt.show(block=True)
    fig.savefig("transition_losses_vs_digit_accuracy.png", bbox_inches="tight")

    best_transition_loss, (
        recognitions,
        _,
        word_error_rates,
        sentence_accuracy,
    ) = min(
        zip(TRANSITION_LOSSES, metrics_list), key=lambda metrics: avg(metrics[1][2])
    )
    print(
        f"""
Best transition loss: {best_transition_loss}
Sentence accuracy: {sentence_accuracy:.2f}%.
Average word error rate: {avg(word_error_rates):.2f}%."""
    )
    fig, ax = plt.subplots()
    bars = ax.bar(DIGIT_STRINGS, word_error_rates)
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
    ax.set_xlabel("Digit String")
    ax.set_ylabel("% Word Error Rate")
    plt.xticks(ha="center", rotation=60)
    plt.show(block=True)
    fig.savefig("digit_string_recognition.png", bbox_inches="tight")


main() if __name__ == "__main__" else None
