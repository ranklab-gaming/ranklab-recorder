import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'recorder_host': os.getenv('RECORDER_HOST'),
    'recorder_user': os.getenv('RECORDER_USER'),
    'recorder_password': os.getenv('RECORDER_PASSWORD'),
    's3_bucket': os.getenv('S3_BUCKET'),
    'instance_id': os.getenv('INSTANCE_ID'),
    'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
    'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'sqs_queue_url': os.getenv('SQS_QUEUE_URL'),
    'recording_timeout': int(os.getenv('RECORDING_TIMEOUT') or 60 * 60)
}
