from abc import ABC

import numpy as np
from numpy.typing import NDArray
from scipy.stats import multivariate_normal

from ..project2 import read_audio_file
from ..project2.lib import (
    N_MFCC_COEFFICIENTS,
    derive_cepstrum_velocities,
    mfcc_homebrew,
)

TEST_INDEXES = range(1, 10, 2)
"""Indexes for test numbers."""

INF_FLOAT32 = np.float32(np.inf)


class NodeCostFn(ABC):
    """Returns node cost given input frame and template frame index."""

    def __call__(
        self, input_frame: NDArray[np.float32], template_frame_index: int
    ) -> np.float32:
        raise NotImplementedError(input_frame, template_frame_index)


def align_sequence(sequence, means, covariances, transition_probs):
    num_states = len(means)
    sequence_length = len(sequence)

    viterbi_trellis = np.full((num_states, sequence_length), -np.inf)
    backpointers = np.zeros((num_states, sequence_length), dtype=int)

    # start from first state
    viterbi_trellis[0, 0] = np.log(
        multivariate_normal.pdf(
            sequence[0], mean=means[0], cov=covariances[0], allow_singular=True
        )
    )

    for t in range(1, sequence_length):
        for state in range(num_states):
            emission_prob = multivariate_normal.pdf(
                sequence[t],
                mean=means[state],
                cov=covariances[state],
                allow_singular=True,
            )
            np.log(transition_probs[:, state])
            viterbi_scores = (
                (viterbi_trellis[:, t - 1])
                + np.log(transition_probs[:, state])
                + np.log(emission_prob)
            )

            viterbi_trellis[state, t] = np.max(viterbi_scores)
            backpointers[state, t] = np.argmax(viterbi_scores)

    # Trace back
    # alignment = [np.argmax(viterbi_trellis[:, -1])]
    # start from last state, not highest score state
    alignment = [num_states - 1]
    for t in range(sequence_length - 1, 0, -1):
        alignment.append(backpointers[alignment[-1], t])

    alignment.reverse()
    return alignment


class HMM:
    def __init__(self):
        self.means = []
        self.variances = []
        self.n_states = 0
        self.transition_matrix = None

    def fit(self, data: list[NDArray[np.float32]], n_states=5):
        """
        Fits the model to the provided training data using segmental K-means.

        Parameters:
        data: The training data.
            It should have the shape (N, l) or (N, l, d), where N is the number of training samples
            and l is the length of each training sample.
            Each training sample can be a scalar or a vector.
        """
        self._raw_data = data
        self.n_states = n_states
        self.n_samples = len(data)
        self.transition_matrix = np.zeros((n_states, n_states))
        self._init()
        print(f"initial group:\n {self.grouped_data}")
        MAX_ITERS = 50
        prev_groups = None
        for _ in range(MAX_ITERS):
            self._update()
            if prev_groups is not None and np.all(prev_groups == self.grouped_data):
                print("coverges")
                break
            prev_groups = self.grouped_data
        print(f"final result:\n {self.grouped_data}")

    def _init(self):
        ls = [_.shape[0] for _ in self._raw_data]
        self.grouped_data = np.array(
            [np.linspace(0, l, self.n_states + 1).astype(int) for l in ls]
        )
        self._calculate_slice_array()
        self._calculate_mean_variance()
        self._calculate_transition_matrix()

    def _update(self):
        alignment_result = []
        for i in range(self.n_samples):
            a = align_sequence(
                self._raw_data[i], self.means, self.variances, self.transition_matrix
            )
            # print(a)
            alignment_result.append(a)
        self.grouped_data = np.array(
            list(map(lambda x: self._state_list_2_grouped_data(x), alignment_result))
        )
        self._calculate_slice_array()
        self._calculate_mean_variance()
        self._calculate_transition_matrix()

    def _state_list_2_grouped_data(self, a):
        prev = a[0]
        r = [prev]
        for id, i in enumerate(a):
            if prev != i:
                r.append(id)
            prev = i
        r.append(len(a))
        return r

    def _calculate_slice_array(self):
        self.slice_array = np.array(
            [
                list(map(lambda x: slice(*x), zip(group, group[1:])))
                for group in self.grouped_data
            ]
        )

    def _calculate_mean_variance(self):
        self.means = []
        self.variances = []

        for state in range(self.n_states):
            state_slices = self.slice_array[:, state]
            state_data = [d[s] for s, d in zip(state_slices, self._raw_data)]
            flat_state_data = np.concatenate(state_data)
            avg = np.average(flat_state_data, axis=0)
            var = np.cov(flat_state_data.T)
            var_diag = np.diag(np.diag(var + 0.1))
            self.means.append(avg)
            self.variances.append(var_diag)

    def _calculate_transition_matrix(self):
        for i in range(self.n_states):
            total = sum([s.stop - s.start for s in self.slice_array[:, i]])
            self.transition_matrix[i, i] = (total - self.n_samples) / total
            if i + 1 < self.n_states:
                self.transition_matrix[i, i + 1] = self.n_samples / total

    def predict():
        pass


def boosted_mfcc_from_file(
    file_name: str, n_filter_banks=40, n_mfcc_coefficients=N_MFCC_COEFFICIENTS
):
    """Get the boosted MFCC features from `file_name`. Each column should have
    `n_mfcc_coefficients` × 3 values."""
    audio_array = read_audio_file(file_name)
    cepstra, _ = mfcc_homebrew(audio_array, n_filter_banks, n_mfcc_coefficients)
    return derive_cepstrum_velocities(cepstra)
