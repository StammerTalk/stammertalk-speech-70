# Stuttering event detection (SED)

SED is a multi-label multi-class tagging problem. By giving a stuttering speech audio snippet, the system aims to tag five stuttering events:

```
/p: prolongation
/b: block
/r: sound repetition
[]: word repetition
/i: interjection
```

## Data

We prepare the data by cutting long utterances into short snippets. The cut is done on the word time boundaries which have been identified by conducting forced alignment between the audios and the transcriptions.

The dataset contains 41953 audio snippets, of which the average length is 4.19s.

An annotation example:

```
Start,Stop,Category,Prolongation,Block,SoundRep,WordRep,Interjection,Text
104.09,105.68,A,0,0,0,0,0,我是。
106.3,108.94,A,0,0,0,1,0,零三[三]的，
108.94,119.12,A,0,0,1,1,0,口[口/r]吃患者。
119.13,124.49,A,0,0,0,0,0,我是从小就有口吃。
126.46,133.89,A,1,0,0,1,1,到[到]现在，嗯/i/p，一直。
136.61,141.33,A,0,0,0,0,1,伴随我，到我现在那嗯/i。
142.72,149.5,A,1,0,1,0,1,现在我已经工/r作了，嗯/i/p。
```

In Category, we have 3 kinds of labels. `A`: interviewee conversation (person who stutter), `B`: interviewer conversation (also person who stutter), `P`: interviewee command. 

## Results

Random guess
```
        /p      /b      /r      []      /i
Rec:    50.0    51.06   48.96   50.88   49.64
Prec:   11.93   10.24   9.9     33.46   16.85
F1:     19.27   17.06   16.47   40.37   25.16
```

Confomer + sigmoid cross entropy loss  
This is a model with 3 blocks Conformer encoder that is trained with sigmoid cross entropy loss.
Results please check the overleaf paper.
