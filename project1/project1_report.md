# Project 1 Report

<!-- TODO: Brief overview -->

In this project, we use PyAudio to record sound. Throughout the project, we delve into the fundamentals of raw audio file encoding and storage, as well as techniques for detecting active speech.

## Introduction

<!-- TODO: what is endpointing and how it works -->

In the `main.py` file, we utilize two import functions to detect active speech:

- `get_classify_sample`: This function takes a 20 ms frame as input and provides a Boolean value indicating whether it contains speech or not. We define speech as starting when the energy level (level) is at least `STARTING_THRESHOLD_DB` higher than the background energy. Speech is considered to continue when the energy level is at least `CONTINUING_THRESHOLD_DB` higher than the background energy and at least `STOPPING_THRESHOLD_DB` higher than the foreground energy.
- `get_recording_status`: This function operates above get_classify_sample and has three states:

  - State -1: Not started - indicates that recording has not yet begun.
  - State 0: Recording in progress - indicates that recording is currently ongoing.
  - State 1: Recording stopped - indicates that recording has ended.

  `get_recording_status` will not initiate recording (transition from state -1 to 0) until the first frame containing speech is detected by `get_classify_sample`. It allows for a maximum period of 2 seconds where no speech is detected. If no speech is detected beyond this time limit, `get_recording_status` will indicate that the recording has stopped.

## Implementation

- We use a callback function for PyAudio to send input audio data to the main
  thread with a `Queue`, so calculating the intensity of the audio and
  endpointing do not block or get blocked by the audio input processing.
- Calculated energy per 20ms in decibels using this:
- Maintain level, background, and foreground energy levels
- Thresholds to enter and exit speaking mode
- Timeout to accommodate for pauses in speech

## Testing

- Recording and manual inspection:
  During our testing phase, we conducted recordings using different tones on different devices to ensure compatibility across various platforms. This rigorous testing process aimed to verify that the program functions effectively on most devices.
- Visualization of the recorded audio and classification:
  To facilitate the analysis of recorded audio and its classification, we have developed a separate file named `test.py`. This file allows for the inspection of the audio spectrum and highlights specific regions that have been identified as active speech by the `get_classify_sample` function. This visualization feature aids in the evaluation and understanding of the program's speech detection capabilities.

## Conclusion

<!-- TODO: summary and takeaways -->

Overall, this project provided valuable insights into audio processing, raw file encoding, and speech detection techniques. The implementation of endpointing and the use of energy levels and thresholds proved to be effective in accurately identifying speech segments. This project serves as a foundation for further exploration and development in the field of speech analysis and recognition.
