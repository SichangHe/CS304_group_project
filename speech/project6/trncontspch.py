"""Training digit HMMs from continuous speech.
Run as `python3 -m speech.project6.trncontspch`"""

from speech.project5.hmm import HMM_Single, HMMState
from speech.project5.phone_rand import build_digit_hmms, load_silence_hmms
from speech.project6.digit_sequences import SEQUENCES


def hmm_states_from_sequence(sequence: str, digit_hmms: list[HMM_Single]):
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

    return [state for states in sequence_hmm_states for state in states], silence_states


def main() -> None:
    digit_hmms = build_digit_hmms()
    for sequence in SEQUENCES:
        emitting_states, silence_states = hmm_states_from_sequence(sequence, digit_hmms)


main() if __name__ == "__main__" else None
