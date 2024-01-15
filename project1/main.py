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


STARTING_DECIBEL_THRESHHOLD = 20.0
CONTINUING_DECIBEL_THRESHHOLD = 5.0


def get_break_condition():
    level: np.float64 | None = None
    background: np.float64 | None = None
    speaking = False
    adjustment = 0.05
    forgetfactor = 1.2

    def break_condition(arr: NDArray[np.int16]) -> bool:
        nonlocal level, background, speaking

        current = sample_decibel_energy(arr)
        if level is None:
            level = current
        if background is None:
            background = current

        level = ((level * forgetfactor) + current) / (forgetfactor + 1.0)

        if speaking and level - background < CONTINUING_DECIBEL_THRESHHOLD:
            speaking = False
            background = background if background < level else level
            return True
        if not speaking:
            if current - background >= STARTING_DECIBEL_THRESHHOLD:
                speaking = True
            else:
                # FIXME: Disrupted by sudden silence.
                if background < level:
                    background += (current - background) * adjustment
                else:
                    background = level

        print(
            f"speaking: {speaking}, current: {current:.1f}, background: {background:.1f}, level: {level:.1f}."
        )

        return False

    return break_condition


def sample_decibel_energy(arr: NDArray[np.int16]) -> np.float64:
    """Calculate the energy in decibel of an audio sample."""
    arr = arr.astype(np.int64)  # avoid overflow
    power = arr.dot(arr) / arr.size
    return np.log10(power) * 10.0


@contextmanager
def open_pyaudio():
    py_audio = None
    try:
        yield (py_audio := PyAudio())
    finally:
        py_audio.terminate() if py_audio else None


main() if __name__ == "__main__" else None
