"""Run with `python3 -m speech.project5.hmm`."""

import argparse
from dataclasses import dataclass
from itertools import groupby
from logging import debug

import numpy as np
from numpy.typing import NDArray
from scipy.stats import multivariate_normal  # type: ignore
from sklearn.cluster import KMeans  # type: ignore

from speech import DoubleArray, FloatArray
from speech.project2.main import NUMBERS
from speech.project3 import (
    HARD_TEMPLATE_INDEXES,
    HARD_TEST_INDEXES,
    INF_FLOAT32,
    TEMPLATE_INDEXES,
    TEST_INDEXES,
    boosted_mfcc_from_file,
)

MINUS_INF = -INF_FLOAT32


def multivariate_gaussian_negative_log_pdf_diag_cov(
    x: FloatArray, mean: FloatArray, cov: DoubleArray
):
    return -np.log(multivariate_gaussian_pdf_diag_cov(x, mean, cov))


def multivariate_gaussian_pdf_diag_cov(
    x: FloatArray, mean: FloatArray, cov: DoubleArray
) -> np.float64:
    """
    Compute the probability density function (PDF) of a multivariate Gaussian distribution with a diagonal covariance matrix.
    """
    n = x.shape[0]
    if len(cov.shape) == 2:
        cov = np.diag(cov)
    det_covariance = np.prod(cov)
    inv_covariance_matrix = np.diag(1 / cov)

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
                        multivariate_gaussian_pdf_diag_cov(
                            sequence[t], mean=mean, cov=cov
                        )
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


@dataclass
class HMMState:
    means: list[FloatArray]
    """n_gaussians of mean vectors. Also used for K-means iteration."""
    covariances: list[DoubleArray]
    """n_gaussians of diagonal of covariance matrix"""
    weights: list[float]
    transition_loss: dict["HMMState", float]
    """Negative log transition probability."""
    nth_state: int
    label: int | None
    """The digit associated with the state.
    `None` if the state is the first state."""
    exit_loss: float = 0.0
    """Negative log probability to exit the HMM, positive only if is last state
    of a digit."""
    parent: "HMMState | None" = None
    """The state is the first state if the `parent` is `None`."""

    def is_non_emiting(self):
        return len(self.means) == 0

    @classmethod
    def root(cls):
        return cls(
            means=[],
            covariances=[],
            weights=[],
            transition_loss={},
            nth_state=-1,
            label=None,
        )

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"HMMState{id(self)}(`{self.label}` with {len(self.means)} Gaussians)"


def clone_hmm_states(hmm_states: list[HMMState]):
    """Clone a series of HMMStates preserving their relationships."""
    state_map: dict[HMMState, HMMState] = {}
    new_states: list[HMMState] = []
    for state in hmm_states:
        new_state = HMMState(
            means=state.means,
            covariances=state.covariances,
            transition_loss=state.transition_loss,
            nth_state=state.nth_state,
            weights=state.weights,
            label=state.label,
            parent=state.parent,
        )
        state_map[state] = new_state
        new_states.append(new_state)

    for new_state in new_states:
        new_state.transition_loss = {
            state_map.get(state, state): prob
            for state, prob in new_state.transition_loss.items()
        }
        if new_state.parent is not None:
            new_state.parent = state_map.get(new_state.parent, new_state.parent)
    return new_states


def _align_sequence_round(
    sample: FloatArray | None,
    hmm_state: HMMState,
    round_min_loss: float,
    prev_losses: dict[HMMState, "LossNode"],
    current_losses: dict[HMMState, "LossNode"],
    beam_width: float,
):
    """Aligning non-emitting state if `sample` is `None`."""
    # Similar to `Trie._match_word_round`.
    min_loss = np.inf
    min_loss_node: LossNode | None = None

    for from_node, cost in hmm_state.transition_loss.items():
        if prev_loss_node := prev_losses.get(from_node):
            accumulated_loss = cost + prev_loss_node.loss
            if accumulated_loss < min_loss:
                min_loss = accumulated_loss
                min_loss_node = prev_loss_node

    if min_loss_node is not None and min_loss < round_min_loss + beam_width:
        if sample is None:
            combined_min_loss = min_loss
        else:
            # weighted gaussians
            assert (
                len(hmm_state.means)
                == len(hmm_state.covariances)
                == len(hmm_state.weights)
            )
            emission_loss = (
                min(
                    multivariate_gaussian_negative_log_pdf_diag_cov(
                        sample, mean=mean, cov=cov
                    )
                    - np.log(weight)
                    for mean, cov, weight in zip(
                        hmm_state.means, hmm_state.covariances, hmm_state.weights
                    )
                )
                if len(hmm_state.means) > 0
                else 0
            )
            combined_min_loss = min_loss + emission_loss

        if combined_min_loss < round_min_loss + beam_width:
            round_min_loss = min(round_min_loss, combined_min_loss)
            new_loss_node = min_loss_node.copying_update(
                state_node=hmm_state,
                loss=combined_min_loss,
                prev_end_loss_node=(
                    min_loss_node
                    if sample is None  # Non-emitting state
                    else min_loss_node.prev_end_loss_node
                ),
            )

            current_losses[hmm_state] = new_loss_node

    return round_min_loss


def _align_sequence_and_hmm_states(
    sequence: FloatArray,
    non_emitting_states: list[HMMState],
    emitting_states: list[HMMState],
    beam_width=1000.0,
):
    """Align a sequence against a sequence of HMM states.
    The first non-emitting state should be the beginning state."""
    np.seterr(divide="ignore")

    # Similar to `Trie._match_word`.
    prev_losses: dict[HMMState, LossNode] = {
        non_emitting_states[0]: LossNode(state_node=non_emitting_states[0])
    }

    for sample in sequence:
        intermediate_losses: dict[HMMState, LossNode] = {}
        round_min_loss = np.inf
        for state in non_emitting_states:
            round_min_loss = _align_sequence_round(
                None,
                state,
                round_min_loss,
                prev_losses,
                intermediate_losses,
                beam_width,
            )
        debug("intermediate_losses=%s", intermediate_losses)
        for state, intermediate_loss in intermediate_losses.items():
            if (
                prev_losses.get(state) is None  # beginning state
                or intermediate_loss.loss < prev_losses[state].loss
            ):
                prev_losses[state] = intermediate_loss

        current_losses: dict[HMMState, LossNode] = {}
        round_min_loss = np.inf
        for state in emitting_states:
            round_min_loss = _align_sequence_round(
                sample,
                state,
                round_min_loss,
                prev_losses,
                current_losses,
                beam_width,
            )
        debug("current_losses=%s", current_losses)

        round_threshold = round_min_loss + beam_width
        prev_losses = {
            node: loss_node
            for node, loss_node in current_losses.items()
            if loss_node.loss <= round_threshold
        }
        debug("Filtered previous_losses=%s", prev_losses)

    final_losses: dict[HMMState, LossNode] = {}
    for state in non_emitting_states:
        _ = _align_sequence_round(
            None,
            state,
            np.inf,
            prev_losses,
            final_losses,
            beam_width,
        )
    return prev_losses, final_losses


def match_sequence_against_hmm_states(
    sequence: FloatArray,
    non_emitting_states: list[HMMState],
    emitting_states: list[HMMState],
    beam_width=1000.0,
):
    """Match a sequence against a sequence of HMM states.
    The first non-emitting state should be the beginning state,
    and the last non-emitting state should be the end state."""
    _, last_losses = _align_sequence_and_hmm_states(
        sequence, non_emitting_states, emitting_states, beam_width
    )
    debug("last_losses=%s", last_losses)

    min_finished_loss_node = last_losses[non_emitting_states[-1]]
    return min_finished_loss_node.backtrack()


def align_sequence_train(
    sequence: FloatArray,
    hmm_states: list[HMMState],
):
    """align a sequence vs a hmm model"""
    sequence_length = len(sequence)

    np.seterr(divide="ignore")

    # initialize prev_losses with first state
    prev_losses: dict[HMMState, LossNode] = {
        hmm_states[0]: LossNode(
            state_node=hmm_states[0],
            prev_end_loss_node=None,
            loss=min(
                multivariate_gaussian_negative_log_pdf_diag_cov(
                    sequence[0], mean=mean, cov=cov
                )
                - np.log(weight)
                for mean, cov, weight in zip(
                    hmm_states[0].means,
                    hmm_states[0].covariances,
                    hmm_states[0].weights,
                )
            ),
        )
    }

    current_losses: dict[HMMState, LossNode] = {}
    for t in range(1, sequence_length):
        current_losses = {}
        for node in hmm_states:
            combined_losses: list[tuple[LossNode, float]] = []
            for k, v in node.transition_loss.items():
                if l := prev_losses.get(k):
                    combined_losses.append((l, v + l.loss))

            if len(combined_losses) > 0:
                emission_loss = min(
                    multivariate_gaussian_negative_log_pdf_diag_cov(
                        sequence[t], mean=mean, cov=cov
                    )
                    - np.log(weight)
                    for mean, cov, weight in zip(
                        node.means, node.covariances, node.weights
                    )
                )
                best_loss_node, min_loss = min(combined_losses, key=lambda x: x[1])
                current_losses.update(
                    {
                        node: LossNode(
                            state_node=node,
                            prev_end_loss_node=best_loss_node,
                            loss=min_loss + emission_loss,
                        )
                    }
                )

        prev_losses = current_losses

    # backtrack
    prev_loss = list(current_losses.values())[-1]
    alignment = [prev_loss.state_node.nth_state]
    while maybe_prev := prev_loss.prev_end_loss_node:
        prev_loss = maybe_prev
        alignment.append(prev_loss.state_node.nth_state)

    alignment.reverse()

    return alignment, list(current_losses.values())[-1].loss


def align_sequence_cont_train(
    sequence: FloatArray, hmm_states: list[HMMState], beam_width=2000.0
):
    """align a sequence vs a hmm model"""
    sequence_length = len(sequence)

    np.seterr(divide="ignore")

    # initialize prev_losses with silence state
    prev_losses: dict[HMMState, LossNode] = {
        hmm_states[0]: LossNode(
            state_node=hmm_states[0],
            prev_end_loss_node=None,
            loss=min(
                multivariate_gaussian_negative_log_pdf_diag_cov(
                    sequence[0], mean=mean, cov=cov
                )
                - np.log(weight)
                for mean, cov, weight in zip(
                    hmm_states[0].means,
                    hmm_states[0].covariances,
                    hmm_states[0].weights,
                )
            ),
        )
    }

    current_losses: dict[HMMState, LossNode] = {}
    for t in range(1, sequence_length):
        current_losses = {}
        round_min_loss = np.inf
        for node in hmm_states:
            combined_losses: list[tuple[LossNode, float]] = []
            for k, v in node.transition_loss.items():
                if l := prev_losses.get(k):
                    combined_losses.append((l, v + l.loss))
            if len(combined_losses) > 0:
                emission_loss = min(
                    multivariate_gaussian_negative_log_pdf_diag_cov(
                        sequence[t], mean=mean, cov=cov
                    )
                    - np.log(weight)
                    for mean, cov, weight in zip(
                        node.means, node.covariances, node.weights
                    )
                )

                if emission_loss == np.inf:
                    continue

                best_loss_node, min_loss = min(combined_losses, key=lambda x: x[1])
                potential_loss = min_loss + emission_loss
                round_min_loss = min(round_min_loss, potential_loss)
                current_losses = {
                    k: v
                    for k, v in current_losses.items()
                    if v.loss < round_min_loss + beam_width
                }
                if potential_loss < round_min_loss + beam_width:
                    current_losses.update(
                        {
                            node: LossNode(
                                state_node=node,
                                prev_end_loss_node=best_loss_node,
                                loss=potential_loss,
                            )
                        }
                    )

        prev_losses = current_losses

    prev_loss = current_losses[hmm_states[-1]]
    alignment = [(prev_loss.state_node.label, prev_loss.state_node.nth_state)]
    while maybe_prev := prev_loss.prev_end_loss_node:
        prev_loss = maybe_prev
        alignment.append((prev_loss.state_node.label, prev_loss.state_node.nth_state))

    alignment.reverse()

    indiced_alignment = list(enumerate(alignment))
    indiced_alignment.sort(key=lambda x: x[1][0])
    grouped_indiced_alignment = {
        digit: list([(g[0], g[1][1]) for g in group])
        for digit, group in groupby(indiced_alignment, lambda x: x[1][0])
    }
    sequence_dict: dict[int, FloatArray] = {
        k: np.stack([sequence[g[0]] for g in v])
        for k, v in grouped_indiced_alignment.items()
        if k != -1
    }

    alignment_dict: dict[int, FloatArray] = {
        k: np.stack([g[0] for g in v])
        for k, v in grouped_indiced_alignment.items()
        if k != -1
    }

    alignment_slice = {k: (v[0], v[-1]) for k, v in alignment_dict.items()}

    return sequence_dict, alignment_slice, current_losses[hmm_states[-1]].loss


@dataclass
class LossNode:
    state_node: HMMState
    prev_end_loss_node: "LossNode | None" = None
    loss: float = 0.0

    def copying_update(
        self,
        state_node: HMMState | None = None,
        prev_end_loss_node: "LossNode | None" = None,
        loss: float | None = None,
    ):
        if state_node is None:
            state_node = self.state_node
        if prev_end_loss_node is None:
            prev_end_loss_node = self.prev_end_loss_node
        if loss is None:
            loss = self.loss

        return LossNode(state_node, prev_end_loss_node, loss)

    def backtrack(self) -> list[int]:
        reversed_words = []
        current: "LossNode | None" = self
        while current is not None:
            word = current.state_node.label
            if word is not None:
                reversed_words.append(word)
            current = current.prev_end_loss_node
        return list(reversed(reversed_words))

    def __repr__(self) -> str:
        prev_end_loss_node = (
            self.prev_end_loss_node.state_node if self.prev_end_loss_node else None
        )
        return f"LossNode({self.state_node}, prev_end_loss_node={prev_end_loss_node} loss={self.loss:.2f})"


class HMM_Single:
    n_states: int
    transition_matrix: NDArray[np.float64]
    label: int
    states: list[HMMState]
    
    _raw_data: list[FloatArray]
    _grouped_data: NDArray[np.int64]
    _slice_array: NDArray

    def __init__(
        self,
        label: int,
        data: list[FloatArray],
        n_states=5,
        n_gaussians=4,
    ):
        """
        Fits the model to the provided training data using segmental K-means.

        Parameters:
        data: The training data.
            It should have the shape (N, l) or (N, l, d), where N is the number of training samples
            and l is the length of each training sample.
            Each training sample can be a scalar or a vector.
        """
        self.label = label
        self._raw_data = data
        self.n_states = n_states
        self.n_samples = len(data)
        self.transition_matrix = np.zeros((self.n_states, self.n_states))
        self.states = []
        parent = None
        for s in range(self.n_states):
            state = HMMState(
                parent=parent,
                means=[],
                covariances=[],
                weights=[],
                transition_loss={},
                nth_state=s,
                exit_loss=0,
                label=self.label,
            )
            parent = state
            self.states.append(state)

        self._init()

        prev_groups = None
        current_n_gaussians = 1
        while current_n_gaussians <= n_gaussians:
            self._update(current_n_gaussians)
            if prev_groups is not None and np.all(prev_groups == self._grouped_data):
                # Converge.
                current_n_gaussians *= 2
            prev_groups = self._grouped_data

    def _init(self):
        ls = [_.shape[0] for _ in self._raw_data]
        self._grouped_data = np.array(
            [np.linspace(0, l, self.n_states + 1).astype(int) for l in ls]
        )

    def _update(self, n_gaussians: int):
        self._calculate_slice_array()
        self._calculate_mean_variance(n_gaussians)
        self._calculate_transition_matrix()

        # transition loss
        for s in range(self.n_states):
            self.states[s].transition_loss = {
                self.states[i]: -np.log(v)
                for i, v in enumerate(self.transition_matrix[:, s])
                if v > 0
            }
        # exit prob
        self.states[-1].exit_loss = -np.log(1 - np.sum(self.transition_matrix[-1]))

        alignment_result = []
        for i in range(self.n_samples):
            a, _ = align_sequence_train(self._raw_data[i], self.states)
            alignment_result.append(a)
        self._grouped_data = np.array(
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
        self._slice_array = np.asarray(
            [
                list(map(lambda x: slice(*x), zip(group, group[1:])))
                for group in self._grouped_data
            ],
        )

    def _calculate_mean_variance(self, n_gaussians: int):
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
                prev_means_for_state = np.asarray(self.states[state].means)
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
            labels: NDArray[np.int32] | None = kmeans.labels_
            assert labels is not None
            groups = [
                [True if _ == i else False for _ in labels] for i in range(n_gaussians)
            ]
            weights = [
                list(labels).count(elem) / len(labels) for elem in range(n_gaussians)
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

            self.states[state].means = avg
            self.states[state].covariances = var
            self.states[state].weights = weights

    def _calculate_transition_matrix(self):
        for i in range(self.n_states):
            total = sum([s.stop - s.start for s in self._slice_array[:, i]])
            self.transition_matrix[i, i] = (total - self.n_samples) / total
            if i + 1 < self.n_states:
                self.transition_matrix[i, i + 1] = self.n_samples / total

    def predict_score(self, target: FloatArray):
        """
        Take a target sequence and return similarity with the training samples.
        """
        return align_sequence_train(target, self.states)


def single_hmm_w_template_file_names(
    label: int,
    template_file_names: list[str],
    n_states: int,
    n_gaussians: int,
):
    template_mfcc_s = [
        boosted_mfcc_from_file(file_name) for file_name in template_file_names
    ]
    return HMM_Single(label, template_mfcc_s, n_states, n_gaussians)


class HMM:

    def __init__(
        self,
        n_states=5,
        n_gaussians=4,
        hmm_instances: list[HMM_Single] = [],
    ):
        self.n_states = n_states
        self.n_gaussians = n_gaussians
        self._hmm_instances = hmm_instances

    def fit(
        self,
        templates_for_each_label: list[list[FloatArray]],
        labels: list[int],
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

        for templates, label in zip(templates_for_each_label, labels):
            debug("Calculating single HMM for number `%s`.", label)
            hmm = HMM_Single(label, templates, self.n_states, self.n_gaussians)
            self._hmm_instances.append(hmm)

    def predict(self, test_samples_list: list[FloatArray]):
        result = [self._predict(samples) for samples in test_samples_list]

        return result

    def _predict(self, samples: FloatArray):
        losses = [
            (hmm.predict_score(samples)[1], hmm.label) for hmm in self._hmm_instances
        ]

        # TODO: Doublecheck.
        return min(losses, key=lambda x: x[0])[1]

    @classmethod
    def from_template_file_names_and_labels(
        cls,
        template_file_names_for_each_label: list[list[str]],
        labels: list[int],
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
                label, template_file_names, n_states, n_gaussians
            )
            hmm_instances.append(hmm_single)
        return cls(
            n_states=n_states,
            n_gaussians=n_gaussians,
            hmm_instances=hmm_instances,
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
