import math
from functools import lru_cache

import numpy as np
import scipy
from numpy.typing import NDArray
from scipy import fft
from scipy.signal import spectrogram


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


def frequencies_n_power_spectrum(
    transformed: NDArray[np.complex_], sampling_rate: int
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    """Frequencies and power spectrum of FFT output `transformed`,
    Assuming `transformed` has length `m` that is a 2's power."""
    m = len(transformed)
    n_useful_point = (m >> 1) + 1
    frequencies: NDArray[np.float32] = (
        np.linspace(0, 1 / m, n_useful_point, endpoint=True, dtype=np.float32)
        * sampling_rate
    )

    useful_transformed = transformed[:n_useful_point]
    powers: NDArray[np.float32] = np.square(  # type: ignore
        useful_transformed.real, dtype=np.float32
    ) + np.square(useful_transformed.imag, dtype=np.float32)
    return frequencies, powers


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


def mel_spectrum(pspectrum: NDArray[np.float32]) -> NDArray[np.float32]:
    """
    Perform critical band analysis.
    Takes power spectrogram as input.

    Each column corresponds to a frame, and each row represents a critical band.
    """
    pass


def spec2cep(aspectrum: NDArray[np.float32]) -> NDArray[np.float32]:
    """
    Calculate cepstra from spectral samples via DCT.

    Each column represents a set of cepstral coefficients derived from a particular frame.
    Each row represents an individual cepstral coefficient.
    """
    pass
