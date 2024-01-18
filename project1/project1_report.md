# Project 1 Report

Speech endpoint detection, or endpointing, is the first preparation step before
audio signal can be processed to recognize speech.
In this project, we record audio from computer microphones,
apply endpointing based on its energy level,
and write the speech portion into audio files.
We delve into the fundamentals of raw audio file encoding and storage,
as well as techniques for detecting active speech.

## Audio Recording

We use [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/docs/) to
obtain audio input from the computers' microphone.
To avoid audio input from blocking the main thread,
we use a callback function from `get_stream_callback` to
send input audio samples to the main thread through a `Queue`.
The samples have 16-bit resolution, mono channel, a sampling rate of 16kHz,
and a duration of 20ms.

We start the audio stream when the program starts,
and discard at least 5 audio samples using `discard_first_at_least` to
avoid the initial unstable samples that interfered with our speech detection.
When the user "hits" <kbd>↵</kbd>,
we discard all previous audio samples and start speech detection and recording.

## Speech Detection

Our baseline assumption is that the energy $L_s$ level when speaking is
much higher than the energy level $L_b$ when not speaking.
Here, given audio sample frames $\vec x$ of length $N$,
the energy level $L$ is calculated as

$$
L:=10\log_{10}\left(\frac{1}{N}\sum_{i=1}^N x_i^2\right)\mathrm{dB}.
$$

To distinguish speech from background noise,
while accommodating for fluctuations in the overall energy level,
we implemented `get_classify_sample` to track a `background` energy level and
a smoothened `level` energy level.
When speech is off,
since `background` should track the lower end of the energy level,
we only adjust it upwards weakly when the new energy level is higher,
and adjust it downwards strongly when the new energy level is lower.
During speech,
we do not adjust `background` because we assume the high energy level cannot
represent background noise.

When speech starts,
we assume that `level` would be at least 15dB higher than `background`,
and it would be at least 2dB higher than `background` during speech.
We use these assumptions to enter and exit speech.
This would work with different general volume levels because
our energy measurement $L$ is relative.

If the background noise increases over 15dB during speech,
the algorithm would not be able to detect when the speech stops.
To combat this, we also track a `foreground` energy level,
opposite to how `background` is measured and adjusted.
Using the assumption that speech would become louder when
background noise increases,
we assume it stops when `level` is at least 20dB lower than `foreground`.
Note that this mechanism is usually not triggered any more after
we started to discard the initial unstable audio samples.

## Recording

Based on our speech detection,
we decide when to start and stop the recording.
Our general goal is to include all of the speech portions with
minimal silence around them.

The general control flow of the recording process is implemented in
`get_recording_status`,
with states represented in enum `RecordingStatus`.
We start in the `PENDING` state,
and switch to `STARTING` when the speech just starts.
Here, we backtrack 100ms of audio to capture the potential consonant of
the first word said,
which typically does not trigger the speech detection to start.
We then maintain the `GOING` state if the speech continues and keep recording.
To accommodate for pauses during speech,
we allow for at most 2s of non-speech audio before switching to `STOPPING`.
The last 2s of silence in the recording is cut away.

We write all recorded audio samples into a `.wav` file using
Python's `wave` module.
To avoiding file operations blocking the main thread,
we spawn a `Thread` run `frame_writing_thread`,
which writes audio samples rec received from `byte_queue` into the file .

## Testing

In our testing phase, we recorded audio using various tones on different devices. This comprehensive testing aimed to ensure compatibility across a range of platforms, validating that the program operates effectively on most devices.

For the analysis of the recorded audio and its classification, we created a separate file called `test.py`. This file facilitates the examination of the audio spectrum and emphasizes specific regions identified as active speech by the `get_classify_sample` function. The visualization feature provided by this file is instrumental in evaluating and comprehending the speech detection capabilities of the program.

## Conclusion

Overall, this project provided valuable insights into audio processing, raw file encoding, and speech detection techniques. The implementation of endpointing and the use of energy levels and thresholds proved to be effective in accurately identifying speech segments. This project serves as a foundation for further exploration and development in the field of speech analysis and recognition.
