"""Hidden Markov Model to recognize telephone numbers."""

from speech.project5.hmm import HMM_Single, HMMState, clone_hmm_states


def build_hmm_graph(digit_hmms: list[HMM_Single]):
    """Connect HMM states to create the telephone number recognizer."""
    non_emitting_states = [HMMState.root() for _ in range(8)]
    # Jumping over three digits.
    non_emitting_states[3].transition_loss[non_emitting_states[0]] = 0.0

    digit_state_layers = [  # First digit.
        [
            clone_hmm_states(hmm_single.states)
            for hmm_single in digit_hmms
            if (hmm_single.label is not None and hmm_single.label > 1)
        ]
    ] + [
        [clone_hmm_states(hmm_single.states) for hmm_single in digit_hmms]
        for _ in range(7)
    ]  # Other digits.

    # TODO: Handle silence around non_emitting_states[3]
    # Jump from non_emitting_states[3] to the silence state and back.
    slience_hmm = HMM_Single()
    slience_states = slience_hmm.states
    slience_states[0].transition_loss[non_emitting_states[3]] = 0
    for digit_states in digit_state_layers[4]:
        digit_states[0].transition_loss[slience_states[-1]] = slience_states[
            -1
        ].exit_loss

    for prev_non_emitting_state, digit_state_layer, next_non_emitting_state in zip(
        non_emitting_states, digit_state_layers, non_emitting_states[1:]
    ):
        for digit_states in digit_state_layer:
            # TODO: Add transition loss between non-emitting states and digit states.
            digit_states[0].transition_loss[prev_non_emitting_state] = 0.0
            next_non_emitting_state.transition_loss[digit_states[-1]] = digit_states[
                -1
            ].exit_loss

    emitting_states = [
        state
        for digit_state_layer in digit_state_layers
        for digit_states in digit_state_layer
        for state in digit_states
    ]
    return non_emitting_states, emitting_states
