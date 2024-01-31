from logging import debug
from queue import Queue
from threading import Thread

import numpy as np
from numpy.typing import NDArray

from . import CHUNK_MS, MAX_PAUSE_MS, MS_IN_SECOND, SAMPLING_RATE
from .audio_in import AudioIn

SIZEOF_FRAME = 2
"""Size of each frame in bytes."""
BACKTRACK_MS = 200
"""Duration in milliseconds to backtrack when speech starts."""
SIZE_OF_BACKTRACK = SAMPLING_RATE * BACKTRACK_MS // MS_IN_SECOND
"""Size of the buffer in bytes for backtracking when speech starts."""


class Endpointer:
    """Endpoint audio received from `audio_in` and write speech data to
    `write_queue` in a background thread until speech stops.
    Stopping condition: `MAX_PAUSE_MS` ms after speech stops."""

    def __init__(
        self, audio_in: AudioIn, write_queue: Queue[bytes | None], timeout=0.1
    ):
        self.audio_in = audio_in
        self.write_queue = write_queue
        self.timeout = timeout
        self.classify_sample = get_classify_sample()
        self.off_time = 0
        self.started = False
        self.paused = False
        self.pending_samples = b""
        self.thread = Thread(target=self.write_all, args=())
        self.thread.start()

    def write_all(self):
        """Write all audio sample to `self.write_queue`."""
        try:
            while True:
                data, _ = self.audio_in.audio_queue.get(timeout=self.timeout)
                audio_array = np.frombuffer(data, dtype=np.int16)
                is_speech = self.classify_sample(audio_array)

                if not self.started:
                    if is_speech:
                        self.started = True
                        # Backtrack previous sample before recording starts.
                        self.write_queue.put(self.pending_samples[-SIZE_OF_BACKTRACK:])
                        self.pending_samples = b""
                        self.write_queue.put(data)
                    else:
                        self.pending_samples += data
                else:
                    if is_speech:
                        self.off_time = 0
                        if self.paused:
                            print("Writing samples received during pause.")
                            self.paused = False
                            # Backtrack previous sample during pause.
                            self.write_queue.put(self.pending_samples)
                            self.pending_samples = b""
                        self.write_queue.put(data)
                    else:
                        self.paused = True
                        self.off_time += CHUNK_MS
                        if self.off_time > MAX_PAUSE_MS:
                            break
                        self.pending_samples += data
        finally:
            self.write_queue.put(None)

    def __del__(self):
        self.thread.join(timeout=0)


FORGET_FACTOR = 1.2
"""Forgetting factor for updating `level` energy in `get_classify_sample`."""
STARTING_THRESHOLD_DB = 15.0
"""Threshold from background in decibels for starting to classify as speeches."""
CONTINUING_THRESHOLD_DB = 2.0
"""Threshold from background in decibels for continuing to classify as speeches."""
STOPPING_THRESHOLD_DB = -20.0
"""Threshold from foreground in decibels for stopping to classify as speeches."""
WEAK_ADJUSTMENT = 0.05
STRONG_ADJUSTMENT = 0.8


def get_classify_sample():
    """Get a closure that classifies whether each sample is speech.
    Speech is considered to start when the `level` energy is at least
    `STARTING_THRESHOLD_DB` higher than `background` energy;
    speech is considered to continue when the `level` energy is
    at least `CONTINUING_THRESHOLD_DB` higher than `background` energy and
    at least `STOPPING_THRESHOLD_DB` higher than `foreground` energy."""
    level: np.float64 | None = None
    background: np.float64 | None = None
    foreground = 0.0
    speaking = False

    def classify_frame(arr: NDArray[np.int16]) -> bool:
        nonlocal level, background, foreground, speaking
        current = sample_decibel_energy(arr)
        if level is None:
            level = current
        if background is None:
            background = current

        level = ((level * FORGET_FACTOR) + current) / (FORGET_FACTOR + 1.0)

        debug(
            f"speaking: {'Y' if speaking else 'N'}, current: {current:.1f}, bg: {background:.1f}, fg: {foreground:.1f}, level: {level:.1f}."
        )

        if speaking:
            if (
                level - background < CONTINUING_THRESHOLD_DB
                or level - foreground < STOPPING_THRESHOLD_DB
            ):
                speaking = False
                background = background if background < level else level
            else:
                foreground = adjust_conditionally_on_change(
                    foreground, level, STRONG_ADJUSTMENT, WEAK_ADJUSTMENT
                )
        if not speaking:
            if level - background >= STARTING_THRESHOLD_DB:
                speaking = True
                foreground = level
            else:
                background = adjust_conditionally_on_change(
                    background, level, WEAK_ADJUSTMENT, STRONG_ADJUSTMENT
                )

        return speaking

    return classify_frame


def sample_decibel_energy(arr: NDArray[np.int16]) -> np.float64:
    """Calculate the energy of an audio sample in decibel."""
    arr = arr.astype(np.int64)  # avoid overflow
    power = arr.dot(arr) / arr.size
    return np.log10(power) * 10.0


def adjust_conditionally_on_change(
    original, updated, adjustment_if_inc, adjustment_if_dec
):
    """Adjust `original` based on whether `updated` increased from it."""
    diff = updated - original
    return (adjustment_if_inc if diff > 0 else adjustment_if_dec) * diff + original
