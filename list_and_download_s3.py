import boto3
from pathlib import Path
import concurrent.futures
import time

def list_files_in_s3_bucket(bucket_name):
    s3_client = boto3.client('s3')

    response = s3_client.list_objects(
        Bucket=bucket_name,
        Prefix="clips/",
        MaxKeys=5
    )

    if 'Contents' in response:
        print(len(response['Contents']))
        for file in response['Contents']:
            yield file['Key']

def download_s3_file_to_fs(bucket_name, key, fs_folder_path):
    Path(fs_folder_path).mkdir(parents=True, exist_ok=True)
    s3_client = boto3.client('s3')
    fs_file_name = Path(key).name
    fs_file_path = Path(fs_folder_path) / Path(fs_file_name)
    with open(fs_file_path, 'wb') as f:
        s3_client.download_fileobj(bucket_name, key, f)

def download_files_serially(bucket_name, keys, fs_folder_path):
    for key in keys:
        download_s3_file_to_fs(bucket_name, key, fs_folder_path)

def download_files_in_parallel(bucket_name, keys, fs_folder_path):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_s3_file_to_fs, bucket_name, key, fs_folder_path) for key in keys]
        concurrent.futures.wait(futures)

def measure_time(func, *args):
    s = time.time()
    func(*args)
    e = time.time()
    return e - s

bucket_name = 'raw-audio-files-ags'
keys = list(list_files_in_s3_bucket(bucket_name))

serial_time = measure_time(download_files_serially, bucket_name, keys, './data')
parallel_time = measure_time(download_files_in_parallel, bucket_name, keys, './data')

print(f"Serial Execution Time: {serial_time}")
print(f"Parallel Execution Time: {parallel_time}")
print(f"Speedup: {serial_time / parallel_time:.2f}x")
