"""Training digit HMMs from continuous speech.
Run as `python3 -m speech.project6.trncontspch`"""

from typing import Final

from speech import FloatArray
from speech.project2.main import NUMBERS
from speech.project3 import boosted_mfcc_from_file
from speech.project5.hmm import HMM_Single, HMMState
from speech.project5.phone_rand import (
    ALL_TRAINING_INDEXES,
    build_digit_hmms,
    load_silence_hmms,
)
from speech.project6.digit_sequences import INDEXES, SEQUENCES


# FIXME: Copy the input digits, and return list of states.
def hmm_states_from_sequence(sequence: str, digit_hmms: dict[int, HMM_Single]):
    silence_states = [load_silence_hmms(), load_silence_hmms()]
    sequence_hmm_states = [digit_hmms[int(digit)].states for digit in sequence]

    silence_to_digit_loss = 100
    stay_silence_loss = 100
    transition_loss = 100

    sequence_hmm_states[0][0].transition_loss[silence_states[0]] = silence_to_digit_loss
    silence_states[0].transition_loss[silence_states[0]] = stay_silence_loss
    silence_states[1].transition_loss[sequence_hmm_states[-1][0]] = sequence_hmm_states[
        -1
    ][0].exit_loss
    silence_states[1].transition_loss[silence_states[1]] = stay_silence_loss

    for prev, next in zip(sequence_hmm_states, sequence_hmm_states[1:]):
        next[0].transition_loss[prev[-1]] = transition_loss


def train_digit_sequences(n_states=5, n_gaussians=4) -> dict[int, HMM_Single]:
    """Train digit HMMs using continuous speech digit sequences, bootstrapping
    with isolated digit sequences."""
    isolated_digit_features: Final = {
        digit: [
            boosted_mfcc_from_file(f"recordings/{number}{i}.wav")
            for i in ALL_TRAINING_INDEXES
        ]
        for digit, number in enumerate(NUMBERS[:10])
    }
    sequence_features = {
        sequence: [
            boosted_mfcc_from_file(f"recordings/{sequence}_{index}.wav")
            for index in INDEXES
        ]
        for sequence in SEQUENCES
    }

    digit_hmms: dict[int, HMM_Single] = {}
    digit_features: dict[int, list[FloatArray]] = {}
    new_digit_features = {
        digit: features for digit, features in isolated_digit_features.items()
    }
    while new_digit_features != digit_features:
        # Did not converge. Train again.
        digit_features = new_digit_features
        digit_hmms = {
            digit: HMM_Single(digit, features, n_states, n_gaussians)
            for digit, features in digit_features.items()
        }
        # Reset `new_digit_features` with `isolated_digit_features`.
        new_digit_features = {
            digit: features for digit, features in isolated_digit_features.items()
        }

        for sequence, features in sequence_features.items():
            hmm_states = hmm_states_from_sequence(sequence, digit_hmms)
            # TODO: Align sequence against `hmm_states` and add the resulting
            # features to `digit_features`.

    return digit_hmms


def main() -> None:
    digit_hmms = build_digit_hmms()
    for sequence in SEQUENCES:
        emitting_states, silence_states = hmm_states_from_sequence(sequence, digit_hmms)


main() if __name__ == "__main__" else None
