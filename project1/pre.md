---
presentation:
  width: 1920
  height: 1080
---

<!-- slide -->

# COMPSCI 304 group project 1: Speech Endpointing

Steven Hé (Sīchàng), Luyao Wang

Instructor: Prof. Ming Li, Haoxu Wang

Duke Kunshan University

<!-- slide -->

### Contents

- Assumptions
- Implementation
- Demo

<!-- slide -->

### Assumptions

- Energy level $L$ is calculated as

  $$
  L:=10\log_{10}\left(\frac{1}{N}\sum_{i=1}^N x_i^2\right)\mathrm{dB}.
  $$

- The energy $L_s$ level when speaking is
  much higher than the energy level $L_b$ when not speaking

<!-- slide -->

We track `background` energy level and smoothened `level` energy level

- Speech off
  - Adjust `background` upwards weakly when the new energy level is higher,
  - Adjust it downwards strongly when the new energy level is lower.
- speech starts
  - We do not adjust `background` because we assume the high energy level cannot
    represent background noise.
  - Assume that `level` would be at least 15dB higher than `background` to **enter speech**
  - `level` would be at least 2dB higher than `background` **during speech**.
  - Energy measurement $L$ is relative

<!-- slide -->

### refinements

- Problem: If the environment is becomes noisy and background noise increases over 15dB during speech, the algorithm would not be able to detect when the speech stops.

- To combat this, we also track a `foreground` energy level, opposite to how `background` is measured and adjusted.
- Assumption: speech would become louder when background noise increases,
- Speech stops when `level` is at least 20dB lower than `foreground`.

<!-- slide -->

### Implementation

- Detect speech
- IO, recording and writing raw wav file

<!-- slide -->

### Detect speech

- Two tasks
  - classify a frame: speech/non-speech
    `def classify_frame(arr: NDArray[np.int16]) -> bool:`
  - recording states: `PENDING`, `GOING`, `STOPPING`, `STARTING`
    `def recording_status(is_speech: bool) -> RecordingStatus:`

<!-- slide -->

### classify a frame

```python
def classify_frame(arr: NDArray[np.int16]) -> bool:
    current = sample_decibel_energy(arr)

    if level is None:
        level = current
    if background is None:
        background = current

    level = ((level * FORGET_FACTOR) + current) / (FORGET_FACTOR + 1.0)

    if speaking:
        if level - background < CONTINUING_THRESHOLD_DB or level - foreground < STOPPING_THRESHOLD_DB:
            speaking = False
            background = min(background, level)
        else:
            foreground = adjust_conditionally_on_change(foreground, level, STRONG_ADJUSTMENT, WEAK_ADJUSTMENT)
    else:
        if level - background >= STARTING_THRESHOLD_DB:
            speaking = True
            foreground = level
        else:
            background = adjust_conditionally_on_change(background, level, WEAK_ADJUSTMENT, STRONG_ADJUSTMENT)

    return speaking
```

</br>

<!-- slide -->

### Recording states

```python
class RecordingStatus(Enum):
    """- `PENDING`: The recording has not started yet.
    - `GOING`: The recording is currently in progress.
    - `STOPPING`: The recording has been completed and should be stopped.
    - `STARTING`: The recording has just started."""

    PENDING = -1
    GOING = 0
    STOPPING = 1
    STARTING = 2
```

- We start in the `PENDING` state
- Switch to `STARTING` when the speech just starts.
  - Backtrack 100ms of audio to capture the potential consonant of the first word said
- Maintain the `GOING` state if the speech continues and keep recording
- Allow for at most 2s of non-speech audio before switching to `STOPPING` to accommodate for pauses during speech
  - The last 2s of silence in the recording is cut away.

<!-- ```python
def recording_status(is_speech: bool) -> RecordingStatus:
    if not started:
        if is_speech:
            started = True
            return RecordingStatus.STARTING
        return RecordingStatus.PENDING
    else:
        if is_speech:
            off_time = 0
        else:
            off_time += CHUNK_MS
    if off_time > MAX_PAUSE_MS:
        return RecordingStatus.STOPPING

    return RecordingStatus.GOING
``` -->

<!-- slide -->

### Recording using callback function

- We use a callback function from `get_stream_callback` to
  send input audio samples to the main thread through a `Queue`.
- Avoid audio input from blocking the main thread

```python
audio_queue: Queue[tuple[bytes, int]] = Queue()

def stream_callback(
        in_data: bytes | None,
        n_frame: int,
        time_info: Mapping[str, float],
        status: int,
    ):
    """Callback for `PyAudio.open`. Send input audio data to `audio_queue`."""
    audio_queue.put((in_data, n_frame))

    return None, paContinue

with wave.open(out_file_name, "wb") as out_file, open_pyaudio() as py_audio:
    # Configure output file.
    # ...
    stream = py_audio.open(
        # ...
        stream_callback=stream_callback,
    )
```

</br>

<!-- slide -->

### Writing to file

We use another thread to write to file

- Avoid file operations blocking the main thread
- Ready to write data is pushed to `write_queue`
  - Audio frames is pushed to `write_queue` according to recording states
- Another thread writes data in `write_queue` to wav file to avoid

<!-- slide -->

### Conclusion

- This project provided valuable insights into audio processing, raw file encoding, and speech detection techniques.
- The implementation of endpointing and the use of energy levels and thresholds proved to be effective in accurately identifying speech segments.
- Foundation for further exploration and development in the field of speech analysis and recognition

<!-- ### put it together

```python
audio_queue: Queue[tuple[bytes, int]] = Queue()
stream_callback = get_stream_callback(audio_queue)
write_queue: Queue[bytes | None] = Queue()

buffer = b""
pending_samples = b""

while True:
    data, _ = audio_queue.get(timeout=0.1)

    audio_array = np.frombuffer(data, dtype=np.int16)
    is_speech = classify_sample(audio_array)
    status = recording_status(is_speech)
    match status:
        case RecordingStatus.PENDING:
            pending_samples += data
            continue
        case RecordingStatus.STOPPING:
            break
        case RecordingStatus.STARTING:
            # Backtrack previous sample before recording starts.
            buffer += pending_samples[-SIZE_OF_BACKTRACK:]
            pending_samples = b""
    buffer += data
    if len(buffer) > SIZE_OF_SILENT_END:
        write_queue.put(buffer[:-SIZE_OF_SILENT_END])
        buffer = buffer[-SIZE_OF_SILENT_END:]
print("Stopping recording.")
```
-->
