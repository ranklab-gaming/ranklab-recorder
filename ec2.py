import socket
import time
import boto3
from config import config
from log import log


class EC2Client:
    def __init__(self):
        self.client = boto3.resource(
            "ec2",
            region_name="eu-west-2",
            aws_access_key_id=config["aws_access_key_id"],
            aws_secret_access_key=config["aws_secret_access_key"],
        )
        if not config["ec2_instance_id"]:
            return
        self.instance = self.client.Instance(config["ec2_instance_id"])

    def start_instance(self):
        if not config["ec2_instance_id"]:
            return
        log.info(f"Starting EC2 instance {config['ec2_instance_id']}")
        self.instance.start()
        self.instance.wait_until_running()
        if not self._check_rdp_reachable(self.instance.private_ip_address):
            raise Exception("RDP service is not reachable")
        log.info("Started EC2 instance")

    def stop_instance(self):
        if not config["ec2_instance_id"]:
            return
        log.info("Stopping EC2 instance")
        self.instance.stop()
        self.instance.wait_until_stopped()
        log.info("Stopped EC2 instance")

    def _check_rdp_reachable(self, ip_address, port=3389, timeout=30):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        log.info(f"Checking if RDP port is reachable at {ip_address}:{port}")
        try:
            sock.connect((ip_address, port))
            time.sleep(5)
            log.info("RDP port is reachable")
            return True
        except socket.error:
            return False
        finally:
            sock.close()
