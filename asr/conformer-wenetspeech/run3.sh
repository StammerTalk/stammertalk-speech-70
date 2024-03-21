#!/bin/bash

# semantic level_split2.json

stage=0
stop_stage=5

. src/tools/parse_options.sh || exit 1;

# wenet git repo clone
wenet=/fs/scratch/users/rong_gong/2021/wenet

# Entire repo local dir, which should contain ./asr/wenet-wenetspeech and ./data
project_dir=/fs/scratch/users/rong_gong/2023/dax/is2023

# contain audio_deid_full.zip and annotation_deid_full.zip
raw_data_dir=/fs/data/users/rong_gong/is2024

# utts data dir
utts_data_dir=$project_dir/data_verbatim

# train/dev/test
par=$project_dir/data/level_split2.json

exp=wenetspeech_stutter_verbatim

cw_dir=$project_dir/asr/conformer-wenetspeech
data_dir=$cw_dir/data_verbatim
model_dir=$cw_dir/models

# download wenetspeech pretrained checkpoint model from
# https://github.com/wenet-e2e/wenet/blob/main/docs/pretrained_models.en.md
# copy the model into $model_dir

if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
    # prepare utterance data
    python3 src/prepare_utts.py $raw_data_dir $utts_data_dir --verbatim
fi

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    # process wav.scp and text
    mkdir -p $data_dir

    for split in train dev; do
        rm -r $data_dir/$split
        mkdir -p $data_dir/$split
        ids=$(python3 src/get_ids.py $par $split)
        for i in ${ids}; do find $utts_data_dir/${i} -name '*.wav' -exec sh -c 'for f do echo "$(echo ${f%.*}) $(echo $f)"; done' sh {} + >> $data_dir/$split/wav.scp; done
        for i in ${ids}; do find $utts_data_dir/${i} -name '*.txt' -exec sh -c 'for f do echo "$(echo ${f%.*}) $(cat $f)"; done' sh {} + >> $data_dir/$split/text; done
    done

    rm -r $data_dir/test
    mkdir -p $data_dir/test
    ids=$(python3 src/get_ids.py $par test)
    # only take conversation_A*.wav and command*.wav as test sets
    for i in ${ids}; do find $utts_data_dir/${i} -name 'conversation_A*.wav' -exec sh -c 'for f do echo "$(echo ${f%.*}) $(echo $f)"; done' sh {} + >> $data_dir/test/wav.scp; done
    for i in ${ids}; do find $utts_data_dir/${i} -name 'command*.wav' -exec sh -c 'for f do echo "$(echo ${f%.*}) $(echo $f)"; done' sh {} + >> $data_dir/test/wav.scp; done
    for i in ${ids}; do find $utts_data_dir/${i} -name 'conversation_A*.txt' -exec sh -c 'for f do echo "$(echo ${f%.*}) $(cat $f)"; done' sh {} + >> $data_dir/test/text; done
    for i in ${ids}; do find $utts_data_dir/${i} -name 'command*.txt' -exec sh -c 'for f do echo "$(echo ${f%.*}) $(cat $f)"; done' sh {} + >> $data_dir/test/text; done

    # remove punctuation from text since Wenet model doesn't produce them
    # filter long utterances
    python3 src/clean_scp.py $data_dir $data_dir/filter.log
fi

if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    # prepare wenet data.list
    rm -r $wenet/examples/$exp/s0/exp
    mkdir -p $wenet/examples/$exp/s0/exp
    tar -xzf $model_dir/wenetspeech_u2pp_conformer_exp.tar.gz -C $wenet/examples/$exp/s0/exp/
    cp -r $wenet/examples/$exp/s0/exp/20220506_u2pp_conformer_exp $wenet/examples/$exp/s0/exp/20220506_u2pp_conformer_exp_finetune

    mkdir $wenet/examples/$exp/s0/data
    for split in train dev test; do
        cp -r $data_dir/$split $wenet/examples/$exp/s0/data/
    done

    cp $wenet/examples/aishell/s0/run.sh $wenet/examples/$exp/s0/
    cp $wenet/examples/aishell/s0/path.sh $wenet/examples/$exp/s0/
    ln -s $wenet/examples/aishell/s0/conf $wenet/examples/$exp/s0/
    ln -s $wenet/examples/aishell/s0/local $wenet/examples/$exp/s0/
    ln -sf $wenet/wenet $wenet/examples/$exp/s0/
    ln -sf $wenet/tools $wenet/examples/$exp/s0/

    cd $wenet/examples/$exp/s0 && bash ./run.sh --stage 3 --stop_stage 3
fi

if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    # test pretrained model
    cd $wenet/examples/$exp/s0 && export exp_dir=exp/20220506_u2pp_conformer_exp && bash ./run.sh --stage 5 --stop_stage 5 --average_checkpoint false --dir $exp_dir --dict $exp_dir/units.txt --decode_checkpoint $exp_dir/final.pt --decode_modes "attention_rescoring"
    exp_dir=$wenet/examples/$exp/s0/exp/20220506_u2pp_conformer_exp
    cd $cw_dir && python3 src/stats.py $exp_dir/attention_rescoring $par $exp_dir/attention_rescoring/stats.txt
fi

if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
    # fine-tune pretrained model
    # We need to change resource type to GPU
    # modify $wenet/examples/$exp/s0/run.sh
    #  export CUDA_VISIBLE_DEVICES="0"
    # modify $wenet/examples/$exp/s0/exp/20220506_u2++_conformer_exp_finetune/train.yaml
    #  max_epoch: 5
    #  optim_conf:
    #   lr: 1.0e-05
    #  scheduler: NoamHoldAnnealing
    #  scheduler_conf:
    #   hold_steps: 25000
    #   max_steps: null
    #   min_lr: 1.0e-05
    #   warmup_steps: 1

    sed -i 's/export CUDA_VISIBLE_DEVICES="0,1,2,3,4,5,6,7"/export CUDA_VISIBLE_DEVICES="0"/g' $wenet/examples/$exp/s0/run.sh
    cp $model_dir/train.yaml $wenet/examples/$exp/s0/exp/20220506_u2pp_conformer_exp_finetune/
    cd $wenet/examples/$exp/s0 && export exp_dir=$wenet/examples/$exp/s0/exp/20220506_u2pp_conformer_exp_finetune && cp $exp_dir/global_cmvn data/train/ && bash ./run.sh --stage 4 --stop_stage 4 --average_checkpoint false --dir $exp_dir --dict $exp_dir/units.txt --checkpoint $exp_dir/final.pt --train_config $exp_dir/train.yaml
fi

if [ ${stage} -le 5 ] && [ ${stop_stage} -ge 5 ]; then
    # test finetuned model
    cd $wenet/examples/$exp/s0 && export exp_dir=exp/20220506_u2pp_conformer_exp_finetune && bash ./run.sh --stage 5 --stop_stage 5 --average_checkpoint true --dir $exp_dir --dict $exp_dir/units.txt --decode_checkpoint $exp_dir/200.pt --decode_modes "attention_rescoring"
    exp_dir=$wenet/examples/$exp/s0/exp/20220506_u2pp_conformer_exp_finetune
    cd $cw_dir && python3 src/stats.py $exp_dir/attention_rescoring $par $exp_dir/attention_rescoring/stats.txt
fi
