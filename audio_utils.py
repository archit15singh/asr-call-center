import os

from mutagen import File

def get_audio_file_size_mb(audio_file_path):
    audio_file_path = str(audio_file_path)
    
    if not os.path.exists(audio_file_path):
        return None
    
    file_size_bytes = os.path.getsize(audio_file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    return file_size_mb


def get_audio_stats(file_path):
    audio_stats = {}

    audio = File(file_path)

    if audio is not None:
        props = [prop for prop in dir(audio.info) if '__' not in prop]
        for prop in props:
            audio_stats[prop] = getattr(audio.info, prop)
        
        audio_stats['length'] = audio_stats['length'] / 60
        formatted_length = "{:.2f}".format(audio_stats['length'])
        audio_stats['length'] = formatted_length
        audio_stats.pop('pprint')
        
        file_size_mb = get_audio_file_size_mb(file_path)
        file_size_mb = "{:.2f}".format(file_size_mb) + " MB"
        audio_stats['file_size_mb'] = file_size_mb
        
        return audio_stats

    return None

