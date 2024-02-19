"""Run with `python3 -m speech.project5.hmm_test`."""

import unittest

import numpy as np

from speech.project5.hmm import HMMState, align_sequence, align_sequence_new


class TestAudio(unittest.TestCase):
    def test_new_align_impl(self):
        np.random.seed(0)
        mean1 = np.random.normal(0, 1, 39).astype(np.float32)
        mean2 = np.random.normal(0, 2, 39).astype(np.float32)
        mean3 = np.random.normal(1, 1, 39).astype(np.float32)
        mean4 = np.random.normal(-1, 1, 39).astype(np.float32)
        mean5 = np.random.normal(1, 2, 39).astype(np.float32)
        covariance = np.eye(39)
        covariance = np.abs(np.diag(np.diag(np.random.normal(2, 2, (39, 39)))))
        num_samples = 200
        samples = np.random.multivariate_normal(mean1, covariance, num_samples)
        # s = [samples[i : i + 40] for i in range(0, 161, 10)]
        alignment, score = align_sequence(
            samples[0:40],
            [[mean1], [mean2], [mean3], [mean4], [mean5]],
            [[covariance], [covariance], [covariance], [covariance], [covariance]],
            np.array(
                [
                    [0.5, 0.5, 0, 0, 0],
                    [0, 0.5, 0.5, 0, 0],
                    [0, 0, 0.5, 0.5, 0],
                    [0, 0, 0, 0.5, 0.5],
                    [0, 0, 0, 0, 0.5],
                ],
                dtype=np.float32,
            ),
        )
        print("Alignment and score with legacy implementation:")
        print(score)
        print(alignment)

        root = HMMState(
            parent=None,
            mean=[mean1],
            covariance=[np.diag(covariance.T)],
            transition={},
            nth_state=0,
        )
        n1 = HMMState(
            parent=None,
            mean=[mean2],
            covariance=[np.diag(covariance.T)],
            transition={},
            nth_state=1,
        )
        n2 = HMMState(
            parent=None,
            mean=[mean3],
            covariance=[np.diag(covariance.T)],
            transition={},
            nth_state=2,
        )
        n3 = HMMState(
            parent=None,
            mean=[mean4],
            covariance=[np.diag(covariance.T)],
            transition={},
            nth_state=3,
        )
        n4 = HMMState(
            parent=None,
            mean=[mean5],
            covariance=[np.diag(covariance.T)],
            transition={},
            nth_state=4,
        )
        root.transition = {root: 0.5, n1: 0.5}
        n1.transition = {n1: 0.5, n2: 0.5}
        n2.transition = {n2: 0.5, n3: 0.5}
        n3.transition = {n3: 0.5, n4: 0.5}
        n4.transition = {n4: 0.5}
        n1.parent = root
        n2.parent = n1
        n3.parent = n2
        n4.parent = n3
        states = [root, n1, n2, n3, n4]

        alignment2, score2 = align_sequence_new(samples[0:40], states)
        print("Alignment and score with new implementation:")
        print(score2)
        print(alignment2)


unittest.main() if __name__ == "__main__" else None
