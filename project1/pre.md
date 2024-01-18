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

### Assumptions

- Energy level $L$ is calculated as

  $$
  L:=10\log_{10}\left(\frac{1}{N}\sum_{i=1}^N x_i^2\right)\mathrm{dB}.
  $$

- the energy $L_s$ level when speaking is
  much higher than the energy level $L_b$ when not speaking

<!-- slide -->

we track `background` energy level and smoothened `level` energy level

- speech off
  - adjust `background` upwards weakly when the new energy level is higher,
    and adjust it downwards strongly when the new energy level is lower.
- speech starts
  - we do not adjust `background` because we assume the high energy level cannot
    represent background noise.
  - we assume that `level` would be at least 15dB higher than `background` to **enter speech**
  - `level` would be at least 2dB higher than `background` **during speech**.
  - energy measurement $L$ is relative

<!-- slide -->

- problem: If the background noise increases over 15dB during speech,
  the algorithm would not be able to detect when the speech stops.

- To combat this, we also track a `foreground` energy level, opposite to how `background` is measured and adjusted.
- Assumption: speech would become louder when background noise increases,
- we assume it stops when `level` is at least 20dB lower than `foreground`.
- This mechanism can trigger can sound energy has a very sharp drop

<!-- slide -->

### recording using callback function

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

### recording status

```python
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
```

</br>

<!-- slide -->

### clipping

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

</br>

<!-- slide -->

### put it together

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