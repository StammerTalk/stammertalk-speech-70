# Copyright (c) 2020 Mobvoi Inc. (authors: Binbin Zhang, Xiaoyu Chen, Di Wu)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import argparse
import copy
import logging
import os

import torch
import yaml
from torch.utils.data import DataLoader

from wenet.dataset.dataset_sed import Dataset
from wenet.utils.checkpoint import load_checkpoint
from wenet.utils.config import override_config
from wenet.utils.init_model import init_model
from wenet.utils.context_graph import ContextGraph


def get_args():
    parser = argparse.ArgumentParser(description='recognize with your model')
    parser.add_argument('--config', required=True, help='config file')
    parser.add_argument('--test_data', required=True, help='test data file')
    parser.add_argument('--data_type',
                        default='raw',
                        choices=['raw', 'shard'],
                        help='train and cv data type')
    parser.add_argument('--gpu',
                        type=int,
                        default=-1,
                        help='gpu id for this rank, -1 for cpu')
    parser.add_argument('--checkpoint', required=True, help='checkpoint model')
    parser.add_argument('--penalty',
                        type=float,
                        default=0.0,
                        help='length penalty')
    parser.add_argument('--result_dir', required=True, help='asr result file')
    parser.add_argument('--batch_size',
                        type=int,
                        default=16,
                        help='asr result file')
    parser.add_argument('--override_config',
                        action='append',
                        default=[],
                        help="override yaml config")

    args = parser.parse_args()
    print(args)
    return args

def calc_hit_hyp_ref(results, target):
    hit = torch.logical_and(results, target).int().sum(0)
    hyp = results.sum(0)
    ref = target.sum(0)
    return hit, hyp, ref

def calc_rec_prec_f1(hit, hyp, ref):
    def to_string(t):
        return '\t'.join([str(round(r * 100, 2)) for r in t.tolist()])
    rec = hit / ref
    prec = hit / hyp
    f1 = 2 * rec * prec / (rec + prec)
    print('\t/p\t/b\t/r\t/wr\t/i')
    print('Rec:\t'+to_string(rec))
    print('Prec:\t'+to_string(prec))
    print('F1:\t'+to_string(f1))

def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s')
    os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu)

    with open(args.config, 'r') as fin:
        configs = yaml.load(fin, Loader=yaml.FullLoader)
    if len(args.override_config) > 0:
        configs = override_config(configs, args.override_config)

    test_conf = copy.deepcopy(configs['dataset_conf'])

    test_conf['filter_conf']['max_length'] = 102400
    test_conf['filter_conf']['min_length'] = 0
    test_conf['filter_conf']['token_max_length'] = 200
    test_conf['filter_conf']['token_min_length'] = 0
    test_conf['filter_conf']['max_output_input_ratio'] = 102400
    test_conf['filter_conf']['min_output_input_ratio'] = 0
    test_conf['speed_perturb'] = False
    test_conf['spec_aug'] = False
    test_conf['spec_sub'] = False
    test_conf['spec_trim'] = False
    test_conf['shuffle'] = False
    test_conf['sort'] = False
    if 'fbank_conf' in test_conf:
        test_conf['fbank_conf']['dither'] = 0.0
    elif 'mfcc_conf' in test_conf:
        test_conf['mfcc_conf']['dither'] = 0.0
    test_conf['batch_conf']['batch_type'] = "static"
    test_conf['batch_conf']['batch_size'] = args.batch_size
    threshold = 0.25

    test_dataset = Dataset(args.data_type,
                           args.test_data,
                           test_conf,
                           partition=False)

    test_data_loader = DataLoader(test_dataset, batch_size=None, num_workers=0)

    # Init asr model from configs
    model = init_model(configs)

    load_checkpoint(model, args.checkpoint)
    use_cuda = args.gpu >= 0 and torch.cuda.is_available()
    device = torch.device('cuda' if use_cuda else 'cpu')
    model = model.to(device)
    model.eval()

    # TODO(Dinghao Zhou): Support RNN-T related decoding
    # TODO(Lv Xiang): Support k2 related decoding
    # TODO(Kaixun Huang): Support context graph
    files = {}
    #for mode in args.modes:
    #    dir_name = os.path.join(args.result_dir, mode)
    #    os.makedirs(dir_name, exist_ok=True)
    #    file_name = os.path.join(dir_name, 'text')
    #    files[mode] = open(file_name, 'w')
    #max_format_len = max([len(mode) for mode in args.modes])
    with torch.no_grad():
        hit_all = torch.Tensor([0, 0, 0, 0, 0]).to(device)
        hyp_all = torch.Tensor([0, 0, 0, 0, 0]).to(device)
        ref_all = torch.Tensor([0, 0, 0, 0, 0]).to(device)
        for batch_idx, batch in enumerate(test_data_loader):
            keys, feats, target, feats_lengths, target_lengths = batch
            feats = feats.to(device)
            target = target.to(device)
            feats_lengths = feats_lengths.to(device)
            target_lengths = target_lengths.to(device)
            results = model.decode(
                feats,
                feats_lengths)
            results = (results > threshold).int()
            hit, hyp, ref = calc_hit_hyp_ref(results, target)
            hit_all += hit
            hyp_all += hyp
            ref_all += ref
            #logging.info(f'batch: {batch_idx}')

        hit_rand = torch.Tensor([0, 0, 0, 0, 0]).to(device)
        hyp_rand = torch.Tensor([0, 0, 0, 0, 0]).to(device)
        ref_rand = torch.Tensor([0, 0, 0, 0, 0]).to(device)
        for batch_idx, batch in enumerate(test_data_loader):
            keys, feats, target, feats_lengths, target_lengths = batch
            target = target.to(device)
            results = torch.randint(0, 2, target.shape, device=device)
            hit, hyp, ref = calc_hit_hyp_ref(results, target)
            hit_rand += hit
            hyp_rand += hyp
            ref_rand += ref
            #logging.info(f'batch: {batch_idx}')

    calc_rec_prec_f1(hit_all, hyp_all, ref_all)
    calc_rec_prec_f1(hit_rand, hyp_rand, ref_rand)

if __name__ == '__main__':
    main()
