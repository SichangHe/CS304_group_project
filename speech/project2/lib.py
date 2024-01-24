import math
from functools import lru_cache

import numpy as np
import scipy
from numpy.typing import NDArray
from scipy import fft
from scipy.signal import spectrogram

from ..project1 import CHUNK_MS, MS_IN_SECOND, SAMPLING_RATE


def pre_emphasis(signal: NDArray[np.int16], alpha: float = 0.95) -> NDArray[np.float32]:
    """Apply pre-emphasis to the input signal."""
    pre_emphasized_signal = signal.astype(np.float32, copy=True)
    pre_emphasized_signal[1:] -= alpha * pre_emphasized_signal[:-1]
    return pre_emphasized_signal


class Segmenter:
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.half_window_size = window_size // 2
        self.buffer: NDArray[np.float32] = np.array([], dtype=np.float32)

    def add_sample(self, sample: NDArray[np.float32]):
        """Add a sample to be segmented."""
        self.buffer = np.concatenate((self.buffer, sample))

    def next(self) -> NDArray[np.float32] | None:
        """Segment the collected audio signal into frames."""
        if len(self.buffer) < self.window_size:
            return None
        result = self.buffer[: self.window_size]
        self.buffer = self.buffer[self.half_window_size :]
        return result


def window(samples: NDArray[np.float32]) -> NDArray[np.float32]:
    """Applies the Hanning window function to the given audio samples."""
    m = len(samples)
    return samples * hanning(m)


@lru_cache(maxsize=8)
def hanning(m: int):
    """The Hanning window function for the first `m` points."""
    return 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(m) / m)


def fast_fourier_transform(samples: NDArray[np.float32]) -> NDArray[np.complex_]:
    """Fast Fourier Transform (FFT) of the given audio samples.
    Overwrites the input `samples` for FFT speed.
    Outputs `m` numbers. `m` is a 2's power.
    The first (`m` >> 1) + 1 output numbers are useful."""
    original_len = len(samples)
    m: int = 1 << math.ceil(math.log2(original_len))
    transformed: NDArray[np.complex_] = fft.fft(samples, n=m, overwrite_x=True)  # type: ignore
    return transformed


def frequencies_after_fft(m: int, sampling_rate: int) -> NDArray[np.float32]:
    """Frequencies of FFT output of length `m`, a 2's power."""
    n_useful_point = (m >> 1) + 1
    frequencies: NDArray[np.float32] = (
        np.linspace(0, 1 / m, n_useful_point, endpoint=True, dtype=np.float32)
        * sampling_rate
    )
    return frequencies


def power_spectrum_after_fft(transformed: NDArray[np.complex_]) -> NDArray[np.float32]:
    """Power spectrum of FFT output `transformed`,
    Assuming `transformed` has length `m` that is a 2's power."""
    m = len(transformed)
    n_useful_point = (m >> 1) + 1
    useful_transformed = transformed[:n_useful_point]
    powers: NDArray[np.float32] = np.square(  # type: ignore
        useful_transformed.real, dtype=np.float32
    ) + np.square(useful_transformed.imag, dtype=np.float32)
    return powers


def powspec(
    samples: NDArray[np.float64], sr=8000, wintime=0.025, steptime=0.010
) -> NDArray[np.float32]:
    """
    Compute the powerspectrum and frame energy of the input signal.

    Each column represents a power spectrum for a given frame.
    Each row represents a frequency.
    """
    winpts = round(wintime * sr)
    steppts = round(steptime * sr)

    NFFT = 2 ** np.ceil(np.log2(winpts))
    WINDOW = scipy.signal.windows.hann(winpts, sym=False)
    NOVERLAP = winpts - steppts
    SAMPRATE = sr

    _, _, Sxx = spectrogram(
        samples, nfft=NFFT, fs=SAMPRATE, window=WINDOW, noverlap=NOVERLAP
    )

    return Sxx


@lru_cache(maxsize=8)
def filter_banks_from_frequencies(
    fft_size: int,
    n_useful_point: int,
    sampling_rate: int,
    n_bank: int,
):
    """Filter banks matrix for converting power spectrum into Mel spectrum."""

    # FIXME:
    # frequencies = frequencies_after_fft(fft_size, sampling_rate)
    frequencies = np.arange(fft_size // 2 + 1) / fft_size * sampling_rate
    maxfrq = sampling_rate / 2

    banks_matrix = np.zeros((n_bank, n_useful_point))

    maxmel = hz2mel(maxfrq)
    mel_frequencies = mel2hz(np.arange(n_bank + 2) / (n_bank + 1) * maxmel)

    for i in range(n_bank):
        local_frequences = mel_frequencies[i : i + 3]
        loslope = (frequencies - local_frequences[0]) / (
            local_frequences[1] - local_frequences[0]
        )
        hislope = (local_frequences[2] - frequencies) / (
            local_frequences[2] - local_frequences[1]
        )
        banks_matrix[i] = np.maximum(0, np.minimum(loslope, hislope))

    # Normalize each row
    row_sums = banks_matrix.sum(axis=1)
    banks_matrix = banks_matrix / row_sums[:, np.newaxis]

    return banks_matrix, mel_frequencies


def mel2hz(z):
    """Convert 'mel scale' frequencies into Hz."""
    z = np.asarray(z)
    f_0 = 0
    f_sp = 200 / 3
    brkfrq = 1000
    brkpt = (brkfrq - f_0) / f_sp
    logstep = np.exp(np.log(6.4) / 27)
    linpts = z < brkpt
    f = np.zeros_like(z).astype(np.float32)
    f[linpts] = f_0 + f_sp * z[linpts]
    f[~linpts] = brkfrq * np.exp(np.log(logstep) * (z[~linpts] - brkpt))

    return f


def hz2mel(f):
    """Convert frequencies f (in Hz) to mel 'scale'."""
    f_0 = 0
    f_sp = 200 / 3
    brkfrq = 1000
    brkpt = (brkfrq - f_0) / f_sp
    logstep = np.exp(np.log(6.4) / 27)
    linpts = f < brkfrq
    z = np.zeros_like(f).astype(np.float32)
    if linpts:
        z = (f - f_0) / f_sp
    else:
        z = brkpt + (np.log(f / brkfrq)) / np.log(logstep)

    return z


def spec2cep(spec, ncep=13):
    """
    Calculate cepstra from spectral samples via DCT.

    Each column represents a set of cepstral coefficients derived from a particular frame.
    Each row represents an individual cepstral coefficient.
    """
    nrow, ncol = spec.shape

    dctm = np.zeros((ncep, nrow))
    for i in range(ncep):
        dctm[i, :] = (
            np.cos((i - 1) * np.arange(nrow) / (nrow - 1) * np.pi)
            * 2
            / (2 * (nrow - 1))
        )
    dctm[:, [0, nrow - 1]] /= 2

    cep = np.dot(dctm, np.log(spec))
    return cep, dctm


def cep2spec(cep, nfreq=21):
    ncep, ncol = cep.shape

    dctm = np.zeros((ncep, nfreq))
    idctm = np.zeros((nfreq, ncep))

    for i in range(ncep):
        idctm[:, i] = 2 * np.cos((i - 1) * np.arange(nfreq) / (nfreq - 1) * np.pi)

    idctm[:, [0, ncep - 1]] = 0.5 * idctm[:, [0, ncep - 1]]

    spec = np.exp(np.matmul(idctm, cep))

    return spec, idctm


def mel_spectrum_from_powers(
    fft_size: int,
    power_spectrum: NDArray[np.float32],
    sampling_rate=SAMPLING_RATE,
    n_bank=40,
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    """
    Returns frequencies at filter bank center and Mel spectrum.
    """
    n_useful_point = len(power_spectrum)
    nfreqs = power_spectrum.shape[0]
    banks_matrix, mel_frequencies = filter_banks_from_frequencies(
        fft_size, n_useful_point, sampling_rate, n_bank
    )

    return mel_frequencies[1:-1], banks_matrix[:, :nfreqs] @ power_spectrum


def mel_spectrum(
    pspectrum: NDArray[np.float32], sr=8000, n_banks=40, fft_size=512
) -> NDArray[np.float32]:
    """
    Perform critical band analysis.
    Takes power spectrogram as input.

    Each column corresponds to a frame, and each row represents a critical band.
    """
    nfreqs = pspectrum.shape[0]
    m, _ = filter_banks_from_frequencies(fft_size, nfreqs, sr, n_banks)

    return m @ pspectrum


# TODO:
def mfcc_homebrew(
    audio_array: NDArray[np.int16],
    n_banks=40,
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    segmenter = Segmenter(SAMPLING_RATE * CHUNK_MS // MS_IN_SECOND)
    segmenter.add_sample(pre_emphasis(audio_array))
    mel_spectra = np.array([]).reshape(n_banks, 0)
    while (frame := segmenter.next()) is not None:
        windowed = window(frame)
        transformed = fast_fourier_transform(windowed)
        m = len(transformed)
        power_spectrum = power_spectrum_after_fft(transformed)
        mel_frequencies, mel_spectrum = mel_spectrum_from_powers(
            m, power_spectrum, n_bank=n_banks
        )
        # TODO: use frequencies
        mel_spectra = np.hstack((mel_spectra, mel_spectrum[:, np.newaxis]))
    assert len(mel_spectra) != 0
    cep = spec2cep(mel_spectra, ncep=13)
    return cep, mel_spectra


# TODO:
def mfcc(
    audio_array: NDArray[np.float32], sr=8000
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    audio_array = pre_emphasis(audio_array)
    pspec = powspec(audio_array, sr=sr)
    mspec = mel_spectrum(pspec, sr=sr)
    cep, _ = spec2cep(mspec, ncep=13)
    return cep, mspec
