import time

import whisper

s = time.time()
model = whisper.load_model(name="tiny", in_memory=True)
result = model.transcribe("/Users/architsingh/Documents/projects/asr-call-center/test_set/12.22.wav")

for data in result['segments']:
    start = data['start']
    end = data['end']
    text = data['text']

    start_minutes, start_seconds = divmod(int(start), 60)
    end_minutes, end_seconds = divmod(int(end), 60)

    print(f"Start: {start_minutes} minutes {start_seconds} seconds")
    print(f"End: {end_minutes} minutes {end_seconds} seconds")
    print(f"Text: {text}\n")
e = time.time()
print(e-s)
