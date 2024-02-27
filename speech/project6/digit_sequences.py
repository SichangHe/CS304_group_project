"""Digit sequences for continuous speech recognition.
Run as `python3 -m speech.project6.digit_sequences`"""

from os import system
from queue import Queue
from typing import Final

from speech.project1.main import audio_recording_thread

SEQUENCES: Final = [
    "0123456789",
    "9876543210",
    "1234567890",
    "0987654321",
    "1357902468",
    "8642097531",
]
"""Digit sequences for training."""

INDEXES: Final = range(5)
"""Indexes for training sequences."""

SEQUENCE_FILE_NAMES: Final = [
    f"recordings/{sequence}_{index}.wav" for sequence in SEQUENCES for index in INDEXES
]


def main() -> None:
    for out_file_name in SEQUENCE_FILE_NAMES:
        while True:
            print(f"Recording {out_file_name}.")
            audio_recording_thread(Queue(), out_file_name)

            system(f"open {out_file_name}")
            if input("Press Enter to record the next one.") == "":
                break


main() if __name__ == "__main__" else None
