import boto3
import concurrent.futures

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
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(send_sqs_message, queue_url, bucket_name, key) for key in keys]
        for future in concurrent.futures.as_completed(futures):
            response = future.result()
            print(response)

def main():
    queue_url = 'https://sqs.ap-south-1.amazonaws.com/282118275734/ags-metadata'
    bucket_name = 'raw-audio-files-ags'
    
    keys = list(list_files_in_s3_bucket(bucket_name))
    
    send_messages_for_keys(queue_url, bucket_name, keys)

if __name__ == "__main__":
    main()
