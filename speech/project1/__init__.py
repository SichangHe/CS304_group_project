import wave
from contextlib import contextmanager
from typing import Iterator

from pyaudio import paInt16

RESOLUTION_FORMAT = paInt16
"""Bit resolution per frame."""
N_CHANNEL = 1
"""Number of audio channels."""
SAMPLING_RATE = 16000
"""Audio sampling rate in frames per second."""
CHUNK_MS = 20
"""Audio sample chunk duration in milliseconds."""
MS_IN_SECOND = 1000
"""Number of milliseconds in a second."""
MAX_PAUSE_MS = 500
"""Maximum pause duration in milliseconds during speech."""


@contextmanager
def open_wave_file(filename, mode) -> Iterator[wave.Wave_read]:
    wave_file = None
    try:
        yield (wave_file := wave.open(filename, mode))
    finally:
        wave_file.close() if wave_file else None
