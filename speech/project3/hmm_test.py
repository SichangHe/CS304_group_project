"""Run with `python3 -m speech.project3.hmm_test`."""

import unittest

import numpy as np

from speech.project3.hmm import HMM_Single


class TestAudio(unittest.TestCase):
    def test_1(self):
        mean = np.random.normal(0, 1, 39)
        covariance = np.eye(39)
        num_samples = 200
        np.random.seed(0)
        samples = np.random.multivariate_normal(mean, covariance, num_samples).astype(
            np.float32
        )
        s = [samples[i : i + 40] for i in range(0, 161, 10)]
        dtw = HMM_Single(s, 5, 1)
        another_samples = np.random.multivariate_normal(
            np.random.normal(2, 1, 39), np.eye(39) * 1, 200
        ).astype(np.float32)
        a_s = [another_samples[i : i + 40] for i in range(0, 161, 10)]
        for i in range(10):
            print(dtw.predict_score(s[i]))
        print("another")
        for i in range(10):
            print(dtw.predict_score(a_s[i]))


unittest.main() if __name__ == "__main__" else None
