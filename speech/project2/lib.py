import math
from functools import lru_cache

import numpy as np
import scipy
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import NDArray
from scipy import fft
from scipy.signal import spectrogram

from speech.project1 import CHUNK_MS, MS_IN_SECOND, SAMPLING_RATE


def pre_emphasis(signal: NDArray, alpha: float = 0.95) -> NDArray[np.float32]:
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


@lru_cache(maxsize=2)
def frequencies_after_fft(fft_size: int, sampling_rate: int) -> NDArray[np.float32]:
    """Frequencies of FFT output of length `fft_size`, a 2's power."""
    n_useful_point = (fft_size >> 1) + 1
    return sampling_rate / fft_size * np.arange(n_useful_point, dtype=np.float32)


def power_spectrum_after_fft(transformed: NDArray[np.complex_]) -> NDArray[np.float32]:
    """Power spectrum of FFT output `transformed`,
    Assuming `transformed` has length `m` that is a 2's power."""
    m = len(transformed)
    n_useful_point = (m >> 1) + 1
    useful_transformed = transformed[:n_useful_point]
    powers: NDArray[np.float32] = np.square(  # type: ignore
        useful_transformed.real, dtype=np.float32
    ) + np.square(useful_transformed.imag, dtype=np.float32)
    return powers / m


def powspec(
    samples: NDArray, sr=8000, wintime=0.025, steptime=0.010
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

    frequencies = frequencies_after_fft(fft_size, sampling_rate)
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

    return banks_matrix


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


INVERSE_ROOT_TWO = 1 / np.sqrt(2)

N_MFCC_COEFFICIENTS = 13


def spec2cep(spec, ncep=N_MFCC_COEFFICIENTS):
    """
    Calculate cepstra from spectral samples via DCT.

    Each column represents a set of cepstral coefficients derived from a particular frame.
    Each row represents an individual cepstral coefficient.
    """
    nrow = spec.shape[0]

    i = np.arange(ncep)
    dctm = np.cos(
        (i[:, np.newaxis] - 1) * np.arange(1, 2 * nrow, 2) / (2 * nrow) * np.pi
    ) * np.sqrt(2 / nrow)
    dctm[0, :] *= INVERSE_ROOT_TWO

    cep = np.dot(dctm, np.log(spec))
    return cep, dctm


def cep2spec(cep, nfreq=40):
    ncep = cep.shape[0]

    i = np.arange(ncep)
    dctm = np.cos(
        (i[:, np.newaxis] - 1) * np.arange(1, 2 * nfreq, 2) / (2 * nfreq) * np.pi
    ) * np.sqrt(2 / nfreq)

    dctm[0, :] *= INVERSE_ROOT_TWO
    idctm = dctm.T

    spec = np.exp(np.dot(idctm, cep))

    return spec, idctm


def mel_spectrum_from_powers(
    fft_size: int,
    power_spectrum: NDArray[np.float32],
    sampling_rate=SAMPLING_RATE,
    n_bank=40,
) -> NDArray[np.float32]:
    """
    Returns frequencies at filter bank center and Mel spectrum.
    """
    n_useful_point = len(power_spectrum)
    banks_matrix = filter_banks_from_frequencies(
        fft_size, n_useful_point, sampling_rate, n_bank
    )

    return banks_matrix @ power_spectrum


def mel_spectrum(
    pspectrum: NDArray[np.float32], sr=8000, n_banks=40, fft_size=512
) -> NDArray[np.float32]:
    """
    Perform critical band analysis.
    Takes power spectrogram as input.

    Each column corresponds to a frame, and each row represents a critical band.
    """
    nfreqs = pspectrum.shape[0]
    m = filter_banks_from_frequencies(fft_size, nfreqs, sr, n_banks)

    return m @ pspectrum


def mel_spectrum_from_frame(
    frame: NDArray[np.float32], n_filter_banks: int
) -> NDArray[np.float32]:
    windowed = window(frame)
    transformed = fast_fourier_transform(windowed)
    m = len(transformed)
    power_spectrum = power_spectrum_after_fft(transformed)
    return mel_spectrum_from_powers(m, power_spectrum, n_bank=n_filter_banks)


def mel_spectrum_and_cepstrum_from_frame(
    frame: NDArray[np.float32], n_filter_banks: int, ncep=N_MFCC_COEFFICIENTS
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    mel_spectrum = mel_spectrum_from_frame(frame, n_filter_banks)
    cepstrum, _ = spec2cep(mel_spectrum, ncep=ncep)
    return mel_spectrum, cepstrum


class RunningMeanVariance:
    """For normalizing Mel cepstra on-the-fly using the current running mean
    and variance."""

    mean: NDArray[np.float32]
    variance: NDArray[np.float32]
    n: int

    def __init__(self, n_features: int):
        self.mean = np.zeros(shape=(n_features,), dtype=np.float32)
        self.variance = np.ones(shape=(n_features,), dtype=np.float32)
        self.n = 0

    def normalize_and_update(self, new_sample: NDArray[np.float32]):
        """Normalize `new_sample` in place so it has 0 mean and 1 standard
        deviation, and update `self`'s mean and variance."""
        assert new_sample.shape == self.mean.shape
        self.mean = (self.n * self.mean + new_sample) / (self.n + 1)
        np.subtract(new_sample, self.mean, out=new_sample)
        self.variance = (self.n * self.variance + np.square(new_sample)) / (self.n + 1)
        if self.variance.any() > 0:
            np.divide(new_sample, np.sqrt(self.variance), out=new_sample)
        self.n += 1
        return new_sample


def derive_cepstrum_velocities(cepstrum: NDArray[np.float32]) -> NDArray[np.float32]:
    """Derive the delta and delta delta value of `cepstrum`."""
    cepstrum = np.atleast_2d(cepstrum)

    padded_cepstrum = np.pad(cepstrum, ((0, 0), (1, 1)), mode="edge")
    delta = padded_cepstrum[:, 2:] - padded_cepstrum[:, :-2]
    padded_delta = np.pad(delta, ((0, 0), (1, 1)), mode="edge")
    delta_delta = padded_delta[:, 2:] - padded_delta[:, :-2]

    result = np.hstack((cepstrum, delta, delta_delta))
    return result.squeeze()


def normalize_cepstrum(cepstrum: NDArray[np.float32]) -> NDArray[np.float32]:
    """Normalize `cepstrum` in place to have 0 mean and 1 standard deviation in
    each column."""
    cepstrum_t = cepstrum.T
    np.subtract(cepstrum_t, np.mean(cepstrum_t, axis=0), out=cepstrum_t)
    np.divide(cepstrum_t, np.std(cepstrum_t, axis=0), out=cepstrum_t)
    return cepstrum


class RunningMFCC:
    def __init__(self, n_filter_banks=40, n_mfcc_coefficients=N_MFCC_COEFFICIENTS):
        self.n_filter_banks = n_filter_banks
        self.n_mfcc_coefficients = n_mfcc_coefficients
        self.segmenter = Segmenter(SAMPLING_RATE * CHUNK_MS // MS_IN_SECOND)
        self.mel_spectra = []
        self.cepstra = []
        self.running_mean_variance = RunningMeanVariance(n_mfcc_coefficients)

    def add_sample(self, sample: NDArray[np.float32]):
        """The Mel spectra and cepstra returned have each row corresponding to
        each segment."""
        mel_spectra = []
        cepstra = []
        self.segmenter.add_sample(pre_emphasis(sample))
        while (frame := self.segmenter.next()) is not None:
            mel_spectrum, cepstrum = mel_spectrum_and_cepstrum_from_frame(
                frame, self.n_filter_banks, self.n_mfcc_coefficients
            )
            cepstrum = self.running_mean_variance.normalize_and_update(cepstrum)
            mel_spectra.append(mel_spectrum)
            cepstra.append(cepstrum)
        self.mel_spectra.extend(mel_spectra)
        self.cepstra.extend(cepstra)
        return np.atleast_2d(np.asarray(cepstra)), np.atleast_2d(
            np.asarray(mel_spectra)
        )


def mfcc_homebrew(
    audio_array: NDArray, n_filter_banks=40, n_mfcc_coefficients=N_MFCC_COEFFICIENTS
):
    """The Mel spectra and cepstra returned have each row corresponding to each
    segment."""
    segmenter = Segmenter(SAMPLING_RATE * CHUNK_MS // MS_IN_SECOND)
    segmenter.add_sample(pre_emphasis(audio_array))
    mel_spectra = []
    cepstra = []
    while (frame := segmenter.next()) is not None:
        mel_spectrum, cepstrum = mel_spectrum_and_cepstrum_from_frame(
            frame, n_filter_banks, n_mfcc_coefficients
        )
        mel_spectra.append(mel_spectrum)
        cepstra.append(cepstrum)
    mel_spectra_np = np.asarray(mel_spectra)
    return np.asarray(cepstra), normalize_cepstrum(mel_spectra_np)


def mfcc(audio_array: NDArray, sr=8000):
    pre_emphasized = pre_emphasis(audio_array)
    pspec = powspec(pre_emphasized, sr=sr)
    mspec = mel_spectrum(pspec, sr=sr)
    cep, _ = spec2cep(mspec, ncep=13)
    return cep, mspec, pspec


def plot_log_mel_spectra(
    mel_spectrum_matrix: NDArray[np.float32], title="Log Mel Spectrum"
) -> Figure:
    """
    Plot log mel spectra.

    Each column of input matrix represents a feature vector of size equal to the number of mel filter banks of a frame.
    Each row of input matrix corresponds to a frequency.
    """
    log_mel_spectrum_matrix = np.log(mel_spectrum_matrix)
    ax: Axes
    fig, ax = plt.subplots()
    ax.imshow(log_mel_spectrum_matrix, cmap="hsv")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Dimension")
    ax.set_title(title)
    ax.invert_yaxis()

    return fig


def plot_cepstra(ceptra_matrix: NDArray[np.float32], title="Mel Cepstrum") -> Figure:
    """
    Plot cepstra.

    Each column of input matrix represents a feature vector of size equal to the number of features for cepstra (typically 13).
    Each row of input matrix corresponds to a feature after applying DCT.
    """
    ax: Axes
    fig, ax = plt.subplots()
    ax.imshow(derive_cepstrum_velocities(ceptra_matrix).T, cmap="hsv")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Dimension")
    ax.set_title(title)
    ax.invert_yaxis()

    return fig


def lifting(cepstra, lift=0.6):
    liftwts = np.concatenate(([1], np.arange(1, cepstra.shape[0]) ** lift))
    y = np.diag(liftwts) @ cepstra
    return y
