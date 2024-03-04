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

Output:

```
local/aishell_prepare_dict.sh: AISHELL dict preparation succeeded
```

`aishell_data_prep.sh` extracts the audio file names,
and split them into training, development, and testing sets. For each set,
it lists <!-- the file names without the `.wav` extension in `utt.list`, -->
the map from utterance IDs to speaker IDs in `utt2spk` and the other way around
in `spk2utt`, the map from utterance IDs to `.wav` file paths in `wav.scp`,
and map from utterance IDs to transcriptions in `transcripts.txt` (and
deduplicated in `text`).

Output:

```
Preparing data/local/train transcriptions
Preparing data/local/dev transcriptions
Preparing data/local/test transcriptions
local/aishell_data_prep.sh: AISHELL data preparation succeeded
```

`utils/prepare_lang.sh` <!-- TODO: What? -->

Output:

```
utils/prepare_lang.sh --position-dependent-phones false data/local/dict <SPOKEN_NOISE> data/local/lang data/lang
Checking data/local/dict/silence_phones.txt ...
--> reading data/local/dict/silence_phones.txt
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> data/local/dict/silence_phones.txt is OK

Checking data/local/dict/optional_silence.txt ...
--> reading data/local/dict/optional_silence.txt
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> data/local/dict/optional_silence.txt is OK

Checking data/local/dict/nonsilence_phones.txt ...
--> reading data/local/dict/nonsilence_phones.txt
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> data/local/dict/nonsilence_phones.txt is OK

Checking disjoint: silence_phones.txt, nonsilence_phones.txt
--> disjoint property is OK.

Checking data/local/dict/lexicon.txt
--> reading data/local/dict/lexicon.txt
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> data/local/dict/lexicon.txt is OK

Checking data/local/dict/lexiconp.txt
--> reading data/local/dict/lexiconp.txt
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> data/local/dict/lexiconp.txt is OK

Checking lexicon pair data/local/dict/lexicon.txt and data/local/dict/lexiconp.txt
--> lexicon pair data/local/dict/lexicon.txt and data/local/dict/lexiconp.txt match

Checking data/local/dict/extra_questions.txt ...
--> reading data/local/dict/extra_questions.txt
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> data/local/dict/extra_questions.txt is OK
--> SUCCESS [validating dictionary directory data/local/dict]

fstaddselfloops data/lang/phones/wdisambig_phones.int data/lang/phones/wdisambig_words.int
prepare_lang.sh: validating output directory
utils/validate_lang.pl data/lang
Checking existence of separator file
separator file data/lang/subword_separator.txt is empty or does not exist, deal in word case.
Checking data/lang/phones.txt ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> data/lang/phones.txt is OK

Checking words.txt: #0 ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> data/lang/words.txt is OK

Checking disjoint: silence.txt, nonsilence.txt, disambig.txt ...
--> silence.txt and nonsilence.txt are disjoint
--> silence.txt and disambig.txt are disjoint
--> disambig.txt and nonsilence.txt are disjoint
--> disjoint property is OK

Checking sumation: silence.txt, nonsilence.txt, disambig.txt ...
--> found no unexplainable phones in phones.txt

Checking data/lang/phones/context_indep.{txt, int, csl} ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> 1 entry/entries in data/lang/phones/context_indep.txt
--> data/lang/phones/context_indep.int corresponds to data/lang/phones/context_indep.txt
--> data/lang/phones/context_indep.csl corresponds to data/lang/phones/context_indep.txt
--> data/lang/phones/context_indep.{txt, int, csl} are OK

Checking data/lang/phones/nonsilence.{txt, int, csl} ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> 216 entry/entries in data/lang/phones/nonsilence.txt
--> data/lang/phones/nonsilence.int corresponds to data/lang/phones/nonsilence.txt
--> data/lang/phones/nonsilence.csl corresponds to data/lang/phones/nonsilence.txt
--> data/lang/phones/nonsilence.{txt, int, csl} are OK

Checking data/lang/phones/silence.{txt, int, csl} ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> 1 entry/entries in data/lang/phones/silence.txt
--> data/lang/phones/silence.int corresponds to data/lang/phones/silence.txt
--> data/lang/phones/silence.csl corresponds to data/lang/phones/silence.txt
--> data/lang/phones/silence.{txt, int, csl} are OK

Checking data/lang/phones/optional_silence.{txt, int, csl} ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> 1 entry/entries in data/lang/phones/optional_silence.txt
--> data/lang/phones/optional_silence.int corresponds to data/lang/phones/optional_silence.txt
--> data/lang/phones/optional_silence.csl corresponds to data/lang/phones/optional_silence.txt
--> data/lang/phones/optional_silence.{txt, int, csl} are OK

Checking data/lang/phones/disambig.{txt, int, csl} ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> 105 entry/entries in data/lang/phones/disambig.txt
--> data/lang/phones/disambig.int corresponds to data/lang/phones/disambig.txt
--> data/lang/phones/disambig.csl corresponds to data/lang/phones/disambig.txt
--> data/lang/phones/disambig.{txt, int, csl} are OK

Checking data/lang/phones/roots.{txt, int} ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> 67 entry/entries in data/lang/phones/roots.txt
--> data/lang/phones/roots.int corresponds to data/lang/phones/roots.txt
--> data/lang/phones/roots.{txt, int} are OK

Checking data/lang/phones/sets.{txt, int} ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> 67 entry/entries in data/lang/phones/sets.txt
--> data/lang/phones/sets.int corresponds to data/lang/phones/sets.txt
--> data/lang/phones/sets.{txt, int} are OK

Checking data/lang/phones/extra_questions.{txt, int} ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> 7 entry/entries in data/lang/phones/extra_questions.txt
--> data/lang/phones/extra_questions.int corresponds to data/lang/phones/extra_questions.txt
--> data/lang/phones/extra_questions.{txt, int} are OK

Checking optional_silence.txt ...
--> reading data/lang/phones/optional_silence.txt
--> data/lang/phones/optional_silence.txt is OK

Checking disambiguation symbols: #0 and #1
--> data/lang/phones/disambig.txt has "#0" and "#1"
--> data/lang/phones/disambig.txt is OK

Checking topo ...

Checking word-level disambiguation symbols...
--> data/lang/phones/wdisambig.txt exists (newer prepare_lang.sh)
Checking data/lang/oov.{txt, int} ...
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> 1 entry/entries in data/lang/oov.txt
--> data/lang/oov.int corresponds to data/lang/oov.txt
--> data/lang/oov.{txt, int} are OK

--> data/lang/L.fst is olabel sorted
--> data/lang/L_disambig.fst is olabel sorted
--> SUCCESS [validating lang directory data/lang]
```

Rest of the output:

```
Not creating raw N-gram counts ngrams.gz and heldout_ngrams.gz since they already exist in data/local/lm/3gram-mincount
(remove them if you want them regenerated)
Not doing optimization of discounting parameters since
file data/local/lm/3gram-mincount/config.6 already exists
Final config is:
D=0.6 tau=0.527830672157611 phi=2
D=0.706938285164495 tau=0.664727230661135 phi=2.7
D=0 tau=1.09671484103859 phi=1.85025636116095
Not creating discounted N-grams file data/local/lm/3gram-mincount/ngrams_disc.gz since it already exists
Computing final perplexity
Building ARPA LM (perplexity computation is in background)
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
Perplexity over 99496.000000 words is 567.320537
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 567.320537
567.320537
Done training LM of type 3gram-mincount
Converting 'data/local/lm/3gram-mincount/lm_unpruned.gz' to FST
arpa2fst --disambig-symbol=#0 --read-symbol-table=data/lang_test/words.txt - data/lang_test/G.fst 
LOG (arpa2fst[5.5.1126~1-8c451]:Read():arpa-file-parser.cc:94) Reading \data\ section.
LOG (arpa2fst[5.5.1126~1-8c451]:Read():arpa-file-parser.cc:149) Reading \1-grams: section.
LOG (arpa2fst[5.5.1126~1-8c451]:Read():arpa-file-parser.cc:149) Reading \2-grams: section.
LOG (arpa2fst[5.5.1126~1-8c451]:Read():arpa-file-parser.cc:149) Reading \3-grams: section.
LOG (arpa2fst[5.5.1126~1-8c451]:RemoveRedundantStates():arpa-lm-compiler.cc:359) Reduced num-states from 561655 to 102646
fstisstochastic data/lang_test/G.fst 
8.84583e-06 -0.56498
Succeeded in formatting LM: 'data/local/lm/3gram-mincount/lm_unpruned.gz'
steps/make_mfcc_pitch.sh --cmd utils/parallel/run.pl --nj 10 data/train exp/make_mfcc/train mfcc
utils/validate_data_dir.sh: Successfully validated data-directory data/train
steps/make_mfcc_pitch.sh: [info]: no segments file exists: assuming wav.scp indexed by utterance.
steps/make_mfcc_pitch.sh: Succeeded creating MFCC and pitch features for train
steps/compute_cmvn_stats.sh data/train exp/make_mfcc/train mfcc
Succeeded creating CMVN stats for train
fix_data_dir.sh: kept all 120098 utterances.
fix_data_dir.sh: old files are kept in data/train/.backup
steps/make_mfcc_pitch.sh --cmd utils/parallel/run.pl --nj 10 data/dev exp/make_mfcc/dev mfcc
utils/validate_data_dir.sh: Successfully validated data-directory data/dev
steps/make_mfcc_pitch.sh: [info]: no segments file exists: assuming wav.scp indexed by utterance.
steps/make_mfcc_pitch.sh: Succeeded creating MFCC and pitch features for dev
steps/compute_cmvn_stats.sh data/dev exp/make_mfcc/dev mfcc
Succeeded creating CMVN stats for dev
fix_data_dir.sh: kept all 14326 utterances.
fix_data_dir.sh: old files are kept in data/dev/.backup
steps/make_mfcc_pitch.sh --cmd utils/parallel/run.pl --nj 10 data/test exp/make_mfcc/test mfcc
utils/validate_data_dir.sh: Successfully validated data-directory data/test
steps/make_mfcc_pitch.sh: [info]: no segments file exists: assuming wav.scp indexed by utterance.
steps/make_mfcc_pitch.sh: Succeeded creating MFCC and pitch features for test
steps/compute_cmvn_stats.sh data/test exp/make_mfcc/test mfcc
Succeeded creating CMVN stats for test
fix_data_dir.sh: kept all 7176 utterances.
fix_data_dir.sh: old files are kept in data/test/.backup
steps/train_mono.sh --cmd utils/parallel/run.pl --nj 10 data/train data/lang exp/mono
steps/train_mono.sh: Initializing monophone system.
steps/train_mono.sh: Compiling training graphs
steps/train_mono.sh: Aligning data equally (pass 0)
steps/train_mono.sh: Pass 1
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 2
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 3
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 4
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 5
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 6
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 7
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 8
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 9
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 10
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 11
steps/train_mono.sh: Pass 12
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 13
steps/train_mono.sh: Pass 14
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 15
steps/train_mono.sh: Pass 16
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 17
steps/train_mono.sh: Pass 18
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 19
steps/train_mono.sh: Pass 20
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 21
steps/train_mono.sh: Pass 22
steps/train_mono.sh: Pass 23
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 24
steps/train_mono.sh: Pass 25
steps/train_mono.sh: Pass 26
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 27
steps/train_mono.sh: Pass 28
steps/train_mono.sh: Pass 29
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 30
steps/train_mono.sh: Pass 31
steps/train_mono.sh: Pass 32
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 33
steps/train_mono.sh: Pass 34
steps/train_mono.sh: Pass 35
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 36
steps/train_mono.sh: Pass 37
steps/train_mono.sh: Pass 38
steps/train_mono.sh: Aligning data
steps/train_mono.sh: Pass 39
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/mono
steps/diagnostic/analyze_alignments.sh: see stats in exp/mono/log/analyze_alignments.log
37209 warnings in exp/mono/log/align.*.*.log
1136 warnings in exp/mono/log/acc.*.*.log
exp/mono: nj=10 align prob=-82.05 over 150.16h [retry=0.9%, fail=0.0%] states=203 gauss=985
steps/train_mono.sh: Done training monophone system in exp/mono
tree-info exp/mono/tree 
tree-info exp/mono/tree 
fstpushspecial 
fstminimizeencoded 
fsttablecompose data/lang_test/L_disambig.fst data/lang_test/G.fst 
fstdeterminizestar --use-log=true 
fstisstochastic data/lang_test/tmp/LG.fst 
-0.0663446 -0.0666824
[info]: LG not stochastic.
fstcomposecontext --context-size=1 --central-position=0 --read-disambig-syms=data/lang_test/phones/disambig.int --write-disambig-syms=data/lang_test/tmp/disambig_ilabels_1_0.int data/lang_test/tmp/ilabels_1_0.46111 data/lang_test/tmp/LG.fst 
fstisstochastic data/lang_test/tmp/CLG_1_0.fst 
-0.0663446 -0.0666824
[info]: CLG not stochastic.
make-h-transducer --disambig-syms-out=exp/mono/graph/disambig_tid.int --transition-scale=1.0 data/lang_test/tmp/ilabels_1_0 exp/mono/tree exp/mono/final.mdl 
fstdeterminizestar --use-log=true 
fstminimizeencoded 
fsttablecompose exp/mono/graph/Ha.fst data/lang_test/tmp/CLG_1_0.fst 
fstrmsymbols exp/mono/graph/disambig_tid.int 
fstrmepslocal 
fstisstochastic exp/mono/graph/HCLGa.fst 
0.000205497 -0.132761
HCLGa is not stochastic
add-self-loops --self-loop-scale=0.1 --reorder=true exp/mono/final.mdl exp/mono/graph/HCLGa.fst 
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 10 exp/mono/graph data/dev exp/mono/decode_dev
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/mono/graph exp/mono/decode_dev
steps/diagnostic/analyze_lats.sh: see stats in exp/mono/decode_dev/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,16,132) and mean=49.4
steps/diagnostic/analyze_lats.sh: see stats in exp/mono/decode_dev/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/dev exp/mono/graph exp/mono/decode_dev
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 10 exp/mono/graph data/test exp/mono/decode_test
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/mono/graph exp/mono/decode_test
steps/diagnostic/analyze_lats.sh: see stats in exp/mono/decode_test/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,20,154) and mean=57.2
steps/diagnostic/analyze_lats.sh: see stats in exp/mono/decode_test/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/test exp/mono/graph exp/mono/decode_test
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/align_si.sh --cmd utils/parallel/run.pl --nj 10 data/train data/lang exp/mono exp/mono_ali
steps/align_si.sh: feature type is delta
steps/align_si.sh: aligning data in data/train using model from exp/mono, putting alignments in exp/mono_ali
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/mono_ali
steps/diagnostic/analyze_alignments.sh: see stats in exp/mono_ali/log/analyze_alignments.log
steps/align_si.sh: done aligning data.
steps/train_deltas.sh --cmd utils/parallel/run.pl 2500 20000 data/train data/lang exp/mono_ali exp/tri1
steps/train_deltas.sh: accumulating tree stats
steps/train_deltas.sh: getting questions for tree-building, via clustering
steps/train_deltas.sh: building the tree
steps/train_deltas.sh: converting alignments from exp/mono_ali to use current tree
steps/train_deltas.sh: compiling graphs of transcripts
steps/train_deltas.sh: training pass 1
steps/train_deltas.sh: training pass 2
steps/train_deltas.sh: training pass 3
steps/train_deltas.sh: training pass 4
steps/train_deltas.sh: training pass 5
steps/train_deltas.sh: training pass 6
steps/train_deltas.sh: training pass 7
steps/train_deltas.sh: training pass 8
steps/train_deltas.sh: training pass 9
steps/train_deltas.sh: training pass 10
steps/train_deltas.sh: aligning data
steps/train_deltas.sh: training pass 11
steps/train_deltas.sh: training pass 12
steps/train_deltas.sh: training pass 13
steps/train_deltas.sh: training pass 14
steps/train_deltas.sh: training pass 15
steps/train_deltas.sh: training pass 16
steps/train_deltas.sh: training pass 17
steps/train_deltas.sh: training pass 18
steps/train_deltas.sh: training pass 19
steps/train_deltas.sh: training pass 20
steps/train_deltas.sh: aligning data
steps/train_deltas.sh: training pass 21
steps/train_deltas.sh: training pass 22
steps/train_deltas.sh: training pass 23
steps/train_deltas.sh: training pass 24
steps/train_deltas.sh: training pass 25
steps/train_deltas.sh: training pass 26
steps/train_deltas.sh: training pass 27
steps/train_deltas.sh: training pass 28
steps/train_deltas.sh: training pass 29
steps/train_deltas.sh: training pass 30
steps/train_deltas.sh: aligning data
steps/train_deltas.sh: training pass 31
steps/train_deltas.sh: training pass 32
steps/train_deltas.sh: training pass 33
steps/train_deltas.sh: training pass 34
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/tri1
steps/diagnostic/analyze_alignments.sh: see stats in exp/tri1/log/analyze_alignments.log
2880 warnings in exp/tri1/log/align.*.*.log
1 warnings in exp/tri1/log/compile_questions.log
846 warnings in exp/tri1/log/acc.*.*.log
1 warnings in exp/tri1/log/build_tree.log
exp/tri1: nj=10 align prob=-79.45 over 150.17h [retry=0.5%, fail=0.0%] states=2072 gauss=20046 tree-impr=4.49
steps/train_deltas.sh: Done training system with delta+delta-delta features in exp/tri1
tree-info exp/tri1/tree 
tree-info exp/tri1/tree 
fstcomposecontext --context-size=3 --central-position=1 --read-disambig-syms=data/lang_test/phones/disambig.int --write-disambig-syms=data/lang_test/tmp/disambig_ilabels_3_1.int data/lang_test/tmp/ilabels_3_1.58623 data/lang_test/tmp/LG.fst 
fstisstochastic data/lang_test/tmp/CLG_3_1.fst 
0 -0.0666824
[info]: CLG not stochastic.
make-h-transducer --disambig-syms-out=exp/tri1/graph/disambig_tid.int --transition-scale=1.0 data/lang_test/tmp/ilabels_3_1 exp/tri1/tree exp/tri1/final.mdl 
fstrmepslocal 
fsttablecompose exp/tri1/graph/Ha.fst data/lang_test/tmp/CLG_3_1.fst 
fstrmsymbols exp/tri1/graph/disambig_tid.int 
fstminimizeencoded 
fstdeterminizestar --use-log=true 
fstisstochastic exp/tri1/graph/HCLGa.fst 
0.000487832 -0.178947
HCLGa is not stochastic
add-self-loops --self-loop-scale=0.1 --reorder=true exp/tri1/final.mdl exp/tri1/graph/HCLGa.fst 
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 10 exp/tri1/graph data/dev exp/tri1/decode_dev
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri1/graph exp/tri1/decode_dev
steps/diagnostic/analyze_lats.sh: see stats in exp/tri1/decode_dev/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,4,30) and mean=11.9
steps/diagnostic/analyze_lats.sh: see stats in exp/tri1/decode_dev/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/dev exp/tri1/graph exp/tri1/decode_dev
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 10 exp/tri1/graph data/test exp/tri1/decode_test
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri1/graph exp/tri1/decode_test
steps/diagnostic/analyze_lats.sh: see stats in exp/tri1/decode_test/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,4,40) and mean=15.3
steps/diagnostic/analyze_lats.sh: see stats in exp/tri1/decode_test/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/test exp/tri1/graph exp/tri1/decode_test
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/align_si.sh --cmd utils/parallel/run.pl --nj 10 data/train data/lang exp/tri1 exp/tri1_ali
steps/align_si.sh: feature type is delta
steps/align_si.sh: aligning data in data/train using model from exp/tri1, putting alignments in exp/tri1_ali
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/tri1_ali
steps/diagnostic/analyze_alignments.sh: see stats in exp/tri1_ali/log/analyze_alignments.log
steps/align_si.sh: done aligning data.
steps/train_deltas.sh --cmd utils/parallel/run.pl 2500 20000 data/train data/lang exp/tri1_ali exp/tri2
steps/train_deltas.sh: accumulating tree stats
steps/train_deltas.sh: getting questions for tree-building, via clustering
steps/train_deltas.sh: building the tree
steps/train_deltas.sh: converting alignments from exp/tri1_ali to use current tree
steps/train_deltas.sh: compiling graphs of transcripts
steps/train_deltas.sh: training pass 1
steps/train_deltas.sh: training pass 2
steps/train_deltas.sh: training pass 3
steps/train_deltas.sh: training pass 4
steps/train_deltas.sh: training pass 5
steps/train_deltas.sh: training pass 6
steps/train_deltas.sh: training pass 7
steps/train_deltas.sh: training pass 8
steps/train_deltas.sh: training pass 9
steps/train_deltas.sh: training pass 10
steps/train_deltas.sh: aligning data
steps/train_deltas.sh: training pass 11
steps/train_deltas.sh: training pass 12
steps/train_deltas.sh: training pass 13
steps/train_deltas.sh: training pass 14
steps/train_deltas.sh: training pass 15
steps/train_deltas.sh: training pass 16
steps/train_deltas.sh: training pass 17
steps/train_deltas.sh: training pass 18
steps/train_deltas.sh: training pass 19
steps/train_deltas.sh: training pass 20
steps/train_deltas.sh: aligning data
steps/train_deltas.sh: training pass 21
steps/train_deltas.sh: training pass 22
steps/train_deltas.sh: training pass 23
steps/train_deltas.sh: training pass 24
steps/train_deltas.sh: training pass 25
steps/train_deltas.sh: training pass 26
steps/train_deltas.sh: training pass 27
steps/train_deltas.sh: training pass 28
steps/train_deltas.sh: training pass 29
steps/train_deltas.sh: training pass 30
steps/train_deltas.sh: aligning data
steps/train_deltas.sh: training pass 31
steps/train_deltas.sh: training pass 32
steps/train_deltas.sh: training pass 33
steps/train_deltas.sh: training pass 34
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/tri2
steps/diagnostic/analyze_alignments.sh: see stats in exp/tri2/log/analyze_alignments.log
566 warnings in exp/tri2/log/acc.*.*.log
1 warnings in exp/tri2/log/compile_questions.log
2219 warnings in exp/tri2/log/align.*.*.log
1 warnings in exp/tri2/log/build_tree.log
exp/tri2: nj=10 align prob=-79.42 over 150.18h [retry=0.4%, fail=0.0%] states=2128 gauss=20032 tree-impr=4.82
steps/train_deltas.sh: Done training system with delta+delta-delta features in exp/tri2
tree-info exp/tri2/tree 
tree-info exp/tri2/tree 
make-h-transducer --disambig-syms-out=exp/tri2/graph/disambig_tid.int --transition-scale=1.0 data/lang_test/tmp/ilabels_3_1 exp/tri2/tree exp/tri2/final.mdl 
fstrmepslocal 
fsttablecompose exp/tri2/graph/Ha.fst data/lang_test/tmp/CLG_3_1.fst 
fstrmsymbols exp/tri2/graph/disambig_tid.int 
fstdeterminizestar --use-log=true 
fstminimizeencoded 
fstisstochastic exp/tri2/graph/HCLGa.fst 
0.000486833 -0.178947
HCLGa is not stochastic
add-self-loops --self-loop-scale=0.1 --reorder=true exp/tri2/final.mdl exp/tri2/graph/HCLGa.fst 
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 10 exp/tri2/graph data/dev exp/tri2/decode_dev
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri2/graph exp/tri2/decode_dev
steps/diagnostic/analyze_lats.sh: see stats in exp/tri2/decode_dev/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,4,29) and mean=11.7
steps/diagnostic/analyze_lats.sh: see stats in exp/tri2/decode_dev/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/dev exp/tri2/graph exp/tri2/decode_dev
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 10 exp/tri2/graph data/test exp/tri2/decode_test
decode.sh: feature type is delta
```

<!-- TODO: Output not finished yet. -->
