# Wenet Wenetspeech finetuning

We finetuned the Wenetspeech pretrained model with the train and dev splits, and evaluate on the test split.

Please refer to `run.sh` for data preprocessing, finetuning and evaluation. The finetuning config is located in `models/train.yaml`.

## Results

Pretrained model evaluation results: `stats_pretrained.txt`
```
Level     |Category
----------|------------
mild      |all         :	WER=11.41% N= 64095 C= 58821 D= 982 S=4292 I=2042
moderate  |all         :	WER=17.81% N= 22143 C= 19251 D= 509 S=2383 I=1051
severe    |all         :	WER=33.21% N=  9204 C=  7988 D= 274 S= 942 I=1841
all       |conversation:	WER=11.82% N= 60099 C= 56098 D=1540 S=2461 I=3105
all       |command     :	WER=20.40% N= 35343 C= 29962 D= 225 S=5156 I=1829
all       |all         :	WER=15.00% N= 95442 C= 86060 D=1765 S=7617 I=4934
```

Finetuned model evaluation results: `stats_finetuned.txt`
```
Level     |Category
----------|------------
mild      |all         :	WER= 8.00% N= 64095 C= 60136 D=1117 S=2842 I=1169
moderate  |all         :	WER=12.48% N= 22143 C= 19902 D= 647 S=1594 I= 523
severe    |all         :	WER=17.29% N=  9204 C=  8084 D= 492 S= 628 I= 471
all       |conversation:	WER= 9.16% N= 60099 C= 56332 D=1741 S=2026 I=1741
all       |command     :	WER=11.25% N= 35343 C= 31790 D= 515 S=3038 I= 422
all       |all         :	WER= 9.94% N= 95442 C= 88122 D=2256 S=5064 I=2163
```

On all levels and categories, the finetuning achieved 35.73% WERR.