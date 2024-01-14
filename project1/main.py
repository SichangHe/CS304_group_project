import wave

from pyaudio import PyAudio, paInt16

CHUNK = 1024
FORMAT = paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5


def main():
    """Record 5sec into `output.wav`"""
    with wave.open("output.wav", "wb") as file:
        py_audio = PyAudio()
        file.setnchannels(CHANNELS)
        file.setsampwidth(py_audio.get_sample_size(FORMAT))
        file.setframerate(RATE)

        stream = py_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print("Recording...")
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            file.writeframes(stream.read(CHUNK))
        print("Done")

        stream.close()
        py_audio.terminate()


main() if __name__ == "__main__" else None
