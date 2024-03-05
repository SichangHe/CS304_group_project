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

`local/aishell_prepare_dict.sh` produces the dictionary in `data/local/dict/`,
an intermediate artifact later used to generate the language data.
It extracts the non-silence phones from
`~/AISHELL-1/resource_aishell/lexicon.txt` into `nonsilence_phones.txt`,
with the variances of the same base phones (phones with different indexes)
grouped in each line and the base phones sorted alphabetically.
It also prepares the (optional) silence phones in (`optional_silence.txt` and)
`silence_phones.txt`. The extra questions for constructing the decision tree,
simply a list of all the phone groups, are extracted into `extra_questions.txt`.
These extra questions are useful to group the same phone together when
constructing the decision tree later.

`aishell_data_prep.sh` extracts the audio file names and other related
information from `wav/` and `transcript/` in `~/AISHELL-1/data_aishell/`,
and splits them into training (`train/`), development (`dev/`),
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

`utils/prepare_lang.sh` constructs the pronunciation lexicon WFST ($L$)
and other information about the phone set in `data/lang/`,
based on the dictionary in `data/local/dict/`.
It first validates the files in `data/local/dict/` have correct encodings,
format, and matching phones.
It then converts the dictionary files from using phone names to using integers
so that the data can be processed using OpenFST. It executes several
intermediate steps, including adding position markers (`_B`, `_E`, `_I`, `_S`)
for word-internal positions in the extra questions,
adding disambiguation symbols, creating phone/word symbol table,
adding word boundary information, and silence handling. Eventually,
it produces the $L$ WFST at `L.fst`, the out-of-vocabulary (OOV)
word at `oov.txt`, the HMM topology at `topo`,
together with all the phone information at `phone/`.

## Feature Extraction

<!-- TODO: -->

<!-- TODO: `steps/make_mfcc_pitch.sh` -->

The script `steps/make_mfcc_pitch.sh` is used to compute MFCC (Mel Frequency Cepstral Coefficients) and pitch feature vectors. The data is divided into three groups: train, test, and dev.

Here's an overview of the steps performed by the script:

1. The `compute-mfcc-feats` command is used to compute MFCC features from the input audio data.
2. The `compute-kaldi-pitch-feats` command is used to compute pitch features from the input audio data.
3. The `paste-feats` command is used to combine the MFCC and pitch features into a single feature representation.
4. The `copy-feats` command is used to save the combined features to the directory specified by the `$mfcc_pitch_dir` variable in binary format.

The script generates `.scp` text files that map utterance IDs to positions in an archive `.ark` file. These files store the paths to the binary feature archives along with their associated utterance IDs.

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

To generate a human-readable format of the MFCC and pitch feature vectors associated with the feats.scp file, we use the `copy-feats` command with the `ark,t:-` option. This command reads the feature archives specified in the `feats.sc`p file and outputs the features in plain text format.

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

`local/aishell_train_lms.sh` trains a 3-gram language model in the ARPA format
in `data/local/lm/3gram-mincount/lm_unpruned.gz` using the transcript
(`data/local/train/text`) and the lexicon (`data/local/dict/lexicon.txt`).
After cleaning the transcript, it counts the occurrences of each word,
use this information to construct a unigram, and construct a word map.
It then calls `train_lm.sh` to train the language model with the output in the
ARPA format.

`utils/format_lm.sh` converts `data/local/lm/3gram-mincount/lm_unpruned.gz`,
a language model in the ARPA format,
into a WFST in the OpenFst format at `data/lang_test/G.fst`.
This is the language model WFST ($G$).

`steps/train_mono.sh` trains a monophone acoustic model in `exp/mono/` from the
training data set in `data/train/` to bootstrap the HMM WFST model ($H$).
It uses the delta features of the MFCC features to encapsulate time derivatives,
and normalizes the features to have zero mean and unit variance per speaker to
remove the influence of specific recording environment.
It creates a trivial decision tree
([reference](https://www.kaldi-asr.org/doc/tree_externals.html)).
It initializes GMMs based on the topology, the $L$ WFST,
and other phone information in `data/lang/`.
It then trains the GMMs iteratively by aligning the training data against the
model and increasing the number of Gaussians gradually,
and repeats this process for a fixed number (40) of rounds.
The resulting bootstrap HMM WFST model ($H$) is at `exp/mono/final.mdl`.

`steps/train_deltas.sh` trains a triphone acoustic model in `exp/triN/` from the
model and alignment produced in the last round.
It builds the decision tree for the acoustic model at `exp/triN/tree` after
collecting questions by phone clustering.
It then initializes the training graphs,
and iteratively increases the number of Gaussians in a fixed number of
iterations. The resulting HMM WFST model ($H$) is at `exp/triN/final.mdl`.

<!-- TODO: `steps/train_lda_mllt.sh` -->

<!-- TODO: `steps/train_lda_mllt.sh` -->

<!-- TODO: `steps/train_sat.sh` -->

## Model Testing

<!-- TODO:
you need to describe in detail the evaluation criteria for the test section. -->

The script `utils/mkgraph.sh` creates a fully expanded decoding graph $ H \circ C \circ L \circ G $. The output is a Finite State Transducer that has `word-ids` on the output, and `transition-ids` on the input that resolve to pdf-ids.

Kaldi reference <https://kaldi-asr.org/doc/graph_recipe_test.html>

There are five steps invloved.

1. Preparing $ L \circ G $:

    $ L $ and $ G $ FSTs are generated in `utils/prepare_lang.sh` and `utils/format_lm.sh` respectively. $ L \circ G $ is generated in the following command:

    ```sh
    fsttablecompose data/L_disambig.fst data/G.fst | \
    fstdeterminizestar --use-log=true | \
    fstminimizeencoded | fstpushspecial > somedir/LG.fst
    ```

    The command `fsttablecompose` is used to compose the FSTs `L_disambig.fst` and `G.fst`. Subsequently, `fstdeterminizestar` and `fstminimizeencoded` are employed for determinization and minimization respectively. The weight is then pushed using `fstpushspecial`, resulting in the final `LG.fst`.

2. Prepare $ C \circ L \circ G $:

    The context transducer $ C $ is constructed to prepare $ C \circ L \circ G $. In the triphone case, the $ C $ transducer transduces a triphone sequence into a phone sequence. The following command is used to create $ C $:

    ```sh
    fstmakecontextfst --read-disambig-syms=$dir/disambig_phones.list \
    --write-disambig-syms=$dir/disambig_ilabels.list data/phones.txt $subseq_sym \
    $dir/ilabels > $dir/C.fst
    ```

    In this command, the command takes as input the list of disambiguation symbols for reading and writing, along with the phone symbol table. The command writes label information and generates `C.fst`.

    However, it's worth noting that the command `fstmakecontextfst` is inefficient. Instead, it is recommended to use `fstcomposecontext` for dynamic composition of $ C $. The following command performs the composition of $ C $ with the $ L \circ G $ from the previous step (`LG.fst`) to generate $ C \circ L \circ G $ without explicitly creating $ C $:

    ```sh
    fstcomposecontext  --read-disambig-syms=$dir/disambig_phones.list \
    --write-disambig-syms=$dir/disambig_ilabels.list \
    $dir/ilabels < $dir/LG.fst >$dir/CLG.fst
    ```

3. Making the $ H $ transducer:

    $ H $ tranducer tranduces input speech features to context-dependent phones. In the Kaldi script, $ H $ is created without self-loops and represents context-dependent phones on its output and `transition-ids` on its input. The `transition-ids` encode information such as the `pdf-id` (acoustic state in Kaldi terminology) and phone. Each transition-id can be mapped to a `pdf-id`.

    The transitions for context-dependent phones lead to structures representing the corresponding HMMs and then back to the start state. For the normal topology, the $ H $ transducer includes self-loops on the initial state for each disambiguation symbol.

    It takes two inputs: `$tree`, which contains the mapping from the phone-in-context and HMM state to `pdf-id`, and the `$model` file that contains the HMM parameters generated in steps such as `train_mono.sh` or `train_deltas.sh`. The following command produces `Ha.fst`, which represents $ H $ without self-loops.

    ```sh
    make-h-transducer --disambig-syms-out=$dir/disambig_tstate.list \
    --transition-scale=1.0  $dir/ilabels.remapped \
    $tree $model  > $dir/Ha.fst
    ```

4. Making $ H \circ C \circ L \circ G $

    In order to create the final graph $ H \circ C \circ L \circ G $, the first step involves constructing $ H \circ C \circ L \circ G $ without self-loops. The corresponding command in our script is:

    ```sh
    fsttablecompose $dir/Ha.fst $dir/CLG.fst | \
    fstdeterminizestar --use-log=true | \
    fstrmsymbols $dir/disambig_tstate.list | \
    fstrmepslocal | fstminimizeencoded > $dir/HCLGa.fst
    ```

    The script removes the disambiguation symbols and any easy-to-remove epsilons, before minimizing.

5. Adding self-loops to $ H \circ C \circ L \circ G $

    The next step involves adding self-loops to $ H \circ C \circ L \circ G $ using the following command:

    ```sh
    add-self-loops --self-loop-scale=0.1 \
    --reorder=true $model < $dir/HCLGa.fst > $dir/HCLG.fst
    ```

These 5 steps generates a fully expanded decoding graph $ H \circ C \circ L \circ G $.

<!-- TODO: `steps/align_si.sh` -->

<!-- TODO: `steps/align_fmllr.sh` -->
