"""Recognize 25 valid random telephone numbers and report accuracy.
Run as `python3 -m speech.project5.phone_rand`."""

from logging import debug

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from speech.project2.main import NUMBERS
from speech.project3 import boosted_mfcc_from_file
from speech.project4.segment import levenshtein_distance
from speech.project5.hmm import (
    match_sequence_against_hmm_states,
    single_hmm_w_template_file_names,
)
from speech.project5.phone_hmm import build_hmm_graph

plt.rcParams["font.size"] = 24
ALL_TRAINING_INDEXES = range(20)
TELEPHONE_NUMBERS = [
    "8765",
    "2356",
    "4198",
    "7432",
    "5321",
    "6214",
    "8743021",
    "3156",
    "9821",
    "7245981",
    "1367",
    "5432",
    "2198473",
    "8976",
    "4298513",
    "6532",
    "5189",
    "9271564",
    "7345",
    "6291087",
    "4821",
    "7698432",
    "5412968",
    "8654123",
    "2371098",
]


def avg(lst: list[float]) -> float:
    return sum(lst) / len(lst)


def recording_for_number(number: str) -> str:
    """Return the recording file for the given number."""
    return f"recordings/{number}.wav"


def load_silence_hmms():
    silence_recordings_files = [f"recordings/silence{n}.wav" for n in range(1, 10)]
    silence_single_hmms = single_hmm_w_template_file_names(
        -1, silence_recordings_files, n_states=1, n_gaussians=4
    )
    assert len(silence_single_hmms.states) == 1
    return silence_single_hmms.states[0]


def build_digit_hmms(indices=ALL_TRAINING_INDEXES):
    template_files_list = [
        [f"recordings/{number}{i}.wav" for i in indices] for number in NUMBERS[:10]
    ]
    return [
        single_hmm_w_template_file_names(
            number, template_files, n_states=5, n_gaussians=4
        )
        for number, template_files in zip(range(10), template_files_list)
    ]


def main() -> None:
    digit_hmms = build_digit_hmms()
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
