import boto3
import concurrent.futures
import json
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION")
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL")
INPUT_S3_BUCKET_NAME = os.environ.get("INPUT_S3_BUCKET_NAME")

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

def list_files_in_s3_bucket(bucket_name):
    try:
        s3_client = session.client('s3')
        response = s3_client.list_objects(
            Bucket=bucket_name,
            Prefix="clips/",
            MaxKeys=10
        )

        if 'Contents' in response:
            logger.info(f"Found {len(response['Contents'])} files in the bucket.")
            for file in response['Contents']:
                yield file['Key']
    except Exception as e:
        logger.error(f"Error listing files in S3 bucket: {e}")

def send_sqs_message(queue_url, bucket_name, key):
    try:
        sqs = session.client('sqs')
        body = {
            's3_bucket_name': bucket_name,
            'key': key,
        }

        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(body)
        )

        return response
    except Exception as e:
        logger.error(f"Error sending SQS message: {e}")

def send_messages_for_keys(queue_url, bucket_name, keys):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(send_sqs_message, queue_url, bucket_name, key) for key in keys]
        for future in concurrent.futures.as_completed(futures):
            response = future.result()
            # print(response)

def main():
    try:
        keys = list(list_files_in_s3_bucket(INPUT_S3_BUCKET_NAME))
        logger.info(f"Processing {len(keys)} keys from S3 bucket.")
        send_messages_for_keys(SQS_QUEUE_URL, INPUT_S3_BUCKET_NAME, keys)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
