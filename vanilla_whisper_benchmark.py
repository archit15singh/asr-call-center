import time
from pathlib import Path

from audio_utils import get_audio_stats

import whisper

def get_wav_files_in_directory(directory_path):
    directory_path = Path(directory_path)
    wav_file_paths = []

    for wav_file in directory_path.glob("**/*.wav"):
        wav_file_paths.append(wav_file)

    return wav_file_paths

def get_transcription(audio_file_path, model="tiny"):
    stats = get_audio_stats(audio_file_path)
    model = whisper.load_model(name=model, in_memory=True, fp16=False)
    result = model.transcribe(audio_file_path)
    return result, stats

audio_directory_path = "/Users/architsingh/Documents/projects/asr-call-center/test_set/audio"
wav_files = get_wav_files_in_directory(audio_directory_path)

for audio_file_path in wav_files:
    audio_file_path = str(audio_file_path)
    s = time.time()
    get_transcription(audio_file_path)
    e = time.time()
    print(e-s)
