from abc import ABC
from logging import debug

import numpy as np
from cache_to_disk import cache_to_disk
from numpy.typing import NDArray

from speech.project2 import read_audio_file
from speech.project2.lib import (
    N_MFCC_COEFFICIENTS,
    derive_cepstrum_velocities,
    mfcc_homebrew,
)

TEST_INDEXES = range(11, 20, 2)
"""Indexes for test numbers."""

TEMPLATE_INDEXES = range(10, 20, 2)
"""Indexes for template numbers."""

HARD_TEST_INDEXES = range(1, 10, 2)
"""Indexes for hard mode test numbers."""

HARD_TEMPLATE_INDEXES = range(0, 10, 2)
"""Indexes for hard mode template numbers."""

DEMO_TEMPLATE_INDEXES = range(10)

INF_FLOAT32 = np.float32(np.inf)


class NodeCostFn(ABC):
    """Returns node cost given input frame and template frame index."""

    def __call__(
        self, input_frame: NDArray[np.float32], template_frame_index: int
    ) -> np.float32:
        raise NotImplementedError(input_frame, template_frame_index)


@cache_to_disk(30)
def boosted_mfcc_from_file(
    file_name: str, n_filter_banks=40, n_mfcc_coefficients=N_MFCC_COEFFICIENTS
):
    """Get the boosted MFCC features from `file_name`. Each column should have
    `n_mfcc_coefficients` × 3 values."""
    debug(f"Calculating the boosted MFCC from audio file {file_name}.")
    audio_array = read_audio_file(file_name)
    cepstra, _ = mfcc_homebrew(audio_array, n_filter_banks, n_mfcc_coefficients)
    return derive_cepstrum_velocities(cepstra)
