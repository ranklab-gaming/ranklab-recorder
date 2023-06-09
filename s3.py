import boto3
from config import config
from log import log


class S3Client:
    def __init__(self):
        self.client = boto3.client('s3', region_name='eu-west-2')

    def upload_video(self, file_path, video_key):
        s3 = boto3.client('s3', region_name='eu-west-2')
        url = s3.generate_presigned_url('put_object', Params={
                                        'Bucket': config['s3_bucket'], 'Key': f'{video_key}'})
        with open(file_path, 'rb') as data:
            log.info(f"Uploading file to {url}")
            s3.upload_fileobj(data, config['s3_bucket'], video_key, ExtraArgs={
                'ACL': 'public-read',
                'ContentType': 'video/mp4',
                'Metadata': {'instance-id': config['instance_id']}
            })
            log.info(f"Finsihed uploading file")
