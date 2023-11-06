import time
from pathlib import Path

from audio_utils import get_audio_stats

import whisper
import pandas as pd


def get_wav_files_in_directory(directory_path):
    directory_path = Path(directory_path)
    wav_file_paths = []

    for wav_file in directory_path.glob("**/*.wav"):
        wav_file_paths.append(wav_file)

    return wav_file_paths

def get_transcription(audio_file_path, model="tiny"):
    model = whisper.load_model(name=model, in_memory=True)
    result = model.transcribe(audio_file_path)
    return result

audio_directory_path = "/Users/architsingh/Documents/projects/asr-call-center/test_set/audio"
wav_files = get_wav_files_in_directory(audio_directory_path)

for audio_file_path in wav_files:
    audio_file_path = str(audio_file_path)
    stats = get_audio_stats(audio_file_path)
    print(stats)
    s = time.time()
    # models = ["tiny", "base", "small", "medium", "large-v1", "large-v2"]
    models = ["tiny"]
    for model in models:
        get_transcription(audio_file_path=audio_file_path, model=model)
    e = time.time()
    print(e-s)
