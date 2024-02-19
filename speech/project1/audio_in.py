from queue import Queue
from typing import Mapping

from pyaudio import PyAudio, paContinue

from speech.project1 import (
    CHUNK_MS,
    MS_IN_SECOND,
    N_CHANNEL,
    RESOLUTION_FORMAT,
    SAMPLING_RATE,
)

N_FRAME_PER_CHUNK = SAMPLING_RATE * CHUNK_MS // MS_IN_SECOND
"""Number of frames per audio sample chunk."""


class AudioIn:
    def __init__(self):
        self.py_audio = PyAudio()
        self.audio_queue: Queue[tuple[bytes, int]] = Queue()
        self.stream = self.py_audio.open(
            format=RESOLUTION_FORMAT,
            channels=N_CHANNEL,
            rate=SAMPLING_RATE,
            input=True,
            frames_per_buffer=N_FRAME_PER_CHUNK,
            stream_callback=self.stream_callback,
        )

    def stream_callback(
        self,
        in_data: bytes | None,
        n_frame: int,
        time_info: Mapping[str, float],  # pyright: ignore reportUnusedVariable
        status: int,  # pyright: ignore reportUnusedVariable
    ):
        """A callback for `PyAudio.open`, which sends input audio data to
        `self.audio_queue`."""
        assert in_data is not None
        self.audio_queue.put((in_data, n_frame))
        return None, paContinue

    def discard_first_at_least(self, n_discard=5):
        """Discard first `n_discard` samples in `self.audio_queue` to avoid
        initial unstable samples. Then, discard all previous samples."""
        if self.audio_queue.qsize() < n_discard:
            for _ in range(n_discard):
                self.audio_queue.get(timeout=0.1)
        with self.audio_queue.mutex:
            self.audio_queue.queue.clear()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stream.close()
        self.py_audio.terminate()
