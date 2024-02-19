"""Run with `python3 -m speech.project1.main`."""

import argparse
import wave
from queue import Queue
from threading import Thread

import matplotlib.pyplot as plt
import numpy as np

from speech.project1 import N_CHANNEL, RESOLUTION_FORMAT, SAMPLING_RATE
from speech.project1.audio_in import AudioIn
from speech.project1.endpoint import Endpointer


def audio_recording_thread(byte_queue: Queue[bytes | None], out_file_name: str):
    """Endpoint speech and record into `out_file_name`."""
    write_queue: Queue[bytes | None] = Queue()
    overlay_queue: Queue[bytes | None] = Queue()

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

            endpointer = Endpointer(audio_in, overlay_queue)
            while data := overlay_queue.get():
                write_queue.put(data)
                byte_queue.put(data)
            print("Stopping recording.")
            del endpointer
        finally:
            write_queue.put(None)
            byte_queue.put(None)
            writer_thread.join(timeout=0.1)


def frame_writing_thread(out_file: wave.Wave_write, byte_queue: Queue[bytes | None]):
    """A thread that writes frames from `byte_queue` to `out_file`."""
    while data := byte_queue.get():
        out_file.writeframes(data)


MAXIMUM_DRAWING_TIME = 10
"""Maximum duration of the spectrum plot"""
MAX_DRAWING_SAMPLES = SAMPLING_RATE * MAXIMUM_DRAWING_TIME
"""Maximum number of samples drawn"""


def main():
    """Run GUI from main thread."""
    parser = argparse.ArgumentParser(description="Recorder")
    parser.add_argument("-g", "--gui", action="store_true", help="Show spectrum GUI.")
    parser.add_argument("-o", "--output", help="Output file directory")
    args = parser.parse_args()

    out_file_name = args.output or "output.wav"

    byte_queue: Queue[bytes | None] = Queue()
    audio_thread = Thread(
        target=audio_recording_thread, args=(byte_queue, out_file_name)
    )
    audio_thread.start()

    if args.gui:
        _, ax = plt.subplots()
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
