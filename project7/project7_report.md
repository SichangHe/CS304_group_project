# Project 7 Report

## Errors Encountered

We got an error:

```sh
steps/make_mfcc_pitch.sh: line 157: run.pl: command not found
```

This was because `run.pl` is not in the present directory or `$PATH`.
We solved this by replace it with `utils/parallel/run.pl` in `cmd.sh`.

We got another error:

```sh
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
```

This was because we did not copy the symbolic links in `kaldi/egs/wsj/s5`.
The problem was solved after we did that.

## Data Preparation

<!-- TODO: local folder contains the code related to data preparation,
and you need to explain the codes in details. -->

Reference: <https://www.kaldi-asr.org/doc/data_prep.html>.

Our data are downloaded into `~/AISHELL-1/` from <www.openslr.org/resources/33>.

`local/aishell_prepare_dict.sh` produces the dictionary in `data/local/dict`,
an intermediate artifact later used to generate the language data.
It extracts the non-silence phones from `lexicon.txt` into
`nonsilence_phones.txt`,
grouped by the same phones with different indexes and sorted alphabetically.
It also prepares the (optional) silence phones in (`optional_silence.txt` and)
`silence_phones.txt`. The extra questions, simply all the phones,
are extracted into `extra_questions.txt`.
<!-- TODO: What is this extra questions? -->

`aishell_data_prep.sh` extracts the audio file names and other related
information from `data_aishell/wav/` and `data_aishell/transcript` in
`~/AISHELL-1/`, and splits them into training (`train/`), development (`dev/`),
and testing (`test/`) sets under `data/local/`.
It first dumps all `.wav` file names and dump them into
`data/local/tmp/wav.flist` and validates the count.
It then splits the file names into the three sets based on the file names and
creates separate `wav.flist` for each set. For each set,
it lists the file names without the `.wav` extension (the utterance IDs)
in `utt.list`,
the map from utterance IDs to IDs of their speakers in `utt2spk` and the other
way around in `spk2utt`,
the map from utterance IDs to `.wav` file paths in `wav.scp`,
and map from utterance IDs to their transcriptions in `transcripts.txt` (and
deduplicated in `text`). It filters out any instances not included,
and eventually produces the three sets containing `spk2utt`, `utt2spk`,
`wav.scp` and `text` in `data/`.

`utils/prepare_lang.sh` constructs the $L$ FST based on the output of
`local/aishell_prepare_dict.sh`.

## Feature Extraction

<!-- TODO: -->

<!-- TODO: `steps/make_mfcc_pitch.sh` -->

<!-- TODO: `steps/compute_cmvn_stats.sh` -->

## Acoustic Model Training

<!-- TODO:
the introduction to the model training script does not need to go into
specifics,
whereas you need to pay efforts in explaining the concepts related to the
current training step. -->

<!-- TODO: `utils/format_lm.sh` -->

<!-- TODO: `local/aishell_train_lms.sh` -->

<!-- TODO: `steps/train_mono.sh` -->

<!-- TODO: `steps/train_deltas.sh` -->

<!-- TODO: `steps/train_lda_mllt.sh` -->

<!-- TODO: `steps/train_lda_mllt.sh` -->

<!-- TODO: `steps/train_sat.sh` -->

<!-- TODO: `steps/align_*.sh` -->

<!-- TODO: `utils/mkgraph.sh` -->

## Model Testing

<!-- TODO:
you need to describe in detail the evaluation criteria for the test section. -->
