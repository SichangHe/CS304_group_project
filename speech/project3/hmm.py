"""Run with `python3 -m speech.project3.hmm`."""

import argparse
from logging import debug
from typing import Iterable, List, Tuple

import numpy as np

from cache_to_disk import cache_to_disk
from numpy.typing import NDArray
from scipy.stats import multivariate_normal
from sklearn.cluster import KMeans

from ..project2.main import NUMBERS
from . import (
    HARD_TEMPLATE_INDEXES,
    HARD_TEST_INDEXES,
    INF_FLOAT32,
    TEMPLATE_INDEXES,
    TEST_INDEXES,
    boosted_mfcc_from_file,
)

MINUS_INF = -INF_FLOAT32


def multivariate_gaussian_pdf_diag_cov(
    x: NDArray[np.float64], mean: NDArray[np.float64], cov: NDArray[np.float64]
) -> np.float64:
    """
    Compute the probability density function (PDF) of a multivariate Gaussian distribution with a diagonal covariance matrix.
    """
    n = x.shape[0]
    variance = np.diag(cov)
    det_covariance = np.prod(variance)
    inv_covariance_matrix = np.diag(1 / variance)

    difference_vector = x - mean
    exponent = np.dot(
        np.dot(difference_vector, inv_covariance_matrix), difference_vector
    )

    normalization = (2 * np.pi) ** (n / 2) * np.sqrt(det_covariance)

    pdf = 1 / normalization * np.exp(-0.5 * exponent)

    return pdf


def align_sequence(sequence, means, covariances, transition_probs):
    num_states = len(means)
    sequence_length = len(sequence)

    viterbi_trellis = np.full((num_states, sequence_length), MINUS_INF)
    backpointers = np.zeros((num_states, sequence_length), dtype=int)

    np.seterr(divide="ignore")

    # wait until positive probability
    start_index = -1
    while True:
        start_index += 1

        if start_index > 5:
            return [0] * len(sequence), MINUS_INF

        log_probabilities = (
            multivariate_normal.logpdf(
                sequence[start_index], mean=mean, cov=cov, allow_singular=True
            )
            for mean, cov in zip(means[0], covariances[0])
        )
        viterbi_trellis[0, start_index] = max(log_probabilities)

        if viterbi_trellis[0, start_index] != MINUS_INF:
            break

    for t in range(start_index + 1, sequence_length):
        for state in range(num_states):
            last_viterbi_trellis = viterbi_trellis[:, t - 1]
            log_transition_prob = np.log(transition_probs[:, state])
            if all(
                np.logical_or(
                    last_viterbi_trellis == MINUS_INF,
                    log_transition_prob == MINUS_INF,
                )
            ):
                """last_viterbi_trellis or log_transition_prob is -inf"""
                viterbi_trellis[state, t] = MINUS_INF
            else:
                emission_log_prob = np.log(
                    max(
                        multivariate_gaussian_pdf_diag_cov(sequence[t], mean=mean, cov=cov)
                        for mean, cov in zip(means[state], covariances[state])
                    )
                )
                viterbi_scores = (
                    last_viterbi_trellis + log_transition_prob + emission_log_prob
                )

                viterbi_trellis[state, t] = np.max(viterbi_scores)
                backpointers[state, t] = np.argmax(viterbi_scores)

    # Trace back
    # alignment = [np.argmax(viterbi_trellis[:, -1])]
    # start from last state, not highest score state
    path = [num_states - 1]
    for t in range(sequence_length - 1, 0, -1):
        path.append(backpointers[path[-1], t])

    path.reverse()
    return path, viterbi_trellis[-1, -1]


class HMM_Single:
    n_states: int
    transition_matrix: NDArray[np.float64]
    grouped_data: NDArray[np.int64]
    _raw_data: List[NDArray[np.float32]]
    _slice_array: NDArray

    def __init__(self, data: List[NDArray[np.float32]], n_states=5, n_gaussians=4):
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

        self.means: list[list[NDArray[np.float32]]] = []
        self._init()

        prev_groups = None
        current_n_gaussians = 1
        while current_n_gaussians <= n_gaussians:
            self._update(current_n_gaussians)
            if prev_groups is not None and np.all(prev_groups == self.grouped_data):
                # Converge.
                current_n_gaussians *= 2
            prev_groups = self.grouped_data

    def _init(self):
        ls = [_.shape[0] for _ in self._raw_data]
        self.grouped_data = np.array(
            [np.linspace(0, l, self.n_states + 1).astype(int) for l in ls]
        )

    def _update(self, n_gaussians: int):
        self._calculate_slice_array()
        self._calculate_mean_variance(n_gaussians)
        self._calculate_transition_matrix()
        alignment_result = []
        for i in range(self.n_samples):
            a, _ = align_sequence(
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
        self._slice_array = np.array(
            [
                list(map(lambda x: slice(*x), zip(group, group[1:])))
                for group in self.grouped_data
            ]
        )

    def _calculate_mean_variance(self, n_gaussians: int):
        prev_means = self.means

        self.means = []  # [(39,); n_gaussian; n_state]
        self.variances = []

        for state in range(self.n_states):
            state_slices = self._slice_array[:, state]
            state_data = [d[s] for s, d in zip(state_slices, self._raw_data)]
            flat_state_data = np.concatenate(state_data)  # (n, 39)
            if n_gaussians < 2:
                # First K-means iteration
                new_means = np.mean(flat_state_data, axis=0)
                assert new_means.shape == (39,)
                new_means = new_means[np.newaxis, :]
                assert new_means.shape == (1, 39)
            else:
                prev_means_for_state = np.asarray(prev_means[state])
                if prev_means_for_state.shape[0] == n_gaussians:
                    # Last iteration with the same `n_gaussians` did not converge
                    new_means = prev_means_for_state
                else:
                    # New iteration with double the `n_gaussians`
                    assert prev_means_for_state.shape == (
                        n_gaussians / 2,
                        39,
                    ), (n_gaussians, prev_means_for_state.shape)
                    new_means = np.vstack(
                        (prev_means_for_state * 0.9, prev_means_for_state * 1.1)
                    )
            assert new_means.shape == (n_gaussians, 39), new_means.shape
            kmeans = KMeans(n_clusters=n_gaussians, init=new_means)  # type: ignore
            kmeans = kmeans.fit(flat_state_data)
            labels: Iterable[int] | None = kmeans.labels_
            assert labels is not None
            groups = [
                [True if _ == i else False for _ in labels] for i in range(n_gaussians)
            ]
            grouped_flat_state_data = [
                flat_state_data[g] for g in groups
            ]  # [(n, 39); n_g]
            avg = [
                np.average(d, axis=0) for d in grouped_flat_state_data
            ]  # [(39,); n_g]
            var = [
                (
                    np.diag(np.diag(np.cov(d.T) + 0.1))
                    # careful when a state only has one associated frame
                    if d.shape[0] != 1
                    else np.eye(d.shape[1])
                )
                for d in grouped_flat_state_data
            ]
            self.means.append(avg)
            self.variances.append(var)

    def _calculate_transition_matrix(self):
        for i in range(self.n_states):
            total = sum([s.stop - s.start for s in self._slice_array[:, i]])
            self.transition_matrix[i, i] = (total - self.n_samples) / total
            if i + 1 < self.n_states:
                self.transition_matrix[i, i + 1] = self.n_samples / total

    def predict_score(
        self, target: NDArray[np.float32]
    ) -> Tuple[List[int], np.float32]:
        """
        Take a target sequence and return similarity with the training samples.
        """
        return align_sequence(
            target, self.means, self.variances, self.transition_matrix
        )


@cache_to_disk(2)
def single_hmm_w_template_file_names(
    template_file_names: list[str], n_states: int, n_gaussians: int
):
    template_mfcc_s = [
        boosted_mfcc_from_file(file_name) for file_name in template_file_names
    ]
    return HMM_Single(template_mfcc_s, n_states, n_gaussians)


class HMM:
    labels: List[int]

    def __init__(
        self,
        n_states=5,
        n_gaussians=4,
        hmm_instances: List[HMM_Single] = [],
        labels: list[int] = [],
    ):
        self.n_states = n_states
        self.n_gaussians = n_gaussians
        self._hmm_instances = hmm_instances
        self.labels = labels

    def fit(
        self,
        templates_for_each_label: list[list[NDArray[np.float32]]],
        labels: List[int],
    ):
        """
        Fits the model to the given training data using segmental K-means.

        Parameters
        ----------
        templates_for_each_label : A list of training samples with length `n_samples`, where each sample is represented as a list of numpy arrays.
            The outer list contains different training samples, each corresponding to a target number (e.g., 1, 2, 3).
            The inner list represents the number of samples in each target.
            Each numpy array is the training data and has a shape of `(l, d)`, where `l` is the number of frames and `d` is the dimension of features (typically 39).

        labels : array-like of shape `(n_samples,)`
            Target vector relative to X.
        """
        assert len(templates_for_each_label) == len(labels)
        self.labels = labels

        for templates, label in zip(templates_for_each_label, labels):
            debug(f"Calculating single HMM for number {label}.")
            hmm = HMM_Single(templates, self.n_states, self.n_gaussians)
            self._hmm_instances.append(hmm)

    def predict(self, test_samples_list: list[NDArray[np.float32]]):
        result = [self._predict(samples) for samples in test_samples_list]

        return result

    def _predict(self, samples: NDArray[np.float32]):
        scores = [
            (hmm.predict_score(samples)[1], l)
            for hmm, l in zip(self._hmm_instances, self.labels)
        ]

        return max(scores, key=lambda x: x[0])[1]

    @classmethod
    def from_template_file_names_and_labels(
        cls,
        template_file_names_for_each_label: list[list[str]],
        labels: List[int],
        n_states=5,
        n_gaussians=4,
    ):
        assert len(template_file_names_for_each_label) == len(labels)
        hmm_instances = []
        for template_file_names, label in zip(
            template_file_names_for_each_label, labels
        ):
            debug(f"Calculating single HMM for number {label}.")
            hmm_single = single_hmm_w_template_file_names(
                template_file_names, n_states, n_gaussians
            )
            hmm_instances.append(hmm_single)
        return cls(
            n_states=n_states,
            n_gaussians=n_gaussians,
            hmm_instances=hmm_instances,
            labels=labels,
        )


def main():
    parser = argparse.ArgumentParser(description="HMM")
    parser.add_argument(
        "-m", "--hard-mode", action="store_true", help="Use hard mode datasets."
    )
    parser.add_argument(
        "-n",
        "--n-gaussians",
        default=4,
        type=int,
        help="Number of gaussians for each state.",
    )
    args = parser.parse_args()
    template_indexes, test_indexes = (
        (HARD_TEMPLATE_INDEXES, HARD_TEST_INDEXES)
        if args.hard_mode
        else (TEMPLATE_INDEXES, TEST_INDEXES)
    )

    template_files = [
        [f"recordings/{number}{i}.wav" for i in template_indexes] for number in NUMBERS
    ]
    test_mfcc_s = [
        [boosted_mfcc_from_file(f"recordings/{number}{i}.wav") for i in test_indexes]
        for number in NUMBERS
    ]

    hmm = HMM.from_template_file_names_and_labels(
        template_files, list(range(11)), n_states=5, n_gaussians=args.n_gaussians
    )

    result = []
    for i, _ in enumerate(test_mfcc_s[0:11]):
        print(f"calculating probabilities for number {i}")
        result.append(hmm.predict(_))

    print(f"prediction: {result}")
    target = [[i] * 5 for i in range(11)]
    accuracy = [
        sum(1 for elem1, elem2 in zip(r, t) if elem1 == elem2) / len(r)
        for r, t in zip(result, target)
    ]
    print(f"accuracy: {accuracy}")


main() if __name__ == "__main__" else None
