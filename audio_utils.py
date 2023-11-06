from mutagen import File


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
        return audio_stats

    return None

