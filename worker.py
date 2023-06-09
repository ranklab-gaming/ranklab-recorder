import json
import os
import signal
import sys
import boto3
import time
from rdp import RDPClient
from s3 import S3Client
import ui
import pyautogui
from games import games
from config import config
from ssh import SSHClient
from log import log


root_dir = os.path.dirname(os.path.abspath(__file__))


class Worker:
    def __init__(self):
        self.sqs_client = boto3.client('sqs',
                                       region_name='eu-west-2',
                                       aws_access_key_id=config['aws_access_key_id'],
                                       aws_secret_access_key=config['aws_secret_access_key'])

    def poll_queue(self):
        log.info(f"Worker started. Instance ID: {config['instance_id']}")
        while True:
            try:
                messages = self.sqs_client.receive_message(
                    QueueUrl=config['sqs_queue_url'], MaxNumberOfMessages=1)
                if 'Messages' in messages:
                    for message in messages['Messages']:
                        body = json.loads(message['Body'])
                        if body.get('instance_id') != config['instance_id']:
                            self.sqs_client.change_message_visibility(
                                QueueUrl=config['sqs_queue_url'], ReceiptHandle=message['ReceiptHandle'], VisibilityTimeout=0)
                            log.info(
                                f"Instance ID does not match. Message returned to queue for other instances to process.")
                            time.sleep(5)
                        else:
                            self._record(body)
                            self.sqs_client.delete_message(
                                QueueUrl=config['sqs_queue_url'], ReceiptHandle=message['ReceiptHandle'])
                else:
                    time.sleep(5)
            except Exception as e:
                log.error(f"Error polling queue: {e}")

    def _record(self, body):
        recording_id = body.get('recording_id')
        game_id = body.get('game_id')
        video_key = body.get('video_key')
        ssh_client = SSHClient()
        ssh_client.connect()
        rdp_client = RDPClient()
        rdp_client.connect()
        game = games[body.get('game_id')](ssh_client=ssh_client, data=body)
        signal.signal(signal.SIGINT,
                      lambda _, __: (
                          log.info(
                              "Ctrl+C intercepted, terminating gracefully"),
                          ssh_client.close(),
                          rdp_client.close(),
                          sys.exit(0)))
        try:
            game.stop()
            ssh_client.exec_command(
                f"del C:\\Users\\{config['recorder_user']}\\Videos\\{recording_id}.mp4")
            ssh_client.psexec(f"cmd.exe /C start \"\" \"{game.exe_path}\"")
            game.after_start()
            ssh_client.psexec(
                f"\"nircmd.exe\" win activate title {game.window_title}", ignore_errors=True)
            ssh_client.psexec(
                f"\"nircmd.exe\" win settopmost title {game.window_title} 1", ignore_errors=True)
            game.before_recording()
            ssh_client.psexec(
                f"cmd.exe /C start \"\" /min \"C:\\ranklab-windows\\ranklab-windows.exe\"")
            start_time = time.time()
            while True:
                if time.time() > start_time + config['recording_timeout']:
                    log.info(
                        f"Recording timed out after {config['recording_timeout']}s")
                    break
                if ui.find_element(f"{game_id}/{game.recording_ended_element}"):
                    log.info(f"Game ended")
                    break
                time.sleep(1)
            ssh_client.kill("ranklab-windows.exe", force=False)
            game.stop()
            ssh_client.copy_file(
                f"C:\\Users\\{config['recorder_user']}\\Videos\\{recording_id}.mp4", f"/tmp/{recording_id}.mp4")
            s3_client = S3Client()
            s3_client.upload_file(f"/tmp/{recording_id}.mp4", video_key)
        except Exception as e:
            log.info(f"Taking screenshot of error: {e}")
            pyautogui.screenshot(f"{root_dir}/screenshots/error.png")
            raise e
        finally:
            rdp_client.close()
            ssh_client.close()
        log.info(f"Finished recording {recording_id}!")


if __name__ == "__main__":
    Worker().poll_queue()
