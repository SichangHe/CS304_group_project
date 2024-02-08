"""With time-synchronous dynamic time warping, recordings in `recordings/` among
0~9 as templates to recognize the input audio.
Run as `python3 -m speech.project3.dtw_demo`."""

import argparse
from queue import Queue
from threading import Thread

import numpy as np

from speech.project1.main import audio_recording_thread
from speech.project2.lib import derive_cepstrum_velocities, mfcc_homebrew
from speech.project2.main import NUMBERS
from speech.project3 import DEMO_TEMPLATE_INDEXES, boosted_mfcc_from_file
from speech.project3.dtw import time_sync_dtw_search


def main() -> None:
    parser = argparse.ArgumentParser(description="DTW demo")
    parser.add_argument(
        "-o", "--output", help="Output file directory", default="output.wav"
    )
    args = parser.parse_args()

    byte_queue: Queue[bytes | None] = Queue()
    audio_thread = Thread(target=audio_recording_thread, args=(byte_queue, args.output))
    audio_thread.start()

    template_mfcc_s = [
        (boosted_mfcc_from_file(f"recordings/{number}{template_index}.wav"), number)
        for number in NUMBERS
        for template_index in DEMO_TEMPLATE_INDEXES
    ]

    full_input = np.array([], dtype=np.int16)
    while (data := byte_queue.get()) is not None:
        full_input = np.append(full_input, np.frombuffer(data, dtype=np.int16))
    input_mfcc = derive_cepstrum_velocities(mfcc_homebrew(full_input)[0])

    min_cost, prediction = time_sync_dtw_search(template_mfcc_s, input_mfcc)
    if prediction is None:
        print("Prediction failed because the test sample was too short.")
    else:
        print(f"Recognized number to be {prediction} with cost {min_cost:.2f}.")


main() if __name__ == "__main__" else None
