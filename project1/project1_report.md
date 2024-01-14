# Project 1 Report

- We use a callback function for PyAudio to send input audio data to the main
    thread with a `Queue`, so calculating the intensity of the audio and
    endpointing do not block or get blocked by the audio input processing.
