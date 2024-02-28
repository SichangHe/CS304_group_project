"""Training digit HMMs from continuous speech.
Run as `python3 -m speech.project6.trncontspch`"""

from typing import Final

from speech import FloatArray
from speech.project2.main import NUMBERS
from speech.project3 import boosted_mfcc_from_file
from speech.project5.hmm import HMM_Single, HMMState, clone_hmm_states
from speech.project5.phone_rand import (
    ALL_TRAINING_INDEXES,
    build_digit_hmms,
    load_silence_hmms,
)
from speech.project6.digit_sequences import INDEXES, SEQUENCES


def hmm_states_from_sequence(
    sequence: str, digit_hmms: list[HMM_Single], silence_hmm: HMMState
) -> list[HMMState]:
    """Connect `digit_hmms` for digits `sequence` and pad with silence at both
    ends."""
    sequence_hmm_state_lists = [
        # Defensive copy.
        clone_hmm_states(digit_hmms[int(digit)].states)
        for digit in sequence
    ]
    ## Connect digits.
    for prev_states, next_states in zip(
        sequence_hmm_state_lists, sequence_hmm_state_lists[1:]
    ):
        next_states[0].transition_loss[prev_states[-1]] = prev_states[-1].exit_loss

    ## Insert silence.
    # Defensive copy silence states.
    start_silence_state = clone_hmm_states([silence_hmm])[0]
    end_silence_state = clone_hmm_states([silence_hmm])[0]
    digit_states = [
        states for state_list in sequence_hmm_state_lists for states in state_list
    ]
    digit_states[0].transition_loss[start_silence_state] = start_silence_state.exit_loss
    end_silence_state.transition_loss[digit_states[-1]] = digit_states[-1].exit_loss

    return [start_silence_state] + digit_states + [end_silence_state]


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
    silence_hmm = load_silence_hmms()

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

        digit_hmm_list = [digit_hmms[digit] for digit in range(10)]
        for sequence, features in sequence_features.items():
            hmm_states = hmm_states_from_sequence(sequence, digit_hmm_list, silence_hmm)
            # TODO: Align sequence against `hmm_states` and add the resulting
            # features to `digit_features`.

    return digit_hmms


def main() -> None:
    digit_hmms = build_digit_hmms()
    for sequence in SEQUENCES:
        emitting_states, silence_states = hmm_states_from_sequence(sequence, digit_hmms)


main() if __name__ == "__main__" else None
