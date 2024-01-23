import numpy as np
import scipy
from numpy.typing import NDArray
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


def window(samples: NDArray[np.float32], win_size: int) -> NDArray[np.float32]:
    """Applies a window function to the given audio signal."""
    pass


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
