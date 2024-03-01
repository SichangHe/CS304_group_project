# Bonus Question

## Decompression

```
cd ~/bonus
unzip dataset_all.zip
tar -zxvf dataset1.tar.gz dataset2.tar.gz dataset3.tar.gz
```

## Dataset1

```shell
# dataset1/corpus/wav/G0013/T0055G0013S0001.wav
# dataset1/corpus/wav/<speaker_id>/<wav_id>.wav
```

The dataset has a total of 70,955 audios, 168 speakers, and the transcribed text is in the dataset1_transcription.txt file.

## Dataset2

```shell
# dataset2/data/wav/C0001/IC0001W0001.wav
# dataset2/data/wav/<speaker_id>/<wav_id>.wav
```

The dataset has a total of 69,261 audios, 139 speakers, and the transcribed text is in the dataset2_transcription.txt file.

## Dataset3

```shell
# dataset3/wav/wav/14_3466/14_3466_20170826171159.wav
# dataset3/data/wav/<speaker_id>/<wav_id>.wav
```

The dataset has a total of 70,234 audios, 126 speakers, and the transcribed text is in the dataset3_transcription.txt file.

## Tools

- Tou can use the utils/subset_data_dir_tr_cv.sh to help divide the train and test set.
