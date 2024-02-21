"""Hidden Markov model from unrestricted digits."""

import numpy as np

from speech.project5.hmm import HMM_Single, HMMState, clone_hmm_states

HALF_LOSS = -np.log(0.5)
"""Negative log probability of a half."""


def build_hmm_graph(digit_hmms: list[HMM_Single], transition_loss=HALF_LOSS):
    """Connect HMM states to create the unrestricted number recognizer."""
    non_emitting_state = HMMState.root()
    # Defensively copy the input.
    digit_state_list = [
        clone_hmm_states(hmm_single.states) for hmm_single in digit_hmms
    ]

    for digit_states in digit_state_list:
        digit_states[0].transition_loss[non_emitting_state] = 0.0
        non_emitting_state.transition_loss[digit_states[-1]] = (
            # Extra loss to discourage insertions.
            digit_states[-1].exit_loss
            + transition_loss
        )

    emitting_states = [
        state for digit_states in digit_state_list for state in digit_states
    ]
    return [non_emitting_state], emitting_states
