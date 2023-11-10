import boto3
import concurrent.futures
import time

session = boto3.Session()

def list_files_in_s3_bucket(bucket_name):
    s3_client = session.client('s3')

    response = s3_client.list_objects(
        Bucket=bucket_name,
        Prefix="clips/",
        MaxKeys=5
    )

    if 'Contents' in response:
        print(len(response['Contents']))
        for file in response['Contents']:
            yield file['Key']

def send_sqs_message(queue_url, bucket_name, key):
    sqs = session.client('sqs')

    message_attributes = {
        's3_bucket_name': {
            'DataType': 'String',
            'StringValue': bucket_name
        },
        'key': {
            'DataType': 'String',
            'StringValue': key
        }
    }

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageAttributes=message_attributes,
        MessageBody="s3 file details"
    )

    return response

def send_messages_for_keys(queue_url, bucket_name, keys):
    for key in keys:
        response = send_sqs_message(queue_url, bucket_name, key)
        print(response)

def main():
    queue_url = 'https://sqs.ap-south-1.amazonaws.com/282118275734/ags-metadata'
    bucket_name = 'raw-audio-files-ags'
    
    # Non-threaded version
    start_time = time.time()
    keys = list(list_files_in_s3_bucket(bucket_name))
    send_messages_for_keys(queue_url, bucket_name, keys)
    end_time = time.time()
    non_threaded_time = end_time - start_time
    print(f"Non-Threaded Execution Time: {non_threaded_time} seconds")

    # Threaded version
    start_time = time.time()
    keys = list(list_files_in_s3_bucket(bucket_name))
    send_messages_for_keys(queue_url, bucket_name, keys)
    end_time = time.time()
    threaded_time = end_time - start_time
    print(f"Threaded Execution Time: {threaded_time} seconds")

if __name__ == "__main__":
    main()
