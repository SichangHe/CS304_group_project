"""Run with `python3 -m speech.project1.test`."""
import unittest

import matplotlib.pyplot as plt
import numpy as np

from . import open_wave_file
from .audio_in import N_FRAME_PER_CHUNK
from .endpoint import get_classify_sample


def process(my_list, classify_frame):
    result = []
    for i in range(0, len(my_list), N_FRAME_PER_CHUNK):
        batch = my_list[i : i + N_FRAME_PER_CHUNK]
        result.append(classify_frame(batch))
    return result


class TestAudio(unittest.TestCase):
    def test_1(self):
        classify_frame = get_classify_sample()

        with open_wave_file("output.wav", "rb") as wave_file:
            sample_rate = wave_file.getframerate()
            num_frames = wave_file.getnframes()
            frames = wave_file.readframes(num_frames)

        duration = num_frames / sample_rate
        audio_array = np.frombuffer(frames, dtype=np.int16)
        boolean_array = process(audio_array, classify_frame)
        lspace = np.linspace(0, duration, len(audio_array))
        plt.scatter(lspace, audio_array, 0.5)
        filtered = [
            i
            for val, i in zip(
                boolean_array, np.linspace(0, duration, len(boolean_array))
            )
            if val == True
        ]
        plt.plot(filtered, [0] * len(filtered), "ro")

        plt.savefig("plot.png")


unittest.main() if __name__ == "__main__" else None
