from audio_utils import get_audio_stats

audio_file_path = '/Users/architsingh/Documents/projects/asr-call-center/test_set/12.22.wav'
stats = get_audio_stats(audio_file_path)
print(stats)
