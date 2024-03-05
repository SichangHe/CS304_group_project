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

The script `steps/make_mfcc_pitch.sh` is used to compute MFCC (Mel Frequency Cepstral Coefficients) feature vectors. The data is divided into three groups: train, test, and dev.

The script outputs `.scp` text files, which map utterance ids to positions in an archive `.ark` files.

Sample from `data/train/feats.scp`:

```sh
$ cat data/train/feats.scp | head
BAC009S0002W0122 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:17
BAC009S0002W0123 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:9751
BAC009S0002W0124 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:16077
BAC009S0002W0125 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:24867
BAC009S0002W0126 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:30073
BAC009S0002W0127 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:34335
BAC009S0002W0128 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:43893
BAC009S0002W0129 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:49451
BAC009S0002W0130 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:59409
BAC009S0002W0131 /home/vcm/project7/aishell/s5/mfcc/raw_mfcc_pitch_train.1.ark:66151
```

The following command generates the MFCC feature vector associated with the `feat.scp` file a human-readable format:

```sh
$ copy-feats scp:data/train/feats.scp ark,t:- | head       
copy-feats scp:data/train/feats.scp ark,t:- 
BAC009S0002W0122  [
  37.84496 -15.14622 3.756182 -2.972847 6.935344 12.57643 22.11652 14.48858 0.718733 0.7420206 18.16019 21.15484 7.724125 -0.06633668 0.4676766 -0.02282783 
  36.68964 -16.39552 7.314747 3.214192 7.510836 5.319103 6.638824 3.424962 -4.242895 3.918768 6.590599 5.534946 7.724125 0.1134963 0.4676766 0.01054308 
  37.15177 -17.64481 5.535464 4.828202 6.474951 13.06025 16.98447 12.27586 5.764622 8.439523 16.42476 14.97698 4.688538 0.1055037 0.4676766 0.006692588 
  38.53815 -15.77087 3.546854 2.541688 7.741032 13.06025 13.77376 6.744049 8.918303 2.941307 3.94787 9.178222 9.096274 0.09351488 0.4676766 0.007976085 
  37.6139 -15.77087 1.034926 -8.352882 3.137099 14.51172 27.67624 12.27586 4.187781 3.674402 11.21844 13.55132 8.4102 -0.02637379 0.4676766 -0.0754512 
  37.38284 -15.14622 6.791429 1.869184 10.96379 15.96318 21.26118 0.3899403 -0.5486126 5.262775 7.169078 3.192841 1.696813 0.09351488 0.4549765 -0.04208028 
  40.61772 -19.51876 -4.839973 1.33118 10.84869 6.770569 24.25487 -9.696909 8.287566 12.17859 4.27668 6.185532 3.043089 0.1174926 0.4549765 -0.07031721 
  40.61772 -18.26946 4.070173 6.307713 5.78436 3.383816 21.26118 -9.467663 5.449254 5.751506 -6.080819 26.38225 18.35828 0.1374741 0.4549765 0.01311007 
  37.6139 -17.64481 -0.8490195 -4.99036 4.403181 14.0279 15.20074 7.850411 7.026094 1.352933 6.012119 9.048104 6.034813 -0.08631812 0.4549765 -0.009992868
```

The utterance id `BAC009S0002W0122` in the output above matches the first id in `data/train/feats.scp`.

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

## Model Testing

<!-- TODO:
you need to describe in detail the evaluation criteria for the test section. -->

<!-- TODO: `utils/mkgraph.sh` -->

<!-- TODO: `steps/align_si.sh` -->

<!-- TODO: `steps/align_fmllr.sh` -->
