"""Plot log Mel spectrum and Mel Cepstrum of all speech files in `recordings/`.
Run as `python3 -m speech.project2.demo`."""

import argparse
import os
from queue import Queue
from threading import Thread

import numpy as np
from numpy.typing import NDArray

from ..project1 import CHUNK_MS, MS_IN_SECOND, SAMPLING_RATE
from ..project1.main import audio_recording_thread
from .lib import (
    Segmenter,
    cep2spec,
    mel_spectrum_from_frame,
    plot_cepstra,
    plot_log_mel_spectra,
    pre_emphasis,
    spec2cep,
)
from .main import NS_FILTER_BANKS


def plot_audio(
    cep: NDArray[np.float32],
    mel_spectrum: NDArray[np.float32],
    out_plot_name: str,
    n_filter_banks: int,
):
    dir_name = f"project2_plot/"
    os.makedirs(dir_name, exist_ok=True)

    log_spec_file_name = f"{dir_name}log_spectra{n_filter_banks}_{out_plot_name}"
    title = f"Log Mel Spectrum ({n_filter_banks} Filter Banks)"
    log_spec_fig = plot_log_mel_spectra(mel_spectrum, title=title)
    log_spec_fig.savefig(log_spec_file_name, bbox_inches="tight")

    ceps_file_name = f"{dir_name}cepstra{n_filter_banks}_{out_plot_name}"
    title = f"Mel Cepstrum ({n_filter_banks} Filter Banks)"
    ceps_fig = plot_cepstra(cep, title=title)
    ceps_fig.savefig(ceps_file_name, bbox_inches="tight")

    idct_file_name = f"{dir_name}idct{n_filter_banks}_{out_plot_name}"
    title = f"IDCT-Derived Log Spectrum ({n_filter_banks} Filter Banks)"
    idct_fig = plot_log_mel_spectra(cep2spec(cep)[0], title=title)
    idct_fig.savefig(idct_file_name, bbox_inches="tight")


def main():
    parser = argparse.ArgumentParser(description="Recorder")
    parser.add_argument("-o", "--output", help="Output audio file directory")
    parser.add_argument("-p", "--plot-output", help="Output plot files directory")
    args = parser.parse_args()

    out_file_name = args.output or "output.wav"
    out_plot_name = args.plot_output or "output.png"

    byte_queue: Queue[bytes | None] = Queue()
    audio_thread = Thread(
        target=audio_recording_thread, args=(byte_queue, out_file_name)
    )
    audio_thread.start()

    segmenter = Segmenter(SAMPLING_RATE * CHUNK_MS // MS_IN_SECOND)
    mel_spectra = list(
        np.array([], dtype=np.float32).reshape(n_filter_banks, 0)
        for n_filter_banks in NS_FILTER_BANKS
    )
    while (data := byte_queue.get()) is not None:
        audio_array = np.frombuffer(data, dtype=np.int16)
        segmenter.add_sample(pre_emphasis(audio_array))
        while (frame := segmenter.next()) is not None:
            for index, n_filter_banks in enumerate(NS_FILTER_BANKS):
                mel_spectrum = mel_spectrum_from_frame(frame, n_filter_banks)
                mel_spectra[index] = np.hstack(
                    (mel_spectra[index], mel_spectrum[:, np.newaxis])
                )
    for mel_spectrum, n_filter_banks in zip(mel_spectra, NS_FILTER_BANKS):
        cep, _ = spec2cep(mel_spectrum, ncep=13)
        plot_audio(cep, mel_spectrum, out_plot_name, n_filter_banks)

    audio_thread.join()


main() if __name__ == "__main__" else None
