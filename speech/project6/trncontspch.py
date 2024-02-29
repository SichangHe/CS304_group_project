"""Training digit HMMs from continuous speech.
Run as `python3 -m speech.project6.trncontspch`"""

import itertools
from typing import Final

from cache_to_disk import cache_to_disk

from speech import FloatArray
from speech.project2.main import NUMBERS
from speech.project3 import boosted_mfcc_from_file
from speech.project5.hmm import (
    HMM_Single,
    HMMState,
    align_sequence_cont_train,
    clone_hmm_states,
)
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


@cache_to_disk(2)
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
    alignment: dict[int, list[tuple[int, int]]] = {}
    new_alignment: dict[int, list[tuple[int, int]]] = {}

    while not tolerate_alignment_diff(new_alignment, alignment):
        # Did not converge. Train again.
        digit_features = new_digit_features
        alignment = new_alignment
        digit_hmms = {
            digit: HMM_Single(digit, features, n_states, n_gaussians)
            for digit, features in digit_features.items()
        }
        # Reset `new_digit_features` with `isolated_digit_features`.
        new_digit_features = {
            digit: features for digit, features in isolated_digit_features.items()
        }
        new_alignment = {}

        digit_hmm_list = [digit_hmms[digit] for digit in range(10)]
        for sequence, features in sequence_features.items():
            hmm_states = hmm_states_from_sequence(sequence, digit_hmm_list, silence_hmm)
            result_list = [
                align_sequence_cont_train(feature, hmm_states) for feature in features
            ]
            feature_list = [result[0] for result in result_list]
            alignment_list = [result[1] for result in result_list]

            concatenated_feature_dict = {
                k: [d[k] for d in feature_list if k in d]
                for k in feature_list[0].keys()
            }
            concatenated_alignment_dict = {
                k: [d[k] for d in alignment_list if k in d]
                for k in alignment_list[0].keys()
            }
            for key in new_digit_features:
                new_digit_features[key] = (
                    new_digit_features[key] + concatenated_feature_dict[key]
                )
            for key in concatenated_alignment_dict:
                new_alignment[key] = (
                    new_alignment.get(key, []) + concatenated_alignment_dict[key]
                )

    return digit_hmms


def tolerate_alignment_diff(a, b, eps=0.05):
    if len(a) == 0 or len(b) == 0:
        return False
    l1 = list(itertools.chain.from_iterable(a.values()))
    l2 = list(itertools.chain.from_iterable(b.values()))
    assert len(l1) == len(l2)
    print(f"Diff: {sum(x != y for x, y in zip(l1, l2))}, Total: {len(l1)}")
    return sum(x != y for x, y in zip(l1, l2)) / len(l1) < eps


def main() -> None:
    train_digit_sequences()


main() if __name__ == "__main__" else None
