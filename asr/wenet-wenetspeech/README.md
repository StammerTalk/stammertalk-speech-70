# Wenet Wenetspeech finetuning

We finetuned the Wenetspeech pretrained model with the train and dev splits, and evaluate on the test split.

Please refer to `run.sh` for data preprocessing, finetuning and evaluation. The finetuning config is located in `models/train.yaml`.

## Results

Pretrained model evaluation results: `stats_pretrained.txt`
```
Level     |Category
----------|------------
mild      |all         :	WER=11.45% N= 73745 C= 67300 D=1669 S=4776 I=1999
moderate  |all         :	WER=15.75% N= 28525 C= 25294 D= 851 S=2380 I=1263
severe    |all         :	WER=32.90% N=  9595 C=  8166 D= 442 S= 987 I=1728
all       |conversation:	WER=11.80% N= 71892 C= 66419 D=2683 S=2790 I=3007
all       |command     :	WER=19.05% N= 39973 C= 34341 D= 279 S=5353 I=1983
all       |all         :	WER=14.39% N=111865 C=100760 D=2962 S=8143 I=4990
```

Finetuned model evaluation results: `stats_finetuned.txt`
```
Level     |Category
----------|------------
mild      |all         :	WER= 7.74% N= 73745 C= 69313 D=1149 S=3283 I=1278
moderate  |all         :	WER=10.02% N= 28525 C= 26319 D= 659 S=1547 I= 653
severe    |all         :	WER=18.42% N=  9595 C=  8450 D= 458 S= 687 I= 622
all       |conversation:	WER= 8.54% N= 71892 C= 67763 D=1724 S=2405 I=2008
all       |command     :	WER=10.50% N= 39973 C= 36319 D= 542 S=3112 I= 545
all       |all         :	WER= 9.24% N=111865 C=104082 D=2266 S=5517 I=2553
```

On all levels and categories, the finetuning achieved 35.86% WERR.