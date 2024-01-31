from logging import debug
from typing import Iterable

import numpy as np
from numpy.typing import NDArray

from .. import T
from . import INF_FLOAT32, NodeCostFn

BEST_PRUNING_THRESHOLD = 13.0


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


def time_sync_dtw_search(
    templates: Iterable[tuple[NDArray[np.float32], T]],
    input_frames: NDArray[np.float32],
    pruning_threshold=BEST_PRUNING_THRESHOLD,
) -> tuple[np.float32, T | None]:
    """Conduct time-synchronous dynamic time warping search on given `templates`
    and `input_frames`. Return the minimum cost found, and the corresponding
    prediction if the search is done."""
    costs_and_predictions = [
        (
            DTWCosts(len(template), DTWEnuclideanNodeCostFn(template=template)),
            prediction,
        )
        for template, prediction in templates
    ]
    pruned_list = [False for _ in templates]

    global_min_cost = INF_FLOAT32
    global_best_prediction = None

    for input_frame in input_frames:
        round_min_cost = INF_FLOAT32
        for index, ((costs, prediction), pruned) in enumerate(
            zip(costs_and_predictions, pruned_list)
        ):
            if pruned:
                continue

            if (
                total_cost := costs.add_input(input_frame)
            ) and total_cost < global_min_cost:
                global_min_cost = total_cost
                global_best_prediction = prediction
                debug(f"Got new best total cost {total_cost:.2f} for `{prediction}`.")
            round_min_cost = min(round_min_cost, costs.min_cost)

        past_round_threshold = round_min_cost + pruning_threshold
        for index, ((costs, prediction), pruned) in enumerate(
            zip(costs_and_predictions, pruned_list)
        ):
            if pruned:
                continue
            if costs.min_cost > past_round_threshold:
                pruned_list[index] = True
                debug(f"Pruned template {index} for `{prediction}`.")
            else:
                costs.prune(past_round_threshold)
    return global_min_cost, global_best_prediction


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
    min_cost: np.float32

    def __init__(self, template_len: int, node_cost: NodeCostFn):
        self.template_len = template_len
        self.node_cost = node_cost
        self.cost_columns = []
        self.min_cost = INF_FLOAT32  # TODO: Beam Search.

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
        min_cost = INF_FLOAT32
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
                min_cost = min(min_cost, current_cost)
        self.cost_columns.append(new_column)
        self.min_cost = min_cost

        return total_cost if (total_cost := new_column[-1]) < INF_FLOAT32 else None

    def prune(self, threshold: np.float32):
        """Prune values in the last costs column that are higher than
        `threshold`."""
        if len(self.cost_columns) == 0:
            return
        last_column = self.cost_columns[-1]
        last_column[last_column > threshold] = INF_FLOAT32


def euclidean_distance(x: NDArray[np.float32], y: NDArray[np.float32]) -> np.float32:
    return np.linalg.norm(x - y)
