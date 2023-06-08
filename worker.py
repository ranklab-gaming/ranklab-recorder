import json
import os
import subprocess
import boto3
import time
import ui
import pyautogui
from games import games
from dotenv import load_dotenv
import paramiko

load_dotenv()

recorder_host = os.getenv('RECORDER_HOST')
recorder_user = os.getenv('RECORDER_USER')
recorder_password = os.getenv('RECORDER_PASSWORD')
s3_bucket = os.getenv('S3_BUCKET')
instance_id = os.getenv('INSTANCE_ID')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
sqs_queue_url = os.getenv('SQS_QUEUE_URL')
recording_timeout = int(os.getenv('RECORDING_TIMEOUT') or 60 * 60)

sqs = boto3.client('sqs', 
                   region_name='eu-west-2',
                   aws_access_key_id=aws_access_key_id,
                   aws_secret_access_key=aws_secret_access_key)

def record(body):
    recording_id = body.get('recording_id')
    game_id = body.get('game_id')
    game = games[game_id]
    video_key = body.get('video_key')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"Connecting to {recorder_host} via SSH")
    client.connect(hostname=recorder_host, username=recorder_user, password=recorder_password)

    print(f"Starting RDP session on {recorder_host}")

    rdp_process = subprocess.Popen([
        "xfreerdp",
        f"/u:{recorder_user}",
        f"/p:{recorder_password}",
        f"/v:{recorder_host}",
        "/cert-ignore",
        "/log-level:FATAL",
        "/f",
        "/w:1280",
        "/h:720",
        "/network:lan",
        "/rfx",
        "/audio-mode:1"
    ])

    def ssh(*cmd):
        print(f"Running SSH command: {' '.join(cmd)}")
        _, stdout, _ = client.exec_command(' '.join(cmd))
        stdout.channel.recv_exit_status()

    def psexec(*cmd):
        ssh("psexec64", "-i", "2", "-u", recorder_user, "-p", recorder_password, "-d", *cmd)

    def psexec_wait(*cmd):
        ssh("psexec64", "-i", "2", "-u", recorder_user, "-p", recorder_password, *cmd)

    def kill(*cmd):
        ssh("taskkill", "/IM", *cmd, "/F")

    def focus_window(title):
        psexec(f"\"nircmd.exe\" win activate title {title}")
        psexec(f"\"nircmd.exe\" win settopmost title {title} 1")
        print(f"Focused window {title}")

    def hide_window(title):
        psexec(f"\"nircmd.exe\" win hide title {title}")
        print(f"Hid window {title}")

    try:
        game["stop"](kill)
        print("Stopped previously running game instances")

        ssh("del", f"C:\\Users\\{recorder_user}\\Videos\\{recording_id}.mp4")
        print(f"Deleted previous recording {recording_id}.mp4")

        psexec("cmd.exe", "/C", "start", "\"\"", f"\"{game['exe_path']}\"")
        print(f"Started {game['exe_path']}")

        game["after_start"]()
        print(f"Executed after start commands")

        focus_window(game["window_title"])

        game["before_recording"](body)
        print(f"Prepared game for recording")

        psexec("\"C:\\ranklab-windows\\ranklab-windows.exe\"", f"{recording_id}.mp4")
        print(f"Started recording {recording_id}.mp4")
        hide_window("C:\\ranklab-windows\\ranklab-windows.exe")
        focus_window(game["window_title"])
        
        start_time = time.time()
        while True:
            if time.time() > start_time + recording_timeout:
                print(f"Recording timed out after {recording_timeout}s")
                break
            if ui.find_element(f"{game_id}/{game['recording_ended_element']}"):
                print(f"Game ended")
                break
            time.sleep(1)

        psexec_wait("\"taskkill\"", "/IM", "ranklab-windows.exe")
        print("Stopped recording")

        game["stop"](kill)
        print("Stopped game instance")

        print(f"Copying recording from remote machine")
        sftp = client.open_sftp()
        sftp.get(f"C:\\Users\\{recorder_user}\\Videos\\{recording_id}.mp4", f"/tmp/{recording_id}")
        sftp.close()
        print(f"Copied recording to /tmp/{recording_id}")

        # Generate presigned S3 url
        s3 = boto3.client('s3', region_name='eu-west-2')
        url = s3.generate_presigned_url('put_object', Params={'Bucket': s3_bucket, 'Key': f'{video_key}'})

        # Upload file to bucket
        with open(f"/tmp/{recording_id}", 'rb') as data:
            print(f"Uploading recording to {url}")

            s3.upload_fileobj(data, s3_bucket, video_key, ExtraArgs={
                'ACL': 'public-read',
                'ContentType': 'video/mp4',
                'Metadata': {'instance-id': instance_id}
            })

            print(f"Finsihed uploading recording")
    except Exception as e:
        print(f"Taking screenshot of error: {e}")
        pyautogui.screenshot(f"/tmp/error.png")
        raise e
    finally:
        if rdp_process is not None:
            rdp_process.terminate()
            rdp_process.wait()
            print(f"Killed RDP session")

        client.close()
        print(f"Closed SSH connection")
    print(f"Finished recording {recording_id}!")

def poll_queue():
    while True:
        try:
            messages = sqs.receive_message(QueueUrl=sqs_queue_url, MaxNumberOfMessages=1)
            
            if 'Messages' in messages:  # when the queue is exhausted, the response dict contains no 'Messages' key
                for message in messages['Messages']:  # 'Messages' is a list
                    body = json.loads(message['Body'])

                    if body.get('instance_id') != instance_id:
                        # Set visibility timeout to 0 to make it immediately available to other consumers
                        sqs.change_message_visibility(QueueUrl=sqs_queue_url, ReceiptHandle=message['ReceiptHandle'], VisibilityTimeout=0)
                        print(f"Instance ID does not match. Message returned to queue for other instances to process.")
                        time.sleep(5)
                    else:
                        record(body)
                        # next, we delete the message from the queue so no one else will process it again
                        sqs.delete_message(QueueUrl=sqs_queue_url, ReceiptHandle=message['ReceiptHandle'])
            else:
                time.sleep(5)  # sleep for a while then keep polling the sqs queue
        except Exception as e:
            print(f"Error polling queue: {e}")

if __name__ == "__main__":
    print(f"Worker started. Instance ID: {instance_id}")
    poll_queue()
