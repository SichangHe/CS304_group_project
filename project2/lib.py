import numpy as np
import scipy
from scipy.signal import spectrogram


def pre_emphasis(
    signal: np.ndarray[np.int16], alpha: float = 0.97
) -> np.ndarray[np.float64]:
    """Apply pre-emphasis to the input signal."""

    preemphasized_signal = np.zeros_like(signal)
    preemphasized_signal[0] = signal[0]
    for i in range(1, len(signal)):
        preemphasized_signal[i] = signal[i] - alpha * signal[i - 1]

    return preemphasized_signal


def window(samples: np.ndarray[np.float64], win_size: int) -> np.ndarray[np.float64]:
    """Applies a window function to the given audio signal."""
    pass


def powspec(
    samples: np.ndarray[np.float64], sr=8000, wintime=0.025, steptime=0.010
) -> np.ndarray[np.float64]:
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


def mel_spectrum(pspectrum: np.ndarray[np.float64]) -> np.ndarray[np.float64]:
    """
    Perform critical band analysis.
    Takes power spectrogram as input.

    Each column corresponds to a frame, and each row represents a critical band.
    """
    pass


def spec2cep(aspectrum: np.ndarray[np.float64]) -> np.ndarray[np.float64]:
    """
    Calculate cepstra from spectral samples via DCT.

    Each column represents a set of cepstral coefficients derived from a particular frame.
    Each row represents an individual cepstral coefficient.
    """
    pass
