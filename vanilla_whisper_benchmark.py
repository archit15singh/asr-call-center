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
    model = whisper.load_model(name=model, in_memory=True)
    result = model.transcribe(audio_file_path)
    return result['text']

audio_directory_path = "/Users/architsingh/Documents/projects/asr-call-center/test_set/audio"
wav_files = get_wav_files_in_directory(audio_directory_path)

output_directory = "/Users/architsingh/Documents/projects/asr-call-center/test_set/vanilla_whisper_output"
Path(output_directory).mkdir(parents=True, exist_ok=True)

for audio_file_path in wav_files:
    audio_file_path = str(audio_file_path)
    stats = get_audio_stats(audio_file_path)
    print(stats)
    models = ["tiny.en", "base.en", "small.en", "medium.en", "large-v1", "large-v2"]
    for model in models:
        print(model)
        s = time.time()
        result = get_transcription(audio_file_path=audio_file_path, model=model)
        e = time.time()
        print(e - s)

        model_name = model
        output_file_name = f"{model_name}_{Path(audio_file_path).stem}.txt"
        output_file_path = Path(output_directory) / output_file_name

        with open(output_file_path, 'w') as output_file:
            output_file.write(result)

        print(f"Result saved to: {output_file_path}")
