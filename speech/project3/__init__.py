from abc import ABC

import numpy as np
from numpy.typing import NDArray

from ..project2 import read_audio_file
from ..project2.lib import (
    N_MFCC_COEFFICIENTS,
    derive_cepstrum_velocities,
    mfcc_homebrew,
)

INF_FLOAT32 = np.float32(np.inf)


def single_dtw_search(
    template: NDArray[np.float32], input_frames: NDArray[np.float32]
) -> list[np.float32]:
    """Conduct a single dynamic time warping search on given `template` and
    `input_frames`. Return the total cost if the search is done."""
    node_cost_fn = DTWEnuclideanNodeCostFn(template=template)
    costs = DTWCosts(len(template), node_cost_fn)
    finish_costs = []
    for input_frame in input_frames:
        if total_cost := costs.add_input(input_frame):
            finish_costs.append(total_cost)
    return finish_costs


class NodeCostFn(ABC):
    """Returns node cost given input frame and template frame index."""

    def __call__(
        self, input_frame: NDArray[np.float32], template_frame_index: int
    ) -> np.float32:
        raise NotImplementedError(input_frame, template_frame_index)


class DTWEnuclideanNodeCostFn(NodeCostFn):
    def __init__(self, template: NDArray[np.float32]):
        self.template = template
        self.template_len = len(template)

    def __call__(
        self, input_frame: NDArray[np.float32], template_frame_index: int
    ) -> np.float32:
        distance = euclidean_distance(input_frame, self.template[template_frame_index])
        return distance / self.template_len


class DTWCosts:
    """Growable costs matrix for dynamic time warping."""

    template_len: int
    node_cost: NodeCostFn
    cost_columns: list[NDArray[np.float32]]
    least_cost: np.float32

    def __init__(self, template_len: int, node_cost: NodeCostFn):
        self.template_len = template_len
        self.node_cost = node_cost
        self.cost_columns = []
        self.least_cost = INF_FLOAT32  # TODO: Beam Search.

    def empty_column(self) -> NDArray[np.float32]:
        return np.full(
            shape=self.template_len, fill_value=INF_FLOAT32, dtype=np.float32
        )

    def add_input(self, input_frame: NDArray[np.float32]) -> np.float32 | None:
        """Add an input frame and return the total cost if the end of the
        template is reached."""
        assert len(input_frame) == 39, input_frame.shape
        if len(self.cost_columns) == 0:  # First input frame.
            first_column = self.empty_column()
            first_cost = self.node_cost(input_frame, 0)
            first_column[0] = first_cost
            self.cost_columns.append(first_column)
            return None

        last_column = self.cost_columns[-1]
        r"""P_{\_, j-1}"""

        new_column = self.empty_column()
        least_cost = INF_FLOAT32
        for template_index in range(self.template_len):
            safe_template_index_lower = max(template_index - 2, 0)
            min_prev_cost = np.min(
                last_column[safe_template_index_lower : template_index + 1]
            )
            r"""\min(P_{i-2, j-1}, P_{i-1, j-1}, P_{i, j-1})"""

            if min_prev_cost < INF_FLOAT32:
                current_node_cost = self.node_cost(input_frame, template_index)
                """C_{i,j}"""
                current_cost = min_prev_cost + current_node_cost
                new_column[template_index] = current_cost
                least_cost = min(least_cost, current_cost)
        self.cost_columns.append(new_column)
        self.least_cost = least_cost

        return total_cost if (total_cost := new_column[-1]) < INF_FLOAT32 else None


def euclidean_distance(x: NDArray[np.float32], y: NDArray[np.float32]) -> np.float32:
    return np.linalg.norm(x - y)


class HMM:
    def __init__(self):
        self.means = np.array([])
        self.variances = []
        self.n_states = 0

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
        self._init()

    def _init(self):
        self._raw_data = self._raw_data
        ls = [_.shape[0] for _ in self._raw_data]
        self.grouped_data = [
            np.linspace(0, l, self.n_states + 1).astype(int) for l in ls
        ]
        self._calculate_mean_variance()

    def _update(self):
        for i in range(self.n_samples):
            # TODO: alignment
            pass
        pass

    def _calculate_mean_variance(self):
        slice_array = np.array(
            [
                list(map(lambda x: slice(*x), zip(group, group[1:])))
                for group in self.grouped_data
            ]
        )

        for state in range(self.n_states):
            state_slices = slice_array[:, state]
            state_data = [d[s] for s, d in zip(state_slices, self._raw_data)]
            flat_state_data = np.concatenate(state_data)
            avg = np.average(flat_state_data)
            var = np.cov(flat_state_data.T)
            self.means = np.append(self.means, avg)
            self.variances.append(var)

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
