from typing import Final

DATA_DIR: Final = "project4_data/"


def write_split_lines(filename: str, lines: list[list[str]]):
    write_file(filename, "\n".join(" ".join(line) for line in lines))


def read_file(filename: str):
    with open(filename, "r") as file:
        return file.read()


def write_file(filename: str, content: str):
    with open(filename, "w") as file:
        file.write(content)
