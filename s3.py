import boto3
from config import config
from log import log


class S3Client:
    def __init__(self):
        self.client = boto3.client("s3", region_name="eu-west-2")

    def upload_video(self, file_path, video_key):
        s3 = boto3.client("s3", region_name="eu-west-2")
        url = s3.generate_presigned_url(
            "put_object", Params={"Bucket": config["s3_bucket"], "Key": f"{video_key}"}
        )
        with open(file_path, "rb") as data:
            log.info(f"Uploading {file_path} to {config['s3_bucket']}/{video_key}")
            args = {
                "ACL": "public-read",
                "ContentType": "video/mp4",
            }
            if config["instance_id"]:
                args["Metadata"] = {"instance-id": config["instance_id"]}
            s3.upload_fileobj(
                data,
                config["s3_bucket"],
                video_key,
                ExtraArgs=args,
            )
            log.info("Finsihed uploading file")
