We got an error:

```sh
steps/make_mfcc_pitch.sh: line 157: run.pl: command not found
```

This is because `run.pl` is not in the present directory or `$PATH`.
We solved this by replace it with `utils/parallel/run.pl` in `cmd.sh`.

`local/aishell_prepare_dict.sh` extracts the non-silence phones from
`lexicon.txt`, grouped by the same phones with different indexes.
It also prepares the (optional) silence phones and the extra questions that are
simply all the phones.
<!-- TODO: What is this extra questions? -->

`aishell_data_prep.sh` extracts the audio file names,
and split them into training, development, and testing sets. For each set,
it lists <!-- the file names without the `.wav` extension in `utt.list`, -->
the map from utterance IDs to speaker IDs in `utt2spk` and the other way around
in `spk2utt`, the map from utterance IDs to `.wav` file paths in `wav.scp`,
and map from utterance IDs to transcriptions in `transcripts.txt` (and
deduplicated in `text`).
