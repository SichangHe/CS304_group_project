"""Recognize 25 valid random telephone numbers and report accuracy.
Run as `python3 -m speech.project5.phone_rand`."""

from speech.project2.main import NUMBERS
from speech.project3 import TEMPLATE_INDEXES
from speech.project3.hmm import single_hmm_w_template_file_names
from speech.project5.hmm import _align_sequence_and_hmm_states
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
    template_files = [
        [f"recordings/{number}{i}.wav" for i in TEMPLATE_INDEXES] for number in NUMBERS
    ]
    single_hmms = [
        single_hmm_w_template_file_names(t, n_states=5, n_gaussians=2)
        for t in template_files
    ]

    non_emitting_states, emitting_states = build_hmm_graph(single_hmms)
    # TODO:
    for number_sequences in TELEPHONE_NUMBERS:
        _align_sequence_and_hmm_states(
            number_sequences, non_emitting_states, emitting_states
        )
        # TODO:


main() if __name__ == "__main__" else None
