import wave
from contextlib import contextmanager
from queue import Queue
from typing import Mapping

from pyaudio import PyAudio, paContinue, paInt16

CHUNK = 1024
FORMAT = paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 1


def main():
    """Record 5sec into `output.wav`"""
    audio_queue: Queue[tuple[bytes, int]] = Queue()

    def stream_callback(
        in_data: bytes | None, n_frame: int, time_info: Mapping[str, float], status: int
    ):
        """Send input audio data to `audio_queue`."""
        assert in_data is not None
        audio_queue.put((in_data, n_frame))
        return None, paContinue

    with wave.open("output.wav", "wb") as file, open_pyaudio() as py_audio:
        file.setnchannels(CHANNELS)
        file.setsampwidth(py_audio.get_sample_size(FORMAT))
        file.setframerate(RATE)

        stream = py_audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=stream_callback,
        )

        frames_left = RATE * RECORD_SECONDS
        print("Recording...")

        while frames_left > 0:
            data, n_frame = audio_queue.get(timeout=0.1)
            assert n_frame <= CHUNK

            # TODO: @Luyao: Calculate intensity for endpointing.
            file.writeframes(data)
            frames_left -= n_frame

        print("Done")
        stream.close()


@contextmanager
def open_pyaudio():
    py_audio = None
    try:
        yield (py_audio := PyAudio())
    finally:
        py_audio.terminate() if py_audio else None


main() if __name__ == "__main__" else None
