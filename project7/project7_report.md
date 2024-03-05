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
The resulting files are in `data/local/dict`.

Output:

```
local/aishell_prepare_dict.sh: AISHELL dict preparation succeeded
```

`aishell_data_prep.sh` extracts the audio file names,
and split them into training, development, and testing sets. For each set,
it lists <!-- the file names without the `.wav` extension in `utt.list`,
--> the map from utterance IDs to speaker IDs in `utt2spk` and the other way
around in `spk2utt`,
the map from utterance IDs to `.wav` file paths in `wav.scp`,
and map from utterance IDs to transcriptions in <!-- `transcripts.txt` (and
deduplicated in -->`text`<!-- ) -->.

Output:

```
Preparing data/local/train transcriptions
Preparing data/local/dev transcriptions
Preparing data/local/test transcriptions
local/aishell_data_prep.sh: AISHELL data preparation succeeded
```

`utils/prepare_lang.sh` constructs the $L$ FST based on the output of
`local/aishell_prepare_dict.sh`.

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

Checking data/local/dict/extra_questions.txt ...
--> reading data/local/dict/extra_questions.txt
--> text seems to be UTF-8 or ASCII, checking whitespaces
--> text contains only allowed whitespaces
--> data/local/dict/extra_questions.txt is OK
--> SUCCESS [validating dictionary directory data/local/dict]

**Creating data/local/dict/lexiconp.txt from data/local/dict/lexicon.txt
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
Getting raw N-gram counts
discount_ngrams: for n-gram order 1, D=0.000000, tau=0.000000 phi=1.000000
discount_ngrams: for n-gram order 2, D=0.000000, tau=0.000000 phi=1.000000
discount_ngrams: for n-gram order 3, D=1.000000, tau=0.000000 phi=1.000000
Iteration 1/6 of optimizing discounting parameters
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.675000 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=0.675000 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=0.825000 phi=2.000000
discount_ngrams: for n-gram order 1, D=0.600000, tau=1.215000 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=1.215000 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.485000 phi=2.000000
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.900000 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=0.900000 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.100000 phi=2.000000
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
Perplexity over 99496.000000 words is 573.088187
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 573.088187

real    0m3.032s
user    0m3.779s
sys     0m0.175s
Perplexity over 99496.000000 words is 571.860357
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 571.860357
Perplexity over 99496.000000 words is 571.430399
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 571.430399

real    0m3.053s
user    0m3.730s
sys     0m0.174s

real    0m3.068s
user    0m3.815s
sys     0m0.151s
Projected perplexity change from setting alpha=-0.413521475380432 is 571.860357->571.350704659834, reduction of 0.509652340166213
Alpha value on iter 1 is -0.413521475380432
Iteration 2/6 of optimizing discounting parameters
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=0.483845 phi=2.000000
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=0.645126 phi=2.000000
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=0.870921 phi=2.000000
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
Perplexity over 99496.000000 words is 570.548231
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 570.548231
Perplexity over 99496.000000 words is 570.209333
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 570.209333

real    0m3.021s
user    0m3.662s
sys     0m0.175s

real    0m3.032s
user    0m3.686s
sys     0m0.164s
Perplexity over 99496.000000 words is 570.909914
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 570.909914

real    0m3.097s
user    0m3.812s
sys     0m0.145s
optimize_alpha.pl: alpha=0.782133003937562 is too positive, limiting it to 0.7
Projected perplexity change from setting alpha=0.7 is 570.548231->570.0658029, reduction of 0.482428099999765
Alpha value on iter 2 is 0.7
Iteration 3/6 of optimizing discounting parameters
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.750000
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=2.000000
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=2.350000
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
Perplexity over 99496.000000 words is 570.074175
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 570.074175
Perplexity over 99496.000000 words is 570.070852
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 570.070852
Perplexity over 99496.000000 words is 570.135232
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 570.135232

real    0m3.010s
user    0m3.674s
sys     0m0.153s

real    0m3.016s
user    0m3.712s
sys     0m0.137s

real    0m3.014s
user    0m3.741s
sys     0m0.153s
Projected perplexity change from setting alpha=-0.149743638839048 is 570.074175->570.068152268062, reduction of 0.00602273193794645
Alpha value on iter 3 is -0.149743638839048
Iteration 4/6 of optimizing discounting parameters
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.800000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=1.080000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
Perplexity over 99496.000000 words is 651.559076
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 651.559076

real    0m2.158s
user    0m2.492s
sys     0m0.131s
Perplexity over 99496.000000 words is 571.811721
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 571.811721
Perplexity over 99496.000000 words is 570.079098
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 570.079098

real    0m3.048s
user    0m3.718s
sys     0m0.150s

real    0m3.054s
user    0m3.787s
sys     0m0.166s
Projected perplexity change from setting alpha=-0.116327143544381 is 570.079098->564.672375993263, reduction of 5.40672200673657
Alpha value on iter 4 is -0.116327143544381
Iteration 5/6 of optimizing discounting parameters
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.706938, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.706938, tau=0.395873 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.706938, tau=0.712571 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
Perplexity over 99496.000000 words is 567.407206
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 567.407206

real    0m3.032s
user    0m3.694s
sys     0m0.160s
Perplexity over 99496.000000 words is 567.980179
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 567.980179
Perplexity over 99496.000000 words is 567.231151
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 567.231151

real    0m3.052s
user    0m3.710s
sys     0m0.193s

real    0m3.055s
user    0m3.658s
sys     0m0.171s
Projected perplexity change from setting alpha=0.259356959958262 is 567.407206->567.206654822021, reduction of 0.20055117797915
Alpha value on iter 5 is 0.259356959958262
Iteration 6/6 of optimizing discounting parameters
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.706938, tau=0.664727 phi=1.750000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.706938, tau=0.664727 phi=2.000000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.706938, tau=0.664727 phi=2.350000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
interpolate_ngrams: 137074 words in wordslist
Perplexity over 99496.000000 words is 567.346876
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 567.346876

real    0m3.017s
user    0m3.762s
sys     0m0.163s
Perplexity over 99496.000000 words is 567.181130
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 567.181130
Perplexity over 99496.000000 words is 567.478625
Perplexity over 99496.000000 words (excluding 0.000000 OOVs) is 567.478625

real    0m3.029s
user    0m3.690s
sys     0m0.138s

real    0m3.048s
user    0m3.625s
sys     0m0.207s
optimize_alpha.pl: alpha=2.83365708509299 is too positive, limiting it to 0.7
Projected perplexity change from setting alpha=0.7 is 567.346876->567.0372037, reduction of 0.309672299999761
Alpha value on iter 6 is 0.7
Final config is:
D=0.6 tau=0.527830672157611 phi=2
D=0.706938285164495 tau=0.664727230661135 phi=2.7
D=0 tau=1.09671484103859 phi=1.85025636116095
Discounting N-grams.
discount_ngrams: for n-gram order 1, D=0.600000, tau=0.527831 phi=2.000000
discount_ngrams: for n-gram order 2, D=0.706938, tau=0.664727 phi=2.700000
discount_ngrams: for n-gram order 3, D=0.000000, tau=1.096715 phi=1.850256
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
steps/make_mfcc_pitch.sh --cmd utils/parallel/run.pl --nj 16 data/train exp/make_mfcc/train mfcc
utils/validate_data_dir.sh: Successfully validated data-directory data/train
steps/make_mfcc_pitch.sh: [info]: no segments file exists: assuming wav.scp indexed by utterance.
steps/make_mfcc_pitch.sh: Succeeded creating MFCC and pitch features for train
steps/compute_cmvn_stats.sh data/train exp/make_mfcc/train mfcc
Succeeded creating CMVN stats for train
fix_data_dir.sh: kept all 120098 utterances.
fix_data_dir.sh: old files are kept in data/train/.backup
steps/make_mfcc_pitch.sh --cmd utils/parallel/run.pl --nj 16 data/dev exp/make_mfcc/dev mfcc
utils/validate_data_dir.sh: Successfully validated data-directory data/dev
steps/make_mfcc_pitch.sh: [info]: no segments file exists: assuming wav.scp indexed by utterance.
steps/make_mfcc_pitch.sh: Succeeded creating MFCC and pitch features for dev
steps/compute_cmvn_stats.sh data/dev exp/make_mfcc/dev mfcc
Succeeded creating CMVN stats for dev
fix_data_dir.sh: kept all 14326 utterances.
fix_data_dir.sh: old files are kept in data/dev/.backup
steps/make_mfcc_pitch.sh --cmd utils/parallel/run.pl --nj 16 data/test exp/make_mfcc/test mfcc
utils/validate_data_dir.sh: Successfully validated data-directory data/test
steps/make_mfcc_pitch.sh: [info]: no segments file exists: assuming wav.scp indexed by utterance.
steps/make_mfcc_pitch.sh: Succeeded creating MFCC and pitch features for test
steps/compute_cmvn_stats.sh data/test exp/make_mfcc/test mfcc
Succeeded creating CMVN stats for test
fix_data_dir.sh: kept all 7176 utterances.
fix_data_dir.sh: old files are kept in data/test/.backup
steps/train_mono.sh --cmd utils/parallel/run.pl --nj 16 data/train data/lang exp/mono
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
1152 warnings in exp/mono/log/acc.*.*.log
37199 warnings in exp/mono/log/align.*.*.log
exp/mono: nj=16 align prob=-82.05 over 150.15h [retry=1.0%, fail=0.0%] states=203 gauss=987
steps/train_mono.sh: Done training monophone system in exp/mono
tree-info exp/mono/tree 
tree-info exp/mono/tree 
fstpushspecial 
fsttablecompose data/lang_test/L_disambig.fst data/lang_test/G.fst 
fstminimizeencoded 
fstdeterminizestar --use-log=true 
fstisstochastic data/lang_test/tmp/LG.fst 
-0.0663446 -0.0666824
[info]: LG not stochastic.
fstcomposecontext --context-size=1 --central-position=0 --read-disambig-syms=data/lang_test/phones/disambig.int --write-disambig-syms=data/lang_test/tmp/disambig_ilabe
ls_1_0.int data/lang_test/tmp/ilabels_1_0.27619 data/lang_test/tmp/LG.fst 
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
0.000248593 -0.132761
HCLGa is not stochastic
add-self-loops --self-loop-scale=0.1 --reorder=true exp/mono/final.mdl exp/mono/graph/HCLGa.fst 
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 16 exp/mono/graph data/dev exp/mono/decode_dev
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/mono/graph exp/mono/decode_dev
steps/diagnostic/analyze_lats.sh: see stats in exp/mono/decode_dev/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,16,133) and mean=49.4
steps/diagnostic/analyze_lats.sh: see stats in exp/mono/decode_dev/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/dev exp/mono/graph exp/mono/decode_dev
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 16 exp/mono/graph data/test exp/mono/decode_test
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/mono/graph exp/mono/decode_test
steps/diagnostic/analyze_lats.sh: see stats in exp/mono/decode_test/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,20,156) and mean=57.9
steps/diagnostic/analyze_lats.sh: see stats in exp/mono/decode_test/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/test exp/mono/graph exp/mono/decode_test
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/align_si.sh --cmd utils/parallel/run.pl --nj 16 data/train data/lang exp/mono exp/mono_ali
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
1 warnings in exp/tri1/log/build_tree.log
906 warnings in exp/tri1/log/acc.*.*.log
3411 warnings in exp/tri1/log/align.*.*.log
1 warnings in exp/tri1/log/compile_questions.log
exp/tri1: nj=16 align prob=-79.45 over 150.17h [retry=0.6%, fail=0.0%] states=2072 gauss=20052 tree-impr=4.50
steps/train_deltas.sh: Done training system with delta+delta-delta features in exp/tri1
tree-info exp/tri1/tree 
tree-info exp/tri1/tree 
fstcomposecontext --context-size=3 --central-position=1 --read-disambig-syms=data/lang_test/phones/disambig.int --write-disambig-syms=data/lang_test/tmp/disambig_ilabe
ls_3_1.int data/lang_test/tmp/ilabels_3_1.43358 data/lang_test/tmp/LG.fst 
fstisstochastic data/lang_test/tmp/CLG_3_1.fst 
0 -0.0666824
[info]: CLG not stochastic.
make-h-transducer --disambig-syms-out=exp/tri1/graph/disambig_tid.int --transition-scale=1.0 data/lang_test/tmp/ilabels_3_1 exp/tri1/tree exp/tri1/final.mdl 
fsttablecompose exp/tri1/graph/Ha.fst data/lang_test/tmp/CLG_3_1.fst 
fstrmepslocal 
fstminimizeencoded 
fstrmsymbols exp/tri1/graph/disambig_tid.int 
fstdeterminizestar --use-log=true 
fstisstochastic exp/tri1/graph/HCLGa.fst 
0.000487832 -0.178947
HCLGa is not stochastic
add-self-loops --self-loop-scale=0.1 --reorder=true exp/tri1/final.mdl exp/tri1/graph/HCLGa.fst 
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 16 exp/tri1/graph data/dev exp/tri1/decode_dev
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri1/graph exp/tri1/decode_dev
steps/diagnostic/analyze_lats.sh: see stats in exp/tri1/decode_dev/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,4,30) and mean=11.9
steps/diagnostic/analyze_lats.sh: see stats in exp/tri1/decode_dev/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/dev exp/tri1/graph exp/tri1/decode_dev
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 16 exp/tri1/graph data/test exp/tri1/decode_test
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri1/graph exp/tri1/decode_test
steps/diagnostic/analyze_lats.sh: see stats in exp/tri1/decode_test/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,5,40) and mean=15.7
steps/diagnostic/analyze_lats.sh: see stats in exp/tri1/decode_test/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/test exp/tri1/graph exp/tri1/decode_test
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/align_si.sh --cmd utils/parallel/run.pl --nj 16 data/train data/lang exp/tri1 exp/tri1_ali
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
649 warnings in exp/tri2/log/acc.*.*.log
1 warnings in exp/tri2/log/compile_questions.log
1 warnings in exp/tri2/log/build_tree.log
2581 warnings in exp/tri2/log/align.*.*.log
exp/tri2: nj=16 align prob=-79.41 over 150.18h [retry=0.4%, fail=0.0%] states=2104 gauss=20029 tree-impr=4.85
steps/train_deltas.sh: Done training system with delta+delta-delta features in exp/tri2
tree-info exp/tri2/tree 
tree-info exp/tri2/tree 
make-h-transducer --disambig-syms-out=exp/tri2/graph/disambig_tid.int --transition-scale=1.0 data/lang_test/tmp/ilabels_3_1 exp/tri2/tree exp/tri2/final.mdl 
fstrmepslocal 
fstrmsymbols exp/tri2/graph/disambig_tid.int 
fstminimizeencoded 
fstdeterminizestar --use-log=true 
fsttablecompose exp/tri2/graph/Ha.fst data/lang_test/tmp/CLG_3_1.fst 
fstisstochastic exp/tri2/graph/HCLGa.fst 
0.000487832 -0.178947
HCLGa is not stochastic
add-self-loops --self-loop-scale=0.1 --reorder=true exp/tri2/final.mdl exp/tri2/graph/HCLGa.fst 
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 16 exp/tri2/graph data/dev exp/tri2/decode_dev
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri2/graph exp/tri2/decode_dev
steps/diagnostic/analyze_lats.sh: see stats in exp/tri2/decode_dev/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,4,30) and mean=11.8
steps/diagnostic/analyze_lats.sh: see stats in exp/tri2/decode_dev/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/dev exp/tri2/graph exp/tri2/decode_dev
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/decode.sh --cmd utils/parallel/run.pl --config conf/decode.config --nj 16 exp/tri2/graph data/test exp/tri2/decode_test
decode.sh: feature type is delta
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri2/graph exp/tri2/decode_test
steps/diagnostic/analyze_lats.sh: see stats in exp/tri2/decode_test/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,4,39) and mean=15.3
steps/diagnostic/analyze_lats.sh: see stats in exp/tri2/decode_test/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/test exp/tri2/graph exp/tri2/decode_test
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/align_si.sh --cmd utils/parallel/run.pl --nj 16 data/train data/lang exp/tri2 exp/tri2_ali
steps/align_si.sh: feature type is delta
steps/align_si.sh: aligning data in data/train using model from exp/tri2, putting alignments in exp/tri2_ali
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/tri2_ali
steps/diagnostic/analyze_alignments.sh: see stats in exp/tri2_ali/log/analyze_alignments.log
steps/align_si.sh: done aligning data.
steps/train_lda_mllt.sh --cmd utils/parallel/run.pl 2500 20000 data/train data/lang exp/tri2_ali exp/tri3a
steps/train_lda_mllt.sh: Accumulating LDA statistics.
steps/train_lda_mllt.sh: Accumulating tree stats
steps/train_lda_mllt.sh: Getting questions for tree clustering.
steps/train_lda_mllt.sh: Building the tree
steps/train_lda_mllt.sh: Initializing the model
steps/train_lda_mllt.sh: Converting alignments from exp/tri2_ali to use current tree
steps/train_lda_mllt.sh: Compiling graphs of transcripts
Training pass 1
Training pass 2
steps/train_lda_mllt.sh: Estimating MLLT
Training pass 3
Training pass 4
steps/train_lda_mllt.sh: Estimating MLLT
Training pass 5
Training pass 6
steps/train_lda_mllt.sh: Estimating MLLT
Training pass 7
Training pass 8
Training pass 9
Training pass 10
Aligning data
Training pass 11
Training pass 12
steps/train_lda_mllt.sh: Estimating MLLT
Training pass 13
Training pass 14
Training pass 15
Training pass 16
Training pass 17
Training pass 18
Training pass 19
Training pass 20
Aligning data
Training pass 21
Training pass 22
Training pass 23
Training pass 24
Training pass 25
Training pass 26
Training pass 27
Training pass 28
Training pass 29
Training pass 30
Aligning data
Training pass 31
Training pass 32
Training pass 33
Training pass 34
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/tri3a
steps/diagnostic/analyze_alignments.sh: see stats in exp/tri3a/log/analyze_alignments.log
7 warnings in exp/tri3a/log/lda_acc.*.log
1322 warnings in exp/tri3a/log/align.*.*.log
273 warnings in exp/tri3a/log/acc.*.*.log
1 warnings in exp/tri3a/log/build_tree.log
1 warnings in exp/tri3a/log/compile_questions.log
exp/tri3a: nj=16 align prob=-48.77 over 150.18h [retry=0.3%, fail=0.0%] states=2096 gauss=20037 tree-impr=5.08 lda-sum=24.62 mllt:impr,logdet=0.94,1.40
steps/train_lda_mllt.sh: Done training system with LDA+MLLT features in exp/tri3a
tree-info exp/tri3a/tree 
tree-info exp/tri3a/tree 
make-h-transducer --disambig-syms-out=exp/tri3a/graph/disambig_tid.int --transition-scale=1.0 data/lang_test/tmp/ilabels_3_1 exp/tri3a/tree exp/tri3a/final.mdl 
fstrmepslocal 
fsttablecompose exp/tri3a/graph/Ha.fst data/lang_test/tmp/CLG_3_1.fst 
fstminimizeencoded 
fstrmsymbols exp/tri3a/graph/disambig_tid.int 
fstdeterminizestar --use-log=true 
fstisstochastic exp/tri3a/graph/HCLGa.fst 
0.000487099 -0.178947
HCLGa is not stochastic
add-self-loops --self-loop-scale=0.1 --reorder=true exp/tri3a/final.mdl exp/tri3a/graph/HCLGa.fst 
steps/decode.sh --cmd utils/parallel/run.pl --nj 16 --config conf/decode.config exp/tri3a/graph data/dev exp/tri3a/decode_dev
decode.sh: feature type is lda
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri3a/graph exp/tri3a/decode_dev
steps/diagnostic/analyze_lats.sh: see stats in exp/tri3a/decode_dev/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,3,24) and mean=9.7
steps/diagnostic/analyze_lats.sh: see stats in exp/tri3a/decode_dev/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/dev exp/tri3a/graph exp/tri3a/decode_dev
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/decode.sh --cmd utils/parallel/run.pl --nj 16 --config conf/decode.config exp/tri3a/graph data/test exp/tri3a/decode_test
decode.sh: feature type is lda
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri3a/graph exp/tri3a/decode_test
steps/diagnostic/analyze_lats.sh: see stats in exp/tri3a/decode_test/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,4,31) and mean=12.0
steps/diagnostic/analyze_lats.sh: see stats in exp/tri3a/decode_test/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/test exp/tri3a/graph exp/tri3a/decode_test
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/align_fmllr.sh --cmd utils/parallel/run.pl --nj 16 data/train data/lang exp/tri3a exp/tri3a_ali
steps/align_fmllr.sh: feature type is lda
steps/align_fmllr.sh: compiling training graphs
steps/align_fmllr.sh: aligning data in data/train using exp/tri3a/final.mdl and speaker-independent features.
steps/align_fmllr.sh: computing fMLLR transforms
steps/align_fmllr.sh: doing final alignment.
steps/align_fmllr.sh: done aligning data.
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/tri3a_ali
steps/diagnostic/analyze_alignments.sh: see stats in exp/tri3a_ali/log/analyze_alignments.log
5 warnings in exp/tri3a_ali/log/fmllr.*.log
299 warnings in exp/tri3a_ali/log/align_pass2.*.log
299 warnings in exp/tri3a_ali/log/align_pass1.*.log
steps/train_sat.sh --cmd utils/parallel/run.pl 2500 20000 data/train data/lang exp/tri3a_ali exp/tri4a
steps/train_sat.sh: feature type is lda
steps/train_sat.sh: Using transforms from exp/tri3a_ali
steps/train_sat.sh: Accumulating tree stats
steps/train_sat.sh: Getting questions for tree clustering.
steps/train_sat.sh: Building the tree
steps/train_sat.sh: Initializing the model
steps/train_sat.sh: Converting alignments from exp/tri3a_ali to use current tree
steps/train_sat.sh: Compiling graphs of transcripts
Pass 1
Pass 2
Estimating fMLLR transforms
Pass 3
Pass 4
Estimating fMLLR transforms
Pass 5
Pass 6
Estimating fMLLR transforms
Pass 7
Pass 8
Pass 9
Pass 10
Aligning data
Pass 11
Pass 12
Estimating fMLLR transforms
Pass 13
Pass 14
Pass 15
Pass 16
Pass 17
Pass 18
Pass 19
Pass 20
Aligning data
Pass 21
Pass 22
Pass 23
Pass 24
Pass 25
Pass 26
Pass 27
Pass 28
Pass 29
Pass 30
Aligning data
Pass 31
Pass 32
Pass 33
Pass 34
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/tri4a
steps/diagnostic/analyze_alignments.sh: see stats in exp/tri4a/log/analyze_alignments.log
48 warnings in exp/tri4a/log/fmllr.*.*.log
1 warnings in exp/tri4a/log/build_tree.log
1800 warnings in exp/tri4a/log/align.*.*.log
1 warnings in exp/tri4a/log/compile_questions.log
810 warnings in exp/tri4a/log/acc.*.*.log
steps/train_sat.sh: Likelihood evolution:
-49.2638 -49.0751 -48.9586 -48.7789 -48.3692 -47.9364 -47.6116 -47.3784 -47.1985 -46.8099 -46.6614 -46.4516 -46.339 -46.2553 -46.1875 -46.1254 -46.0639 -46.0033 -45.94
55 -45.8172 -45.7513 -45.7107 -45.675 -45.6418 -45.61 -45.5789 -45.5473 -45.5166 -45.4875 -45.4183 -45.3785 -45.358 -45.3445 -45.3353 
exp/tri4a: nj=16 align prob=-48.28 over 150.17h [retry=0.4%, fail=0.0%] states=2160 gauss=20027 fmllr-impr=0.63 over 115.63h tree-impr=7.08
steps/train_sat.sh: done training SAT system in exp/tri4a
tree-info exp/tri4a/tree 
tree-info exp/tri4a/tree 
make-h-transducer --disambig-syms-out=exp/tri4a/graph/disambig_tid.int --transition-scale=1.0 data/lang_test/tmp/ilabels_3_1 exp/tri4a/tree exp/tri4a/final.mdl 
fsttablecompose exp/tri4a/graph/Ha.fst data/lang_test/tmp/CLG_3_1.fst 
fstrmepslocal 
fstminimizeencoded 
fstrmsymbols exp/tri4a/graph/disambig_tid.int 
fstdeterminizestar --use-log=true 
fstisstochastic exp/tri4a/graph/HCLGa.fst 
0.000486833 -0.178947
HCLGa is not stochastic
add-self-loops --self-loop-scale=0.1 --reorder=true exp/tri4a/final.mdl exp/tri4a/graph/HCLGa.fst 
steps/decode_fmllr.sh --cmd utils/parallel/run.pl --nj 16 --config conf/decode.config exp/tri4a/graph data/dev exp/tri4a/decode_dev
steps/decode.sh --scoring-opts  --num-threads 1 --skip-scoring false --acwt 0.083333 --nj 16 --cmd utils/parallel/run.pl --beam 8.0 --model exp/tri4a/final.alimdl --ma
x-active 2000 exp/tri4a/graph data/dev exp/tri4a/decode_dev.si
decode.sh: feature type is lda
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri4a/graph exp/tri4a/decode_dev.si
steps/diagnostic/analyze_lats.sh: see stats in exp/tri4a/decode_dev.si/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,3,16) and mean=6.6
steps/diagnostic/analyze_lats.sh: see stats in exp/tri4a/decode_dev.si/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/dev exp/tri4a/graph exp/tri4a/decode_dev.si
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/decode_fmllr.sh --cmd utils/parallel/run.pl --nj 16 --config conf/decode.config exp/tri4a/graph data/test exp/tri4a/decode_test
steps/decode.sh --scoring-opts  --num-threads 1 --skip-scoring false --acwt 0.083333 --nj 16 --cmd utils/parallel/run.pl --beam 8.0 --model exp/tri4a/final.alimdl --ma
x-active 2000 exp/tri4a/graph data/test exp/tri4a/decode_test.si
decode.sh: feature type is lda
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri4a/graph exp/tri4a/decode_test.si
steps/diagnostic/analyze_lats.sh: see stats in exp/tri4a/decode_test.si/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,3,19) and mean=7.8
steps/diagnostic/analyze_lats.sh: see stats in exp/tri4a/decode_test.si/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/test exp/tri4a/graph exp/tri4a/decode_test.si
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
steps/align_fmllr.sh --cmd utils/parallel/run.pl --nj 16 data/train data/lang exp/tri4a exp/tri4a_ali
steps/align_fmllr.sh: feature type is lda
steps/align_fmllr.sh: compiling training graphs
steps/align_fmllr.sh: aligning data in data/train using exp/tri4a/final.alimdl and speaker-independent features.
steps/align_fmllr.sh: computing fMLLR transforms
steps/align_fmllr.sh: doing final alignment.
steps/align_fmllr.sh: done aligning data.
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/tri4a_ali
steps/diagnostic/analyze_alignments.sh: see stats in exp/tri4a_ali/log/analyze_alignments.log
347 warnings in exp/tri4a_ali/log/align_pass2.*.log
215 warnings in exp/tri4a_ali/log/align_pass1.*.log
1 warnings in exp/tri4a_ali/log/fmllr.*.log
steps/train_sat.sh --cmd utils/parallel/run.pl 3500 100000 data/train data/lang exp/tri4a_ali exp/tri5a
steps/train_sat.sh: feature type is lda
steps/train_sat.sh: Using transforms from exp/tri4a_ali
steps/train_sat.sh: Accumulating tree stats
steps/train_sat.sh: Getting questions for tree clustering.
steps/train_sat.sh: Building the tree
steps/train_sat.sh: Initializing the model
steps/train_sat.sh: Converting alignments from exp/tri4a_ali to use current tree
steps/train_sat.sh: Compiling graphs of transcripts
Pass 1
Pass 2
Estimating fMLLR transforms
Pass 3
Pass 4
Estimating fMLLR transforms
Pass 5
Pass 6
Estimating fMLLR transforms
Pass 7
Pass 8
Pass 9
Pass 10
Aligning data
Pass 11
Pass 12
Estimating fMLLR transforms
Pass 13
Pass 14
Pass 15
Pass 16
Pass 17
Pass 18
Pass 19
Pass 20
Aligning data
Pass 21
Pass 22
Pass 23
Pass 24
Pass 25
Pass 26
Pass 27
Pass 28
Pass 29
Pass 30
Aligning data
Pass 31
Pass 32
Pass 33
Pass 34
steps/diagnostic/analyze_alignments.sh --cmd utils/parallel/run.pl data/lang exp/tri5a
steps/diagnostic/analyze_alignments.sh: see stats in exp/tri5a/log/analyze_alignments.log
809 warnings in exp/tri5a/log/align.*.*.log
280 warnings in exp/tri5a/log/acc.*.*.log
1 warnings in exp/tri5a/log/build_tree.log
41 warnings in exp/tri5a/log/fmllr.*.*.log
1 warnings in exp/tri5a/log/compile_questions.log
steps/train_sat.sh: Likelihood evolution:
-48.6278 -48.6705 -48.62 -48.4388 -47.8812 -47.1604 -46.6265 -46.2616 -45.989 -45.67 -45.5039 -45.233 -45.1047 -45.0111 -44.9265 -44.8491 -44.7799 -44.7173 -44.6601 -4
4.5412 -44.4721 -44.426 -44.3849 -44.3463 -44.3098 -44.2751 -44.2419 -44.2101 -44.1793 -44.1153 -44.0723 -44.0475 -44.0302 -44.0178 
exp/tri5a: nj=16 align prob=-47.14 over 150.19h [retry=0.1%, fail=0.0%] states=3016 gauss=100104 fmllr-impr=0.25 over 116.69h tree-impr=7.66
steps/train_sat.sh: done training SAT system in exp/tri5a
tree-info exp/tri5a/tree 
tree-info exp/tri5a/tree 
make-h-transducer --disambig-syms-out=exp/tri5a/graph/disambig_tid.int --transition-scale=1.0 data/lang_test/tmp/ilabels_3_1 exp/tri5a/tree exp/tri5a/final.mdl 
fstrmepslocal 
fsttablecompose exp/tri5a/graph/Ha.fst data/lang_test/tmp/CLG_3_1.fst 
fstrmsymbols exp/tri5a/graph/disambig_tid.int 
fstdeterminizestar --use-log=true 
fstminimizeencoded 
fstisstochastic exp/tri5a/graph/HCLGa.fst 
0.000487832 -0.178947
HCLGa is not stochastic
add-self-loops --self-loop-scale=0.1 --reorder=true exp/tri5a/final.mdl exp/tri5a/graph/HCLGa.fst 
steps/decode_fmllr.sh --cmd utils/parallel/run.pl --nj 16 --config conf/decode.config exp/tri5a/graph data/dev exp/tri5a/decode_dev
steps/decode.sh --scoring-opts  --num-threads 1 --skip-scoring false --acwt 0.083333 --nj 16 --cmd utils/parallel/run.pl --beam 8.0 --model exp/tri5a/final.alimdl --ma
x-active 2000 exp/tri5a/graph data/dev exp/tri5a/decode_dev.si
decode.sh: feature type is lda
steps/diagnostic/analyze_lats.sh --cmd utils/parallel/run.pl exp/tri5a/graph exp/tri5a/decode_dev.si
steps/diagnostic/analyze_lats.sh: see stats in exp/tri5a/decode_dev.si/log/analyze_alignments.log
Overall, lattice depth (10,50,90-percentile)=(1,2,14) and mean=5.7
steps/diagnostic/analyze_lats.sh: see stats in exp/tri5a/decode_dev.si/log/analyze_lattice_depth_stats.log
+ steps/score_kaldi.sh --cmd utils/parallel/run.pl data/dev exp/tri5a/graph exp/tri5a/decode_dev.si
local/score.sh: line 5: steps/score_kaldi.sh: No such file or directory
steps/decode.sh: Error: scoring failed. (ignore by '--skip-scoring true')
```

<!-- TODO: Output for successful run. -->
