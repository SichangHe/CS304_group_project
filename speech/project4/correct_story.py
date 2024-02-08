"""Run as `python3 -m speech.project4.correct_story`."""

import string

from . import DATA_DIR, read_lines_stripped, write_split_lines


def correct_story_lines() -> list[list[str]]:
    lines = read_lines_stripped(f"{DATA_DIR}storycorrect.txt")
    return [
        [split.strip(string.punctuation).lower() for split in line.split()]
        for line in lines
    ]


def correct_story_lines_stripped() -> list[list[str]]:
    lines = correct_story_lines()
    return [line for line in lines if len(line) > 0]


def main() -> None:
    correct_story = correct_story_lines()
    write_split_lines(f"cleaned_storycorrect.txt", correct_story_lines())
    print(correct_story)
    print(correct_story_lines_stripped())


main() if __name__ == "__main__" else None
