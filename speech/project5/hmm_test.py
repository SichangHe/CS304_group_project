"""Run with `python3 -m speech.project5.hmm_test`."""

import unittest
from pprint import pprint

import numpy as np

from speech.project5.hmm import (
    HMMState,
    _align_sequence_and_hmm_states,
    align_sequence,
    align_sequence_train,
)


class TestAudio(unittest.TestCase):
    def test_new_align_impl(self):
        np.random.seed(0)
        mean1 = np.random.normal(0, 1, 39).astype(np.float32)
        mean2 = np.random.normal(0, 2, 39).astype(np.float32)
        mean3 = np.random.normal(1, 1, 39).astype(np.float32)
        mean4 = np.random.normal(-1, 1, 39).astype(np.float32)
        mean5 = np.random.normal(1, 2, 39).astype(np.float32)
        covariance = np.eye(39, dtype=np.float32)
        covariance = np.abs(
            np.diag(np.diag(np.random.normal(2, 2, (39, 39)).astype(np.float32)))
        )
        num_samples = 200
        samples = np.random.multivariate_normal(mean1, covariance, num_samples).astype(
            np.float32
        )
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

        root = HMMState.root()
        n0 = HMMState(
            label=None,
            parent=None,
            means=[mean1],
            covariances=[np.diag(covariance.T)],
            weights=[1.0],
            transition_loss={},
            nth_state=0,
            exit_prob=0
        )
        n1 = HMMState(
            label=1,
            parent=None,
            means=[mean2],
            covariances=[np.diag(covariance.T)],
            weights=[1.0],
            transition_loss={},
            nth_state=1,
            exit_prob=0
        )
        n2 = HMMState(
            label=2,
            parent=None,
            means=[mean3],
            covariances=[np.diag(covariance.T)],
            weights=[1.0],
            transition_loss={},
            nth_state=2,
            exit_prob=0
        )
        n3 = HMMState(
            label=3,
            parent=None,
            means=[mean4],
            covariances=[np.diag(covariance.T)],
            weights=[1.0],
            transition_loss={},
            nth_state=3,
            exit_prob=0
        )
        n4 = HMMState(
            label=4,
            parent=None,
            means=[mean5],
            covariances=[np.diag(covariance.T)],
            weights=[1.0],
            transition_loss={},
            nth_state=4,
            exit_prob=0
        )
        root.transition_loss = {n4: 1.0}
        n0.transition_loss = {root: 0.0, n0: 0.5}
        n1.transition_loss = {n1: 0.5, n0: 0.5}
        n2.transition_loss = {n2: 0.5, n1: 0.5}
        n3.transition_loss = {n3: 0.5, n2: 0.5}
        n4.transition_loss = {n4: 0.5, n3: 0.5}
        n1.parent = n0
        n2.parent = n1
        n3.parent = n2
        n4.parent = n3
        states = [n0, n1, n2, n3, n4]

        alignment2, score2 = align_sequence_train(samples[0:40], states)
        print("Alignment and score with new implementation:")
        pprint(alignment2)
        print(score2)

        print("Last losses from inference:")
        last_losses = _align_sequence_and_hmm_states(samples[0:40], [root] + states)
        pprint(last_losses)


unittest.main() if __name__ == "__main__" else None
