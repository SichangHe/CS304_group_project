import numpy as np

from ..project1 import open_wave_file


def read_audio_file(file_name: str):
    with open_wave_file(file_name, "rb") as wave_file:
        n_frames = wave_file.getnframes()
        frames = wave_file.readframes(n_frames)
    return np.frombuffer(frames, dtype=np.int16)
