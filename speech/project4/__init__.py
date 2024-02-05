from typing import Final

DATA_DIR: Final = "project4_data/"


def read_file(filename: str):
    with open(filename, "r") as file:
        return file.read()


def write_file(filename: str, content: str):
    with open(filename, "w") as file:
        file.write(content)
