# -*- coding: utf-8 -*-

import zipfile
import re
import os
import sys
import soundfile as sf
from pathlib import Path

stutter_pattern = r"/[bpri]"
repeat = r"\[[^]]+\]" # match bracket content, include bracket
bracket = r"[\[\]]"
angle = r"\<.+\>"
blank = r"\s+"

def clean_text(text):
  # clean stuttering annotations
  text = re.sub(stutter_pattern, '', text)
  text = re.sub(repeat, '', text)
  text = re.sub(bracket, '', text)
  text = re.sub(angle, '', text)
  text = re.sub(blank, ' ', text) # replace multiple blank
  return text.replace('*', '')

def cut_utt(audio_data, timestamp, sr):
  start = int(timestamp[0] * sr)
  end = int(timestamp[1] * sr)
  return audio_data[start:end]

def parse_annotation(annotation):
  timestamps = []
  with open(annotation) as f:
    for l in f:
      l = l.strip()
      if not l: continue
      start, end, *text = l.split()
      timestamps.append([float(start), float(end), ' '.join(text)])
  return timestamps

def process_utt(data_dir, audio_unzip_dir, cleaned_dir, subdir, audio_file):
  audio_path = audio_unzip_dir / subdir / audio_file
  annotation_path = cleaned_dir / subdir

  corpus_utt_path = data_dir / subdir
  corpus_utt_path.mkdir(exist_ok=True, parents=True)

  audio_data, SR = sf.read(audio_path, dtype='int16')

  assert SR == 16000

  for rootdir, _, annotation_files in os.walk(annotation_path):
    j = 0
    for f in annotation_files:
      if f.startswith('D'):
        if 'A' in f:
          prefix = 'conversation_A'
        elif 'B' in f:
          prefix = 'conversation_B'
        else:
          raise
      else:
        prefix = 'command'
      f = os.path.join(rootdir, f)
      if f.endswith('txt'):
        # annotation starts with D is conversation, otherwise
        # is command
        timestamps = parse_annotation(f)
        for i, timestamp in enumerate(timestamps):
          audio_utt = cut_utt(audio_data, timestamp, SR)
          text = timestamp[-1]
          sf.write(corpus_utt_path / f'{prefix}_{j:04}.wav', audio_utt, SR, 'PCM_16')
          with open(corpus_utt_path / f'{prefix}_{j:04}.txt', 'w') as txt:
            txt.write(text)
          j += 1

if __name__ == '__main__':
  data_dir = sys.argv[1]

  data_dir = Path(data_dir)

  annotation = data_dir / 'annotation_deid_full.zip'
  audio = data_dir / 'audio_deid_full.zip'

  # annotation unzip
  destination_dir = data_dir / 'annotation_unzip'
  destination_dir.mkdir(exist_ok=True)
  # stuttering annotation cleaned
  cleaned_dir = data_dir / 'annotation_cleaned'
  audio_unzip_dir = data_dir / 'audio_unzip'
  audio_unzip_dir.mkdir(exist_ok=True)

  with zipfile.ZipFile(annotation, 'r') as zip_ref:
      zip_ref.extractall(destination_dir)

  with zipfile.ZipFile(audio, 'r') as zip_ref:
      zip_ref.extractall(audio_unzip_dir)

  # Parse annotations
  for dirpath, _, filenames in os.walk(destination_dir):
    for filename in filenames:
      if filename.endswith('.txt'):
        id_ = os.path.basename(dirpath)
        (cleaned_dir / id_).mkdir(exist_ok=True, parents=True)
        bn = os.path.splitext(filename)[0]
        with open(destination_dir / id_ / filename) as f, \
          open(cleaned_dir / id_ / (bn + '.txt'), 'w') as fo:
          for l in f:
            l = l.strip()
            if not l: continue
            start, end, *text = l.split()
            text = ' '.join(text)
            fo.write(f'{start}\t{end}\t{clean_text(text)}\n')

  # loop audio path and save wav and text
  for audio_rootdir, _, audio_files in os.walk(audio_unzip_dir):
    for audio_file in audio_files:
      if audio_file.endswith('.wav'):
        subdir = os.path.basename(audio_rootdir)
        process_utt(data_dir, audio_unzip_dir, cleaned_dir, subdir, audio_file)
