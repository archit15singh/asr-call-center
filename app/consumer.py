import boto3
import json
from pathlib import Path
import concurrent.futures


def download_s3_file_to_fs(bucket_name, key, fs_folder_path):
    Path(fs_folder_path).mkdir(parents=True, exist_ok=True)
    s3_client = boto3.client('s3')
    fs_file_name = Path(key).name
    fs_file_path = Path(fs_folder_path) / Path(fs_file_name)
    with open(fs_file_path, 'wb') as f:
        s3_client.download_fileobj(bucket_name, key, f)


def download_files_in_parallel(bucket_name, keys, fs_folder_path):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_s3_file_to_fs, bucket_name, key, fs_folder_path) for key in keys]
        concurrent.futures.wait(futures)


def receive_and_delete_message(queue_url):
    sqs = boto3.client('sqs')

    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
    )

    if 'Messages' in response:
        messages = response['Messages']
        if bool(messages):
            print(len(messages))
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
            download_files_in_parallel(bucket_name, keys, './data')

queue_url = 'https://sqs.ap-south-1.amazonaws.com/282118275734/ags-metadata'
while True:
    receive_and_delete_message(queue_url)













