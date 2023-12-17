# StammerTalk-speech-70

This is a collection of speech recordings and transcriptions from 70 Chinese Mandarin speakers. The dataset is intended for speech recognition and analysis tasks.

## Dataset Description

- **Size**: 
- **Format**: WAV and TXT files
- **Language**: Mandarin
- **Source**: The speech recordings are collected by 2 members from StammerTalk [@ronggong](https://github.com/ronggong). The transcriptions are done by [AIShell](www.aishelltech.com).
- **License**: CC BY NC 4.0

## Description of annotation symbols

Please check this [link](https://github.com/StammerTalk/stammertalk-speech-70/blob/main/annotation.md) for the description of annotation symbols, which include the stuttering event symbols, etc.

## Data split

For model building and evaluation, we provide the [train/dev/test split](https://github.com/StammerTalk/stammertalk-speech-70/blob/main/data/level_split.json) based on the stuttering severity level.

## Baseline systems

### ASR
#### Wenetspeech model finetuning

This system is based on [Wenet](https://github.com/wenet-e2e/wenet). We finetuned the Wenetspeech pretrained model with the train and dev splits. Please check [this](https://github.com/StammerTalk/stammertalk-speech-70/blob/main/asr/wenet-wenetspeech/README.md) for futher information on the scripts and results.

## Dataset Citation

If you use this dataset in your research or project, please cite it as follows:

```
@dataset{stamertalk_speech_70_2023,
  title = {StammerTalk-speech-70 Dataset},
  author = {StammerTalk, AImpower, AIShell, Northwestern polytechnical university, Wenet community},
  year = {2023},
  url = {^1^},
  license = {CC BY NC 4.0}
}

```
