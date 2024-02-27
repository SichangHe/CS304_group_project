"""Digit sequences for continuous speech recognition.
Run as `python3 -m speech.project6.digit_sequences`"""

from os import system

from speech.project5.silence import record_audio

SEQUENCES = [
    "0123456789",
    "9876543210",
    "1234567890",
    "0987654321",
    "1357902468",
    "8642097531",
]
"""Digit sequences for training."""

INDEXES = range(5)
"""Indexes for training sequences."""


def main() -> None:
    file_names = (
        f"recordings/{sequence}_{index}.wav"
        for sequence in SEQUENCES
        for index in INDEXES
    )
    for out_file_name in file_names:
        while True:
            print(f"Recording {out_file_name}.")
            record_audio(out_file_name)

            system(f"open {out_file_name}")
            if input("Press Enter to record the next one.") == "":
                break


main() if __name__ == "__main__" else None
