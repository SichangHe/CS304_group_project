"""Demo for recognizing unrestricted digits.
Run as `python3 -m speech.project6.phone_demo`."""

import argparse
from queue import Queue
from threading import Thread

import numpy as np

from speech.project1.main import audio_recording_thread
from speech.project2.lib import derive_cepstrum_velocities, mfcc_homebrew
from speech.project5.hmm import match_sequence_against_hmm_states
from speech.project5.phone_rand import build_hmm_graph, load_silence_hmms
from speech.project6.trncontspch import train_digit_sequences


def main() -> None:
    parser = argparse.ArgumentParser(description="Phone number recognition demo")
    parser.add_argument(
        "-o", "--output", help="Output file directory", default="output.wav"
    )
    args = parser.parse_args()

    digit_hmm_dict = train_digit_sequences()
    digit_hmms = [digit_hmm_dict[digit] for digit in range(10)]
    silence_single_hmm = load_silence_hmms()
    non_emitting_states, emitting_states = build_hmm_graph(
        digit_hmms, silence_single_hmm
    )

    byte_queue: Queue[bytes | None] = Queue()
    audio_thread = Thread(target=audio_recording_thread, args=(byte_queue, args.output))
    audio_thread.start()

    full_input = np.array([], dtype=np.int16)
    while (data := byte_queue.get()) is not None:
        full_input = np.append(full_input, np.frombuffer(data, dtype=np.int16))
    input_mfcc = derive_cepstrum_velocities(mfcc_homebrew(full_input)[0])
    recognition_list = match_sequence_against_hmm_states(
        input_mfcc, non_emitting_states, emitting_states, beam_width=4000.0
    )
    recognition = "".join(map(str, recognition_list))
    print(f"Recognized as `{recognition}`.")


main() if __name__ == "__main__" else None
