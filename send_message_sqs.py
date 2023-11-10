import boto3

def send_sqs_message(queue_url, bucket_name, key):
    sqs = boto3.client('sqs')

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
        DelaySeconds=10,
        MessageAttributes=message_attributes,
        MessageBody="s3 file details"
    )

    return response

def main():
    queue_url = 'https://sqs.ap-south-1.amazonaws.com/282118275734/ags-metadata'
    bucket_name = 'raw-audio-files-ags'
    key = 'clips/common_voice_en_38024628.mp3'

    response = send_sqs_message(queue_url, bucket_name, key)
    print(response)

if __name__ == "__main__":
    main()
