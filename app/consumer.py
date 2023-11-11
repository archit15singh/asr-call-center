import boto3
import json
from pathlib import Path
import concurrent.futures
import subprocess
import time
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION")
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL")
INPUT_S3_BUCKET_NAME = os.environ.get("INPUT_S3_BUCKET_NAME")
OUTPUT_S3_BUCKET_NAME = os.environ.get("OUTPUT_S3_BUCKET_NAME")
RAW_FOLDER = os.environ.get("RAW_FOLDER", "./data")
CONVERSION_OUTPUT_FOLDER = os.environ.get("CONVERSION_OUTPUT_FOLDER", "./converted")
TRANSCRIPTION_OUTPUT_FOLDER = os.environ.get("TRANSCRIPTION_OUTPUT_FOLDER", "./transcriptions")


def upload_file_to_s3(file_path, bucket_name, s3_object_key):
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    s3 = session.client('s3')
    
    with open(file_path, "rb") as f:
        s3.upload_fileobj(f, bucket_name, s3_object_key)
    
    os.remove(file_path)


def upload_folder_to_s3(folder_path, bucket_name, s3_prefix=''):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith('.json'):
                    local_file_path = os.path.join(root, file_name)
                    s3_object_key = os.path.join(s3_prefix, file_name)
                    
                    future = executor.submit(upload_file_to_s3, local_file_path, bucket_name, s3_object_key)
                    futures.append(future)

        concurrent.futures.wait(futures)
        

def transcribe_folder(input_folder: str, output_folder) -> None:
    input_folder_path = Path(input_folder)
    output_folder_path = Path(output_folder)

    for wav_file in input_folder_path.glob("*.wav"):
        transcribe(wav_file, output_folder_path)
    else:
        print("completed transcribe")


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
            body_dict = json.loads(message['Body'])
            
            if not bool(bucket_name):
                bucket_name = body_dict['s3_bucket_name']
            keys.append(body_dict['key'])
            
            receipt_handle = message['ReceiptHandle']

            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
        
        
        if bool(keys):
            print(keys)
            download_files_in_parallel(bucket_name, keys, folder)
        return True


while True:
    download(SQS_QUEUE_URL, folder=RAW_FOLDER)
    
    input_folder = RAW_FOLDER
    output_folder = CONVERSION_OUTPUT_FOLDER
    convert_all_wav_files(input_folder, output_folder)
    
    input_folder = CONVERSION_OUTPUT_FOLDER
    output_folder = TRANSCRIPTION_OUTPUT_FOLDER
    transcribe_folder(input_folder, output_folder)
    
    upload_folder_to_s3(TRANSCRIPTION_OUTPUT_FOLDER, OUTPUT_S3_BUCKET_NAME)
