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
