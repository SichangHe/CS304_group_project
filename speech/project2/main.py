"""Plot log Mel spectrum and Mel Cepstrum of all speech files in `recordings/`.
Run as `python3 -m speech.project2.main`."""

import os

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from . import read_audio_file
from .lib import cep2spec, mfcc_homebrew, plot_cepstra, plot_log_mel_spectra

plt.rcParams["font.size"] = 24

NUMBERS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
)

NS_FILTER_BANKS = (40, 30, 25)


def plot_audio_file(number: str, i: int, n_filter_banks: int):
    file_name = f"recordings/{number}{i}.wav"
    print(f"Working on {file_name} using {n_filter_banks} filter banks.")
    audio_array = read_audio_file(file_name)

    dir_name = f"project2_plot/{number}/"
    os.makedirs(dir_name, exist_ok=True)
    cep, mspec = mfcc_homebrew(audio_array=audio_array, n_filter_banks=n_filter_banks)

    log_spec_file_name = f"{dir_name}{number}{i}log_spectra{n_filter_banks}.png"
    title = f"Log Mel Spectrum of `{number}`\n(#{i}, {n_filter_banks} Filter Banks)"
    log_spec_fig: Figure = plot_log_mel_spectra(mspec.T, title=title)
    log_spec_fig.savefig(log_spec_file_name, bbox_inches="tight")

    ceps_file_name = f"{dir_name}{number}{i}cepstra{n_filter_banks}.png"
    title = f"Mel Cepstrum of `{number}`\n(#{i}, {n_filter_banks} Filter Banks)"
    ceps_fig: Figure = plot_cepstra(cep.T, title=title)
    ceps_fig.savefig(ceps_file_name, bbox_inches="tight")

    idct_file_name = f"{dir_name}{number}{i}idct{n_filter_banks}.png"
    title = f"IDCT-Derived Log Spectrum of `{number}`\n(#{i}, {n_filter_banks} Filter Banks)"
    idct_fig: Figure = plot_log_mel_spectra(cep2spec(cep.T)[0], title=title)
    idct_fig.savefig(idct_file_name, bbox_inches="tight")
    plt.close("all")


def main():
    for number in NUMBERS:
        for i in range(4):
            for n_filter_banks in NS_FILTER_BANKS:
                plot_audio_file(number, i, n_filter_banks)
                plt.close("all")


main() if __name__ == "__main__" else None
