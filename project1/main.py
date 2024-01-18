import wave
from contextlib import contextmanager
from enum import Enum
from queue import Queue
from threading import Thread
from typing import Mapping

import numpy as np
from numpy.typing import NDArray
from pyaudio import PyAudio, paContinue, paInt16
import matplotlib.pyplot as plt
import argparse

RESOLUTION_FORMAT = paInt16
"""Bit resolution per frame."""
SIZEOF_FRAME = 2
"""Size of each frame in bytes."""
N_CHANNEL = 1
"""Number of audio channels."""
SAMPLING_RATE = 16000
"""Audio sampling rate in frames per second."""
CHUNK_MS = 20
"""Audio sample chunk duration in milliseconds."""
MS_IN_SECOND = 1000
"""Number of milliseconds in a second."""
N_FRAME_PER_CHUNK = SAMPLING_RATE * CHUNK_MS // MS_IN_SECOND
"""Number of frames per audio sample chunk."""
BACKTRACK_MS = 200
"""Duration in milliseconds to backtrack when speech starts."""
SIZE_OF_BACKTRACK = SAMPLING_RATE * BACKTRACK_MS // MS_IN_SECOND
"""Size of the buffer in bytes for backtracking when speech starts."""
MAX_PAUSE_MS = 2000
"""Maximum pause duration in milliseconds during speech."""
SIZE_OF_SILENT_END = SAMPLING_RATE * MAX_PAUSE_MS * SIZEOF_FRAME // MS_IN_SECOND
"""Size of the buffer in bytes at the silent end."""


def audio_recording_thread(byte_queue: Queue[bytes | None], out_file_name="output.wav"):
    """Endpoint speech and record into `out_file_name`."""
    audio_queue: Queue[tuple[bytes, int]] = Queue()
    stream_callback = get_stream_callback(audio_queue)
    write_queue: Queue[bytes | None] = Queue()

    buffer = b""
    pending_samples = b""

    with wave.open(out_file_name, "wb") as out_file, open_pyaudio() as py_audio:
        # Configure output file.
        out_file.setnchannels(N_CHANNEL)
        out_file.setsampwidth(py_audio.get_sample_size(RESOLUTION_FORMAT))
        out_file.setframerate(SAMPLING_RATE)
        writer_thread = Thread(
            target=frame_writing_thread, args=(out_file, write_queue)
        )
        writer_thread.start()
        stream = py_audio.open(
            format=RESOLUTION_FORMAT,
            channels=N_CHANNEL,
            rate=SAMPLING_RATE,
            input=True,
            frames_per_buffer=N_FRAME_PER_CHUNK,
            stream_callback=stream_callback,
        )

        try:
            input("Press Enter to start recording...")
            discard_first_at_least(audio_queue)
            print("Recording...")

            classify_sample = get_classify_sample()
            recording_status = get_recording_status()
            while True:
                data, _ = audio_queue.get(timeout=0.1)
                byte_queue.put(data)
                audio_array = np.frombuffer(data, dtype=np.int16)
                is_speech = classify_sample(audio_array)
                status = recording_status(is_speech)
                match status:
                    case RecordingStatus.PENDING:
                        pending_samples += data
                        continue
                    case RecordingStatus.STOPPING:
                        break
                    case RecordingStatus.STARTING:
                        # Backtrack previous sample before recording starts.
                        write_queue.put(pending_samples[-SIZE_OF_BACKTRACK:])
                        pending_samples = b""
                buffer += data
                if len(buffer) > SIZE_OF_SILENT_END:
                    write_queue.put(buffer[:-SIZE_OF_SILENT_END])
                    buffer = buffer[-SIZE_OF_SILENT_END:]
            print("Stopping recording.")
        finally:
            write_queue.put(None)
            stream.close()
            writer_thread.join(timeout=0.1)


def frame_writing_thread(out_file: wave.Wave_write, byte_queue: Queue[bytes | None]):
    """A thread that writes frames from `byte_queue` to `out_file`."""
    while data := byte_queue.get():
        out_file.writeframes(data)


def get_stream_callback(audio_queue: Queue[tuple[bytes, int]]):
    """Get a callback for `PyAudio.open`, which sends input audio data to
    `audio_queue`."""

    def stream_callback(
        in_data: bytes | None,
        n_frame: int,
        time_info: Mapping[str, float],  # pyright: ignore reportUnusedVariable
        status: int,  # pyright: ignore reportUnusedVariable
    ):
        nonlocal audio_queue

        assert in_data is not None
        audio_queue.put((in_data, n_frame))
        return None, paContinue

    return stream_callback


def discard_first_at_least(audio_queue: Queue[tuple[bytes, int]], n_discard=5):
    """Discard first `n_discard` samples in `audio_queue` to avoid initial
    unstable samples. Then, discard all previous samples."""
    if audio_queue.qsize() < n_discard:
        for _ in range(n_discard):
            audio_queue.get(timeout=0.1)
    with audio_queue.mutex:
        audio_queue.queue.clear()


STARTING_THRESHOLD_DB = 15.0
"""Threshold from background in decibels for starting to classify as speeches."""
CONTINUING_THRESHOLD_DB = 2.0
"""Threshold from background in decibels for continuing to classify as speeches."""
STOPPING_THRESHOLD_DB = -20.0
"""Threshold from foreground in decibels for stopping to classify as speeches."""
WEAK_ADJUSTMENT = 0.05
STRONG_ADJUSTMENT = 0.8


def get_recording_status():
    """Get a closure that determines the current recording status based on
    whether a sample is classified as speech.
    Stopping condition: `MAX_PAUSE_MS` ms after speech stops.
    """
    off_time = 0
    started = False

    def recording_status(is_speech: bool) -> RecordingStatus:
        nonlocal off_time, started

        if not started:
            if is_speech:
                started = True
                return RecordingStatus.STARTING
            return RecordingStatus.PENDING
        else:
            if is_speech:
                off_time = 0
            else:
                off_time += CHUNK_MS
        if off_time > MAX_PAUSE_MS:
            return RecordingStatus.STOPPING

        return RecordingStatus.GOING

    return recording_status


class RecordingStatus(Enum):
    """- `PENDING`: The recording has not started yet.
    - `GOING`: The recording is currently in progress.
    - `STOPPING`: The recording has been completed and should be stopped.
    - `STARTING`: The recording has just started."""

    PENDING = -1
    GOING = 0
    STOPPING = 1
    STARTING = 2


FORGET_FACTOR = 1.2
"""Forgetting factor for updating `level` energy in `get_classify_sample`."""


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

        print(
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


def adjust_conditionally_on_change(
    original, updated, adjustment_if_inc, adjustment_if_dec
):
    """Adjust `original` based on whether `updated` increased from it."""
    diff = updated - original
    return (adjustment_if_inc if diff > 0 else adjustment_if_dec) * diff + original


def sample_decibel_energy(arr: NDArray[np.int16]) -> np.float64:
    """Calculate the energy of an audio sample in decibel."""
    arr = arr.astype(np.int64)  # avoid overflow
    power = arr.dot(arr) / arr.size
    return np.log10(power) * 10.0


@contextmanager
def open_pyaudio():
    """Provide a self-cleaning-up `PyAudio` instance for a `with` statement."""
    py_audio = None
    try:
        yield (py_audio := PyAudio())
    finally:
        py_audio.terminate() if py_audio else None


MAXIMUM_DRAWING_TIME = 10
"""Maximum duration of the spectrum plot"""
MAX_DRAWING_SAMPLES = SAMPLING_RATE * MAXIMUM_DRAWING_TIME
"""Maximum number of samples drawn"""


def main():
    """Run GUI from main thread."""
    parser = argparse.ArgumentParser(description="Recorder")
    parser.add_argument("-g", "--gui", action="store_true", help="Show spectrum GUI.")
    args = parser.parse_args()
    show_gui = False
    if args.gui:
        show_gui = True

    byte_queue: Queue[bytes] = Queue()
    audio_thread = Thread(target=audio_recording_thread, args=(byte_queue,))
    audio_thread.start()

    _, ax = plt.subplots()

    if show_gui:
        plot_array = np.array([])
        i = 0
        while data := byte_queue.get():
            input_arr = np.frombuffer(data, dtype=np.int16)
            plot_array = np.append(plot_array, input_arr)
            i += 1
            if i % 5 == 0:
                # draw every 5 chunks to avoid gui latency
                num_samples = plot_array.shape[0]
                length = num_samples / SAMPLING_RATE
                lspace = np.linspace(0, length, plot_array.shape[0])
                ax.clear()
                ax.scatter(lspace, plot_array, 0.05)
                plt.draw()
                plt.pause(0.01)
            if plot_array.shape[0] > MAX_DRAWING_SAMPLES:
                plot_array = plot_array[-MAX_DRAWING_SAMPLES:]

    audio_thread.join()


main() if __name__ == "__main__" else None
