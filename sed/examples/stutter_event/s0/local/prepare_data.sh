#!/bin/bash

. ./path.sh || exit 1;

if [ $# != 1 ]; then
  echo "Usage: $0 <audio-path>"
  echo " $0 /home/data/stutter_event"
  exit 1;
fi

data_dir=$1
train_dir=data/train
dev_dir=data/dev
test_dir=data/test

mkdir -p $train_dir
mkdir -p $dev_dir
mkdir -p $test_dir

# data directory check
if [ ! -d $aishell_audio_dir ] || [ ! -f $aishell_text ]; then
  echo "Error: $0 requires two directory arguments"
  exit 1;
fi

for split in train dev test; do
  rm data/$split/*
  ids=$(python3 local/get_ids.py $data_dir/level_split.json $split)
  for i in ${ids}; do echo $data_dir/wav/${i}/meeting_01.wav >> data/$split/wav.flist; done
  for i in ${ids}; do echo $data_dir/ref/${i}.csv >> data/$split/ref.flist; done
done

# process train set
sed -e 's/\.csv//' $train_dir/ref.flist | awk -F '/' '{print $NF}' > $train_dir/utt.list
paste -d' ' $train_dir/utt.list $train_dir/wav.flist | sort -u > $train_dir/wav.scp
python3 local/process_segments.py $train_dir 0

sed -e 's/\.csv//' $dev_dir/ref.flist | awk -F '/' '{print $NF}' > $dev_dir/utt.list
paste -d' ' $dev_dir/utt.list $dev_dir/wav.flist | sort -u > $dev_dir/wav.scp
python3 local/process_segments.py $dev_dir 0

sed -e 's/\.csv//' $test_dir/ref.flist | awk -F '/' '{print $NF}' > $test_dir/utt.list
paste -d' ' $test_dir/utt.list $test_dir/wav.flist | sort -u > $test_dir/wav.scp
# discard interviewer
python3 local/process_segments.py $test_dir 1

echo "$0: data preparation succeeded"
exit 0;
