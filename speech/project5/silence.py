"""Run as `python3 -m speech.project5.silence`."""

import wave
from queue import Queue
from threading import Thread

from speech.project1 import (
    MAX_PAUSE_MS,
    MS_IN_SECOND,
    N_CHANNEL,
    RESOLUTION_FORMAT,
    SAMPLING_RATE,
)
from speech.project1.audio_in import AudioIn


def record_audio(out_file_name: str):
    write_queue: Queue[bytes | None] = Queue()

    with wave.open(out_file_name, "wb") as out_file, AudioIn() as audio_in:
        # Configure output file.
        out_file.setnchannels(N_CHANNEL)
        out_file.setsampwidth(audio_in.py_audio.get_sample_size(RESOLUTION_FORMAT))
        out_file.setframerate(SAMPLING_RATE)
        writer_thread = Thread(
            target=frame_writing_thread, args=(out_file, write_queue)
        )
        writer_thread.start()

        try:
            input("Press Enter to start recording...")
            audio_in.discard_first_at_least()
            print("Recording...")
            n_samples = 0

            while n_samples < MAX_PAUSE_MS * SAMPLING_RATE // MS_IN_SECOND:
                data, n_frame = audio_in.audio_queue.get()
                n_samples += n_frame
                write_queue.put(data)
            print("Stopping recording.")
        finally:
            write_queue.put(None)
            writer_thread.join(timeout=0.1)


def frame_writing_thread(out_file: wave.Wave_write, byte_queue: Queue[bytes | None]):
    """A thread that writes frames from `byte_queue` to `out_file`."""
    while data := byte_queue.get():
        out_file.writeframes(data)


MAXIMUM_DRAWING_TIME = 10
"""Maximum duration of the spectrum plot"""
MAX_DRAWING_SAMPLES = SAMPLING_RATE * MAXIMUM_DRAWING_TIME
"""Maximum number of samples drawn"""


def main() -> None:
    for index in range(10):
        out_file_name = f"recordings/silence{index}.wav"
        print(f"Recording {out_file_name}.")
        record_audio(out_file_name)


main() if __name__ == "__main__" else None
