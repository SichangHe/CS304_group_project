import numpy as np
from numpy.typing import NDArray
from scipy.stats import multivariate_normal
from sklearn.cluster import KMeans

from ..project2 import read_audio_file
from ..project2.lib import (
    N_MFCC_COEFFICIENTS,
    derive_cepstrum_velocities,
    mfcc_homebrew,
)

TEST_INDEXES = range(1, 10, 2)
"""Indexes for test numbers."""

INF_FLOAT32 = np.float32(np.inf)


def align_sequence(sequence, means, covariances, transition_probs):
    num_states = len(means)
    sequence_length = len(sequence)

    viterbi_trellis = np.full((num_states, sequence_length), -np.inf)
    backpointers = np.zeros((num_states, sequence_length), dtype=int)

    # start from first state
    np.seterr(divide="ignore")
    viterbi_trellis[0, 0] = np.log(
        sum(
            [
                multivariate_normal.pdf(
                    sequence[0], mean=mean, cov=cov, allow_singular=True
                )
                for mean, cov in zip(means[0], covariances[0])
            ]
        )
    )

    for t in range(1, sequence_length):
        for state in range(num_states):
            emission_prob = sum(
                [
                    multivariate_normal.pdf(
                        sequence[t], mean=mean, cov=cov, allow_singular=True
                    )
                    for mean, cov in zip(means[state], covariances[state])
                ]
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
        self.n_gaussians = 1
        self.max_gaussians = 5

    def fit(self, data: list[NDArray[np.float32]], n_states=5, n_gaussians=5):
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
        self.max_gaussians = n_gaussians
        self._init()
        print(f"initial group:\n {self.grouped_data}")
        MAX_ITERS = 50
        prev_groups = None
        for _ in range(MAX_ITERS):
            self._update()
            print(self.n_gaussians)
            if prev_groups is not None and np.all(prev_groups == self.grouped_data):
                if self.n_gaussians == self.max_gaussians:
                    print("coverges")
                    break
                self.n_gaussians += 1
            prev_groups = self.grouped_data
        print(f"final result:\n {self.grouped_data}")

    def _init(self):
        ls = [_.shape[0] for _ in self._raw_data]
        self.grouped_data = np.array(
            [np.linspace(0, l, self.n_states + 1).astype(int) for l in ls]
        )

    def _update(self):
        self._calculate_slice_array()
        self._calculate_mean_variance()
        self._calculate_transition_matrix()
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
            kmeans = KMeans(n_clusters=self.n_gaussians)
            kmeans.fit(flat_state_data)
            groups = [
                [True if _ == i else False for _ in kmeans.labels_]
                for i in range(self.n_gaussians)
            ]
            ds = [flat_state_data[g] for g in groups]
            avg = [np.average(d, axis=0) for d in ds]
            var = [np.diag(np.diag(np.cov(d.T) + 0.1)) for d in ds]
            self.means.append(avg)
            self.variances.append(var)

    def _calculate_transition_matrix(self):
        for i in range(self.n_states):
            total = sum([s.stop - s.start for s in self.slice_array[:, i]])
            self.transition_matrix[i, i] = (total - self.n_samples) / total
            if i + 1 < self.n_states:
                self.transition_matrix[i, i + 1] = self.n_samples / total

    def predict():
        pass


def main():
    mean = np.array(
        [
            1,
            -2,
            3,
            0,
            2,
            -1,
            4,
            1,
            -3,
            2,
            -1,
            0,
            2,
            -2,
            3,
            -1,
            0,
            1,
            -2,
            0,
            2,
            1,
            -3,
            0,
            1,
            -2,
            3,
            -1,
            2,
            0,
            1,
            -2,
            3,
            0,
            2,
            -1,
            4,
            1,
            -3,
            2,
        ]
    )
    covariance = np.eye(40)
    num_samples = 200
    np.random.seed(0)
    samples = np.random.multivariate_normal(mean, covariance, num_samples)
    s = [samples[i : i + 40] for i in range(0, 161, 10)]
    dtw = HMM()
    dtw.fit(s, 5, 3)


main() if __name__ == "__main__" else None
