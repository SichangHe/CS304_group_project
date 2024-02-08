"""Run as `python3 -m speech.project4.correct_story`."""

import string

from . import DATA_DIR, read_lines_stripped


def correct_story_lines() -> list[list[str]]:
    lines = read_lines_stripped(f"{DATA_DIR}storycorrect.txt")
    return [
        [split.strip(string.punctuation).lower() for split in line.split()]
        for line in lines
        if line
    ]


def main() -> None:
    print(correct_story_lines())


main() if __name__ == "__main__" else None
