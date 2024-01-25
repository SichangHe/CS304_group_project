---
presentation:
  width: 1920
  height: 1080
---

<!-- slide -->

# COMPSCI 304 group project 2: MFCC computation

Steven Hé (Sīchàng), Luyao Wang

Instructor: Prof. Ming Li, Haoxu Wang

Duke Kunshan University

<!-- slide -->

### Contents

- Implementation
  - Power spectrum calculation
  - Mel spectrum calculation
  - Mel cepstrum calculation
- Demo

<!-- slide -->

### Power spectrum calculation

- Preemphasis
- Segmenting audio and applying window function
- Fast Fourier transform

<!-- slide -->

### Preemphasis

- Reduce the influence of low-frequency components and enhance high-frequency components in a signal.
- Subtract a fraction of the previous sample from the current sample using the formula:

$$ s_{preemp}[n] = s[n] – \alpha s[n-1] $$

<!-- slide -->

### Segmenting audio and applying window function

- A segmenter to divide the collected audio signal into frames.
- Window size of 320. The segmenter moves by half the window size at each step, producing frames of size equal to the window size.
- This approach results in a 160-sample overlap between consecutive frames.

For windowing, the Hanning window function is utilized, defined by the formula:

$$ w[n]= \frac{1}{2}\left[1-\cos \left({\frac {2\pi n}{N}}\right)\right], 0\leq n\leq N$$

Overlapping frames capture the frequency components of the signal more frequently, allowing for a more detailed analysis of rapidly changing frequencies.

<!-- slide -->

### Fast Fourier transform

- Fast Fourier Transform (FFT) algorithm after preemphasis and the application of the window function to the overlapping frames.
- `scipy.fft.fft`
- In accordance with the Nyquist theorem, we only consider the first $ \frac{N\_{\text{FFT}}}{2} + 1 $ frequencies.
- Calculate the power spectrum.

<!-- slide -->

## Mel spectrum calculation

- We employ the Slaney-style mel scale calculation formula.
- A linear relationship with respect to Hz below 1000 Hz and transitions to a logarithmic relationship above 1000 Hz.

$$
{\displaystyle m(f)={\begin{cases}{\frac {3f}{200}}&f<1000\\15+27\log _{6.4}\left({\frac {f}{1000}}\right)&f\geq 1000\end{cases}}}
$$

We multiply the power spectrum by the Mel filter banks matrix to weight each power spectral value by the corresponding filter's value at that frequency.

<!-- slide -->

### Mel banks matrix for 40 filters

![banks_matrix](assets/banks_matrix.jpg "banks matrix")

<!-- slide -->

## Mel cepstrum calculation

- DCT-II matrix for Mel cepstrum calculation
- Multiply the DCT matrix with the Mel spectrum.
- Select the first 13 coefficients as the Mel Frequency Cepstral Coefficients (MFCCs).
- Inverse Discrete Cosine Transform (IDCT) to convert Mel cepstrum back to Mel spectrum.

$$
{\displaystyle X_{k}=\sum _{n=0}^{N-1}x_{n}\cos \left[\,{\tfrac {\,\pi \,}{N}}\left(n+{\tfrac {1}{2}}\right)k\,\right]\qquad {\text{ for }}~k=0,\ \dots \ N-1~.}
$$

<!-- slide -->

## Result

<div style="display: flex;">
    <img src="assets/seven2log_spectra40.png" alt="log mel spectrum of 'seven'" style="width: 36%;">
    <img src="assets/seven2cepstra40.png" alt="log mel spectrum of 'seven'" style="width: 36%;">
    <img src="assets/seven2idct40.png" alt="log mel spectrum of 'seven' reconstructed by IDCT" style="width: 34%;">
</div>

<!-- slide -->

# Demo
