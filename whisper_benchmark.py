import time
import os
from math import ceil

import whisper
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wavpack import WavPack
from mutagen.aiff import AIFF


s = time.time()
model = whisper.load_model(name="tiny", in_memory=True)
result = model.transcribe("conversation.mp3")

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

def get_sample_rate_in_khz(file_path):
    try:
        audio = File(file_path)
        if audio:
            if isinstance(audio, MP3):
                sample_rate_hz = audio.info.sample_rate
            elif isinstance(audio, FLAC):
                sample_rate_hz = audio.info.sample_rate
            elif isinstance(audio, OggVorbis):
                sample_rate_hz = audio.info.sample_rate
            elif isinstance(audio, WavPack):
                sample_rate_hz = audio.info.sample_rate
            elif isinstance(audio, AIFF):
                sample_rate_hz = audio.info.sample_rate
            else:
                return None
            sample_rate_khz = sample_rate_hz / 1000
            return sample_rate_khz
    except Exception as e:
        print("Error:", str(e))
    
    return None


def describe_sample_rate(sample_rate):
    if 44100 <= sample_rate < 48000:
        return "This is the standard sample rate for audio CDs and is often considered 'CD quality.' It's widely used for music distribution and playback."
    elif 48000 <= sample_rate < 96000:
        return "This is a common sample rate for audio in professional video production and digital audio workstations (DAWs)."
    elif 96000 <= sample_rate < 192000:
        return "This higher sample rate is often used in high-resolution audio and professional music recording. It can capture a wide range of frequencies and detail."
    elif 192000 <= sample_rate < 2800000:
        return "This is an even higher sample rate used in some high-end audio recording systems. It can capture extremely high-frequency content and is considered 'studio-quality.'"
    elif sample_rate >= 2800000:
        return "DSD (Direct Stream Digital) uses extremely high sample rates like 2.8 MHz or 5.6 MHz. It's used in Super Audio CDs (SACDs) and is known for its high audio quality."
    else:
        return "sample rate less than 44100"

def classify_bitrate(average_bitrate_kbps):
    if average_bitrate_kbps < 128:
        return "Low Quality"
    elif 128 <= average_bitrate_kbps < 192:
        return "Medium Quality"
    else:
        return "High Quality"

def classify_bitrate_mode(bitrate_mode):
    bitrate_mode = str(bitrate_mode)
    if "CBR" in bitrate_mode:
        return "Constant Bitrate (CBR)"
    elif "VBR" in bitrate_mode:
        return "Variable Bitrate (VBR)"
    else:
        return "Unknown Bitrate Mode"


def get_audio_stats(file_path):
    audio_stats = {}

    audio = File(file_path)

    if audio is not None:
        duration_seconds = audio.info.length
        duration_minutes, duration_seconds = divmod(duration_seconds, 60)
        audio_stats["duration"] = str(duration_minutes) + 'm ' + str(ceil(duration_seconds)) + 's '

        audio_stats["format"] = audio.mime[0] if audio.mime else "Unknown"

        audio_stats["sample_rate"] = audio.info.sample_rate
        description = describe_sample_rate(audio_stats["sample_rate"])
        audio_stats["describe_sample_rate"] = description


        audio_stats["channels"] = audio.info.channels


        file_size_bytes = os.path.getsize(file_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        audio_stats["file_size_mb"] = str(ceil(file_size_mb)) + "MB"


        audio_stats["average_bitrate_kbps"] = audio.info.bitrate / 1000
        classification = classify_bitrate(audio_stats["average_bitrate_kbps"])
        audio_stats["classify_bitrate"] = classification
        
        audio_stats["bitrate_mode"] = audio.info.bitrate_mode
        classification = classify_bitrate_mode(audio_stats["bitrate_mode"])
        audio_stats["classify_bitrate_mode"] = classification
        if 'bitrate' in str(audio.info):
            bit_depth = audio.info.bits_per_sample
            audio_stats["bit_depth"] = bit_depth
        
        audio_stats['audio.info'] = str(audio.info)

        sample_rate_khz = get_sample_rate_in_khz(file_path)
        audio_stats['sample_rate_khz'] = sample_rate_khz

        return audio_stats

    return None

audio_file_path = 'conversation.mp3'
stats = get_audio_stats(audio_file_path)
print(stats)

# 1365 seconds for large
# 34 seconds for tiny
