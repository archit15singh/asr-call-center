import boto3
import json
from pathlib import Path
import concurrent.futures
import subprocess
import time


def transcribe_folder(input_folder: str, output_folder) -> None:
    input_folder_path = Path(input_folder)
    output_folder_path = Path(output_folder)

    for wav_file in input_folder_path.glob("*.wav"):
        transcribe(wav_file, output_folder_path)
    else:
        print("completed transcibe")


def transcribe(input_file: Path, output_folder: Path) -> None:
    output_path = output_folder / f"{input_file.stem}"
    model = "whisper.cpp/models/ggml-medium.en.bin"

    command_list = [
        "whisper.cpp/main",
        "-f", str(input_file),
        "-m", model,
        "-oj",
        "-of", str(output_path)
    ]
    print(command_list)
    subprocess.run(command_list, check=True)

    input_file.unlink()

def convert_wav(input_file, output_file):
    try:
        print(f"Converting {input_file.stem}...")
        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-i", str(input_file),
            "-ar", "16000",
            "-c:a", "pcm_s16le",
            str(output_file)
        ]

        subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Conversion of {input_file.stem} completed.")

        input_file.unlink()
        print(f"Deleted original file: {input_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file.stem}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def convert_all_wav_files(input_folder, output_folder):
    input_folder_path = Path(input_folder)
    output_folder_path = Path(output_folder)

    wav_files = list(input_folder_path.glob("*.mp3"))

    if not wav_files:
        print("completed conversion")
        return

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for wav_file in wav_files:
            output_file = output_folder_path / f"{wav_file.stem}_converted.wav"
            futures.append(executor.submit(convert_wav, wav_file, output_file))

        concurrent.futures.wait(futures)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nConversion of all WAV files took {elapsed_time:.2f} seconds.")
    print(f"Original files count: {len(wav_files)}")
    print(f"Converted files count: {len(list(output_folder_path.glob('*.wav')))}")


def download_s3_file_to_fs(bucket_name, key, fs_folder_path):
    s3_client = boto3.client('s3')
    fs_file_name = Path(key).name
    fs_file_path = Path(fs_folder_path) / Path(fs_file_name)
    with open(fs_file_path, 'wb') as f:
        s3_client.download_fileobj(bucket_name, key, f)


def download_files_in_parallel(bucket_name, keys, fs_folder_path):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_s3_file_to_fs, bucket_name, key, fs_folder_path) for key in keys]
        concurrent.futures.wait(futures)


def download(queue_url, folder):
    sqs = boto3.client('sqs')

    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
    )
    if 'Messages' not in response:
        return False
    
    if 'Messages' in response:
        messages = response['Messages']
        if bool(messages):
            print(len(messages))
        else:
            return False
        bucket_name = ""
        keys = []
        for message in messages:
            # print(message['MessageId'])
            body_dict = json.loads(message['Body'])
            
            # take this two and call function download_files_in_parallel
            if not bool(bucket_name):
                bucket_name = body_dict['s3_bucket_name']
            keys.append(body_dict['key'])
            
            receipt_handle = message['ReceiptHandle']
            # print('Received message: %s' % body_dict)

            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            # print('Deleted message: %s' % message)
        
        
        if bool(keys):
            print(keys)
            download_files_in_parallel(bucket_name, keys, folder)
        return True


queue_url = 'https://sqs.ap-south-1.amazonaws.com/282118275734/ags-metadata'

while True:
    download(queue_url, folder='./data')
    input_folder = './data'
    output_folder = './converted'
    convert_all_wav_files(input_folder, output_folder)
    input_folder = './converted'
    output_folder = './transcriptions'
    transcribe_folder(input_folder, output_folder)
