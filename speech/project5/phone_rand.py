"""Recognize 25 valid random telephone numbers and report accuracy.
Run as `python3 -m speech.project5.phone_rand`."""

from logging import debug

from speech.project2.main import NUMBERS
from speech.project3 import TEMPLATE_INDEXES, boosted_mfcc_from_file
from speech.project5.hmm import (
    match_sequence_against_hmm_states,
    single_hmm_w_template_file_names,
)
from speech.project5.phone_hmm import build_hmm_graph

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


def recording_for_number(number: str) -> str:
    """Return the recording file for the given number."""
    return f"recordings/{number}.wav"


def main() -> None:
    template_files_list = [
        [f"recordings/{number}{i}.wav" for i in TEMPLATE_INDEXES]
        for number in NUMBERS[:10]
    ]
    single_hmms = [
        single_hmm_w_template_file_names(
            number, template_files, n_states=5, n_gaussians=2
        )
        for number, template_files in zip(range(10), template_files_list)
    ]

    non_emitting_states, emitting_states = build_hmm_graph(single_hmms)
    debug(
        "non_emitting_states=%s",
        [(state, state.transition_loss) for state in non_emitting_states],
    )
    debug("emitting_states=%s", emitting_states)

    for number in TELEPHONE_NUMBERS:
        print(f"Recognizing `{number}`.")
        mfcc = boosted_mfcc_from_file(recording_for_number(number))
        recognition = match_sequence_against_hmm_states(
            mfcc, non_emitting_states, emitting_states, beam_width=1500.0
        )
        print(f"Recognized as `{recognition}`.")
        # TODO: Compare the recognition with the expected number.


main() if __name__ == "__main__" else None
