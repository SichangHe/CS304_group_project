import wave
from contextlib import contextmanager
from queue import Queue
from typing import Mapping
import numpy as np

from pyaudio import PyAudio, paContinue, paInt16

CHUNK = 1024
FORMAT = paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 999


def main():
    """Record 5sec into `output.wav`"""
    audio_queue: Queue[tuple[bytes, int]] = Queue()

    def stream_callback(
        in_data: bytes | None, n_frame: int, time_info: Mapping[str, float], status: int
    ):
        """Send input audio data to `audio_queue`."""
        assert in_data is not None
        audio_queue.put((in_data, n_frame))
        return None, paContinue

    with wave.open("output.wav", "wb") as file, open_pyaudio() as py_audio:
        file.setnchannels(CHANNELS)
        file.setsampwidth(py_audio.get_sample_size(FORMAT))
        file.setframerate(RATE)

        stream = py_audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=stream_callback,
        )

        frames_left = RATE * RECORD_SECONDS
        print("Recording...")

        break_condition = get_break_condition()

        while frames_left > 0:
            data, n_frame = audio_queue.get(timeout=0.1)
            assert n_frame <= CHUNK

            # TODO: @Luyao: Calculate intensity for endpointing.
            audio_array = np.frombuffer(data, dtype=np.int16)
            if break_condition(audio_array):
                break
            file.writeframes(data)
            frames_left -= n_frame

        print("Done")
        stream.close()


def get_break_condition():
    level = -1
    threshhold = 1000000000

    def energy_per_sample_in_decibel(arr: np.ndarray[np.int16]):
        arr_int32 = arr.astype(np.int32)
        return np.sum(arr_int32**2)

    def break_condition(arr: np.ndarray[np.int16]) -> bool:
        nonlocal level

        if level == -1:
            # initial case
            level = energy_per_sample_in_decibel(arr)

        level = level / 2 + energy_per_sample_in_decibel(arr) / 2
        print("current level: " + str(level))

        return True if level < threshhold else False

    return break_condition


@contextmanager
def open_pyaudio():
    py_audio = None
    try:
        yield (py_audio := PyAudio())
    finally:
        py_audio.terminate() if py_audio else None


main() if __name__ == "__main__" else None
