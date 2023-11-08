"""experiment 2"""
"""multiple threads"""
"""concurrent.futures ThreadPoolExecutor"""

from pathlib import Path
import subprocess
import time
import shutil
import concurrent.futures

def convert_wav(input_file, output_file):
    print(f"running for {input_file}")
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", str(input_file),
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(output_file)
    ]

    subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def convert_all_wav_files(input_folder, output_folder):
    input_folder_path = Path(input_folder)
    output_folder_path = Path(output_folder)

    wav_files = list(input_folder_path.glob("*.wav"))

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for wav_file in wav_files:
            output_file = output_folder_path / f"{wav_file.stem}_converted.wav"
            futures.append(executor.submit(convert_wav, wav_file, output_file))

        concurrent.futures.wait(futures)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Conversion took {elapsed_time:.2f} seconds.")

input_folder = '/Users/architsingh/Documents/projects/sqs-s3-boto3/ffmpeg_benchmark/test_set'
output_folder = '/Users/architsingh/Documents/projects/sqs-s3-boto3/ffmpeg_benchmark/test_set_converted'

if Path(output_folder).exists():
    shutil.rmtree(Path(output_folder))

Path(output_folder).mkdir(parents=True, exist_ok=True)

convert_all_wav_files(input_folder, output_folder)

original_files_count = len(list(Path(input_folder).glob("*.wav")))
converted_files_count = len(list(Path(output_folder).glob("*.wav")))

assert original_files_count == converted_files_count
