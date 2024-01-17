# Project 1 Report

<!-- TODO: Brief overview -->

## Introduction

<!-- TODO: what is endpointing and how it works -->

## Implementation

- We use a callback function for PyAudio to send input audio data to the main
    thread with a `Queue`, so calculating the intensity of the audio and
    endpointing do not block or get blocked by the audio input processing.
- Calculated energy per 20ms in decibels using this:
- Maintain level, background, and foreground energy levels
- Thresholds to enter and exit speaking mode
- Timeout to accommodate for pauses in speech

## Testing

- Recording and manual inspection
- Visualization of the recorded audio and classification

## Conclusion

<!-- TODO: summary and takeaways -->
