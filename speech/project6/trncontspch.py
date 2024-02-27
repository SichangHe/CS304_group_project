"""Training digit HMMs from continuous speech.
Run as `python3 -m speech.project6.trncontspch`"""

from speech.project5.hmm import HMM_Single, HMMState
from speech.project5.phone_rand import build_digit_hmms, load_silence_hmms
from speech.project6.digit_sequences import SEQUENCES


def hmm_states_from_sequence(sequence: str, digit_hmms: list[HMM_Single]):
    silence_states = [load_silence_hmms() for _ in range(len(sequence) + 1)]
    sequence_hmm_states = [digit_hmms[int(digit)].states for digit in sequence]
    for i, sequence_hmm_state in enumerate(sequence_hmm_states):
        sequence_hmm_state[0].transition_loss[silence_states[i]] = 0
        silence_states[i].transition_loss[silence_states[i]] = 100  # TODO
        silence_states[i + 1].transition_loss[sequence_hmm_state[-1]] = (
            sequence_hmm_state[-1].exit_loss
        )
    silence_states[-1].transition_loss[silence_states[-1]] = 100 # TODO

    return [state for states in sequence_hmm_states for state in states], silence_states


def main() -> None:
    digit_hmms = build_digit_hmms()
    for sequence in SEQUENCES:
        emitting_states, silence_states = hmm_states_from_sequence(sequence, digit_hmms)


main() if __name__ == "__main__" else None
