# Quick Start

## AISHELL-1 Introduction

Aishell is an open-source Chinese Mandarin speech corpus published by Beijing Shell Shell Technology Co.,Ltd.

[OpenSLR](http://www.openslr.org/33/)

[AISHELL-ASR0009-OS1 Open Source Mandarin Speech Corpus](http://www.aishelltech.com/kysjcp)

## Preparation

- Step 1. We recommend you to copy the egs from the original kaldi folder.

```shell
cd ~
mkdir -p project7
cp -r /home/vcm/kaldi/egs/aishell project7/
```

- Step 2. Delete the previous soft links to "steps" and "utils" and copy the folders directly here.

```shell
cd /home/vcm/project7/aishell/s5
rm steps utils
cp -r /home/vcm/kaldi/egs/wsj/s5/steps .
cp -r /home/vcm/kaldi/egs/wsj/s5/utils .
```

- Step 3. Change the path.sh and cmd.sh.

```shell
# path.sh file
# comment the original KALDI_ROOT variance.

# export KALDI_ROOT=`pwd`/../../..
export KALDI_ROOT=/home/vcm/kaldi
[ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export LC_ALL=C
```

```shell
# cmd.sh file

# export train_cmd="queue.pl --mem 2G"
# export decode_cmd="queue.pl --mem 4G"
# export mkgraph_cmd="queue.pl --mem 8G"
export train_cmd="run.pl"
export decode_cmd="run.pl"
export mkgraph_cmd="run.pl"
```

- Step 4. Change the run.sh to set the aishell path and comment the DNN training.

```shell
# run.sh file

# data=/export/a05/xna/data
data=/home/vcm/AISHELL-1

# ....codes....

# nnet3
# local/nnet3/run_tdnn.sh

# chain
# local/chain/run_tdnn.sh

# ....codes....
```

- Step 5. Start the aishell script.

```shell
./run.sh

# or bash ./run.sh

# or chmod +x run.sh 
# then run.sh
```

## Training Duration

The whole training process of HMM-GMM for aishell1 may take up to 7 hours.
