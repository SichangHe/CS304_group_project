"""Run with `python3 -m speech.project6.hmm_test`."""

import unittest

import numpy as np
from speech.project3 import boosted_mfcc_from_file
from speech.project5.hmm import align_sequence_cont_train

from speech.project5.phone_rand import build_digit_hmms, load_silence_hmms
from speech.project6.trncontspch import hmm_states_from_sequence


class TestAudio(unittest.TestCase):
    def test_continuous_alignment(self):
        digit_hmms = build_digit_hmms()
        states, silence_states = hmm_states_from_sequence("165890", digit_hmms)
        np.random.seed(0)
        samples = boosted_mfcc_from_file("recordings/123456.wav")
        alignment, score = align_sequence_cont_train(samples, states, silence_states)
        print(alignment)
        print(score)

    def test_save_features(self):
        digit_hmms = build_digit_hmms()
        print(digit_hmms[1].features[1])


unittest.main() if __name__ == "__main__" else None
