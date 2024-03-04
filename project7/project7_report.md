We got an error:

```sh
steps/make_mfcc_pitch.sh: line 157: run.pl: command not found
```

This is because `run.pl` is not in the present directory or `$PATH`.
We solved this by replace it with `utils/parallel/run.pl` in `cmd.sh`.
