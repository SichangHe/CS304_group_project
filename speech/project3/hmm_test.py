"""Run with `python3 -m speech.project3.hmm_test`."""
import unittest

import numpy as np

from speech.project3.hmm import HMM


class TestAudio(unittest.TestCase):
    def test_1(self):
        mean = np.random.normal(0, 1, 40)
        covariance = np.eye(40)
        num_samples = 200
        np.random.seed(0)
        samples = np.random.multivariate_normal(mean, covariance, num_samples)
        s = [samples[i : i + 40] for i in range(0, 161, 10)]
        dtw = HMM()
        dtw.fit(s, 5, 1)
        another_samples = np.random.multivariate_normal(
            np.random.normal(2, 1, 40), np.eye(40) * 1, 5
        )
        for i in range(10):
            print(dtw.predict(samples[i]))
        print("another")
        for s in another_samples:
            print(dtw.predict(s))


unittest.main() if __name__ == "__main__" else None
