"""Run as `python3 -m speech.project4.correct_story`."""

import string

from . import DATA_DIR, read_file


def correct_story() -> list[str]:
    splits = read_file(f"{DATA_DIR}storycorrect.txt").split()
    return [split.strip(string.punctuation).lower() for split in splits]


def main() -> None:
    print(correct_story())


main() if __name__ == "__main__" else None
