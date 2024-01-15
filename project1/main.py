import wave
from contextlib import contextmanager
from queue import Queue
from typing import Mapping

import numpy as np
from numpy.typing import NDArray
from pyaudio import PyAudio, paContinue, paInt16

FORMAT = paInt16
CHANNELS = 1
RATE = 16000
CHUNK = RATE * 20 // 1000
"""Number of frames for 20ms."""
RECORD_SECONDS = 999


def main():
    """Record 5sec into `output.wav`"""
    audio_queue: Queue[tuple[bytes, int]] = Queue()

    def stream_callback(
        in_data: bytes | None,
        n_frame: int,
        time_info: Mapping[str, float],  # pyright: ignore reportUnusedVariable
        status: int,  # pyright: ignore reportUnusedVariable
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

            audio_array = np.frombuffer(data, dtype=np.int16)
            if break_condition(audio_array):
                break
            file.writeframes(data)
            frames_left -= n_frame

        print("Done")
        stream.close()


DECIBEL_THRESHHOLD = 20


def get_break_condition():
    level = -1
    background = -1
    adjustment = 0.05
    forgetfactor = 2
    init_background_adjustment = 0.65

    def break_condition(arr: NDArray[np.int16]) -> bool:
        nonlocal level, background
        current = sample_decibel_energy(arr)
        if level == -1:
            # initial case
            level = current
        if background == -1:
            background = current * init_background_adjustment

        level = ((level * forgetfactor) + current) / (forgetfactor + 1)

        if current < background:
            background = current
        else:
            background += (current - background) * adjustment

        print("background level: " + str(background))
        print("current level: " + str(level))
        print("level - background: " + str(level - background))

        return True if level - background < DECIBEL_THRESHHOLD else False

    return break_condition


def sample_decibel_energy(arr: NDArray[np.int16]) -> np.float64:
    """Calculate the energy in decibel of an audio sample."""
    arr_int32 = arr.astype(np.int32)  # avoid overflow
    power: np.int32 = arr_int32.dot(arr_int32)
    return np.log10(power) * 10.0


@contextmanager
def open_pyaudio():
    py_audio = None
    try:
        yield (py_audio := PyAudio())
    finally:
        py_audio.terminate() if py_audio else None


main() if __name__ == "__main__" else None
