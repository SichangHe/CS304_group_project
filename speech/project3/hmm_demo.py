"""With time-synchronous dynamic time warping, recordings in `recordings/` among
0~9 as templates to recognize the input audio.
Run as `python3 -m speech.project3.hmm_demo`."""

import argparse
from queue import Queue
from threading import Thread

import numpy as np

from speech.project1.main import audio_recording_thread
from speech.project2.lib import derive_cepstrum_velocities, mfcc_homebrew
from speech.project2.main import NUMBERS
from speech.project3 import DEMO_TEMPLATE_INDEXES
from speech.project3.hmm import HMM


def main() -> None:
    parser = argparse.ArgumentParser(description="DTW demo")
    parser.add_argument(
        "-o", "--output", help="Output file directory", default="output.wav"
    )
    parser.add_argument(
        "-n",
        "--n-gaussians",
        default=4,
        type=int,
        help="Number of gaussians for each state.",
    )
    args = parser.parse_args()

    byte_queue: Queue[bytes | None] = Queue()
    audio_thread = Thread(target=audio_recording_thread, args=(byte_queue, args.output))
    audio_thread.start()

    template_files = [
        [f"recordings/{number}{i}.wav" for i in DEMO_TEMPLATE_INDEXES]
        for number in NUMBERS
    ]
    hmm = HMM.from_template_file_names_and_labels(
        template_files, list(range(11)), n_gaussians=args.n_gaussians
    )

    full_input = np.array([], dtype=np.int16)
    while (data := byte_queue.get()) is not None:
        full_input = np.append(full_input, np.frombuffer(data, dtype=np.int16))
    input_mfcc = derive_cepstrum_velocities(mfcc_homebrew(full_input)[0])

    prediction = hmm.predict([input_mfcc])[0]
    print(f"Recognized number to be {prediction}.")


main() if __name__ == "__main__" else None
