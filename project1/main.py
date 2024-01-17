import wave
from contextlib import contextmanager
from queue import Queue
from typing import Mapping

import numpy as np
from numpy.typing import NDArray
from pyaudio import PyAudio, paContinue, paInt16

FORMAT = paInt16
SIZEOF_FORMAT = 2  # bytes
CHANNELS = 1
RATE = 16000
CHUNK_MS = 20
CHUNK = RATE * CHUNK_MS // 1000
"""Number of frames for 20ms."""
RECORD_SECONDS = 999
MAX_OFF_TIME = 2000


def main():
    """Record 5sec into `output.wav`"""
    audio_queue: Queue[tuple[bytes, int]] = Queue()

    buffer = b""
    buffer_size = RATE * MAX_OFF_TIME * SIZEOF_FORMAT // 1000

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

    input("Press Enter to start recording...")

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

        recording_status = get_recording_status()

        # Discard first 5 chunks.
        for _ in range(5):
            _ = audio_queue.get(timeout=0.1)

        while frames_left > 0:
            data, n_frame = audio_queue.get(timeout=0.1)
            assert n_frame <= CHUNK

            audio_array = np.frombuffer(data, dtype=np.int16)
            status = recording_status(audio_array)
            if status == -1:
                continue
            elif status == 0:
                buffer += data
                if len(buffer) > buffer_size:
                    file.writeframes(buffer[:-buffer_size])
                    buffer = buffer[-buffer_size:]
                frames_left -= n_frame
            elif status == 1:
                break

        print("Done")
        stream.close()


STARTING_DECIBEL_THRESHHOLD = 15.0
CONTINUING_DECIBEL_THRESHHOLD = 2.0
STOPPING_DECIBEL_THRESHHOLD = -20.0
WEAK_ADJUSTMENT = 0.05
STRONG_ADJUSTMENT = 0.8


def get_recording_status():
    """
    Get current recording status

    Returns:
        int: The status code indicating the current state of the task.
            -1: The recording has not started yet.
             0: The recording is currently in progress.
             1: The recording has been completed and should be stopped.
    """
    classify_frame = get_classify_frame()
    off_time = 0
    started = False

    def recording_status(arr: NDArray[np.int16]) -> bool:
        nonlocal off_time, started

        if not started:
            started = classify_frame(arr)
            return -1
        else:
            if classify_frame(arr):
                off_time = 0
            else:
                off_time += CHUNK_MS
        if off_time > MAX_OFF_TIME:
            return 1

        return 0

    return recording_status


def get_classify_frame():
    level: np.float64 | None = None
    background: np.float64 | None = None
    foreground = 0.0
    speaking = False
    forgetfactor = 1.2

    def classify_frame(arr: NDArray[np.int16]) -> bool:
        nonlocal level, background, foreground, speaking
        current = sample_decibel_energy(arr)
        if level is None:
            level = current
        if background is None:
            background = current

        level = ((level * forgetfactor) + current) / (forgetfactor + 1.0)

        print(
            f"speaking: {speaking}, current: {current:.1f}, background: {background:.1f}, foreground: {foreground:.1f}, level: {level:.1f}."
        )

        if speaking:
            if (
                level - background < CONTINUING_DECIBEL_THRESHHOLD
                or level - foreground < STOPPING_DECIBEL_THRESHHOLD
            ):
                speaking = False
                background = background if background < level else level
            else:
                foreground = adjust_conditionally_on_change(
                    foreground, level, STRONG_ADJUSTMENT, WEAK_ADJUSTMENT
                )
        if not speaking:
            if level - background >= STARTING_DECIBEL_THRESHHOLD:
                speaking = True
                foreground = level
            else:
                background = adjust_conditionally_on_change(
                    background, level, WEAK_ADJUSTMENT, STRONG_ADJUSTMENT
                )

        return speaking

    return classify_frame


def adjust_conditionally_on_change(
    original, updated, adjustment_if_inc, adjustment_if_dec
):
    diff = updated - original
    return (adjustment_if_inc if diff > 0 else adjustment_if_dec) * diff + original


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
