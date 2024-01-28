from abc import ABC
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

INF_FLOAT32 = np.float32(np.inf)


class NodeCostFn(ABC):
    """Returns node cost given input frame and template frame index."""

    def __call__(
        self, input_frame: NDArray[np.float32], template_frame_index: int
    ) -> np.float32:
        raise NotImplementedError(input_frame, template_frame_index)


class DTWEnuclideanNodeCostFn(NodeCostFn):
    def __init__(self, template: NDArray[np.float32]):
        self.template = template

    def __call__(
        self, input_frame: NDArray[np.float32], template_frame_index: int
    ) -> np.float32:
        return euclidean_distance(input_frame, self.template[template_frame_index])


@dataclass
class DTWCosts:
    """Growable costs matrix for dynamic time warping."""

    template_len: int
    node_cost: NodeCostFn
    cost_columns: list[NDArray[np.float32]] = []
    least_cost: np.float32 = INF_FLOAT32  # TODO: Beam Search.

    def __init__(self, template_len: int, node_cost: NodeCostFn):
        self.template_len = template_len
        self.node_cost = node_cost

    def empty_column(self) -> NDArray[np.float32]:
        return np.full(
            shape=self.template_len, fill_value=INF_FLOAT32, dtype=np.float32
        )

    def add_input(self, input_frame: NDArray[np.float32]) -> np.float32 | None:
        """Add an input frame and return the total cost if the end of the
        template is reached."""
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
