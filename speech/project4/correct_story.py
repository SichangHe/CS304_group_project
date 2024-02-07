"""Run as `python3 -m speech.project4.correct_story`."""

import string

from . import DATA_DIR, read_file


def correct_story_lines() -> list[list[str]]:
    lines = read_file(f"{DATA_DIR}storycorrect.txt").splitlines()
    return [
        [split.strip(string.punctuation).lower() for split in line.split()]
        for line in lines
    ]


def main() -> None:
    print(correct_story_lines())


main() if __name__ == "__main__" else None
