from celery import Celery, current_task
import json
import os
import subprocess
import boto3
import time
from dotenv import load_dotenv

load_dotenv()

broker_url = os.getenv('BROKER_URL')
recorder_host = os.getenv('RECORDER_HOST')
recorder_user = os.getenv('RECORDER_USER')
recorder_password = os.getenv('RECORDER_PASSWORD')
s3_bucket = os.getenv('S3_BUCKET')
instance_id = os.getenv('INSTANCE_ID')

app = Celery('tasks', broker=broker_url, concurrency=1)

@app.task
def record(message):
    body = json.loads(message.get('Body', ''))

    if body.get('instance_id') != instance_id:
        # Requeue task to give other instances a chance to pick it up
        current_task.apply_async(args=[message])

        # Sleep to avoid immediately picking up the requeued task
        time.sleep(10)
        return
    
    # Create a virtual framebuffer with xvfb
    subprocess.run(["Xvfb", ":1", "-screen", "0", "1024x768x24"])
    subprocess.run(["export", "DISPLAY=:1"])

    import ui
    import games

    recording_id = body.get('recording_id')
    game = games[body.get('game_id')]
    video_key = body.get('video_key')


    # Start rdp session
    subprocess.run(["xfreerdp", f"/u:{recorder_user}", f"/p:{recorder_password}", f"/v:{recorder_host}"])

    # Execute psexec commands through ssh
    ssh_cmd =  ["sshpass", "-p", recorder_password, "ssh", f"{recorder_user}@{recorder_host}"]
    start_cmd = ssh_cmd + ["psexec", "-i", "-d", "cmd.exe", "start", ""]
    kill_cmd = ssh_cmd + ["taskkill", "/IM"]
    subprocess.run(start_cmd + [game["exe_path"]])

    # Start recording
    game["before_recording"](body)
    subprocess.run(start_cmd + ["ranklab-windows.exe", f"{recording_id}.mp4"])

    # Wait for recording to end
    while True:
        if ui.find_element(game["recording_ended_element"]):
            break
        time.sleep(1)

    # Stop recording
    subprocess.run(kill_cmd + ["ranklab-windows.exe"])
    game["after_recording"](kill_cmd)

    # Copy file from remote machine
    subprocess.run(["scp", f"{recorder_user}@{recorder_host}:C:\\Users\\{recorder_user}\\Videos\\{recording_id}", f"/tmp/{recording_id}"])

    # Generate presigned S3 url
    s3 = boto3.client('s3', region_name='eu-west-2')
    url = s3.generate_presigned_url('put_object', Params={'Bucket': s3_bucket, 'Key': f'{video_key}'})

    # Upload file to bucket
    with open(f"/tmp/{recording_id}", 'rb') as data:
        subprocess.run(["aws", "s3", "cp", "-", url], stdin=data)
