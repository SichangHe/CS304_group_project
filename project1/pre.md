---
presentation:
  width: 1920
  height: 1080
---

<!-- slide -->

COMPSCI304 group project 1

<!-- slide -->

recording using callback function

```python
def stream_callback(
        in_data: bytes | None,
        n_frame: int,
        time_info: Mapping[str, float],
        status: int,
    ):
    """Callback for `PyAudio.open`. Send input audio data to `audio_queue`."""

with wave.open(out_file_name, "wb") as out_file, open_pyaudio() as py_audio:
    # Configure output file.
    # ...
    stream = py_audio.open(
        # ...
        stream_callback=stream_callback,
    )
```

<!-- slide -->

`Open in Browser`

<!-- slide -->
### classify a frame
```python
classify_frame(arr: NDArray[np.int16]) -> bool:
```
<!-- slide -->
### classify a frame: implementation

```python
def classify_frame(arr):
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