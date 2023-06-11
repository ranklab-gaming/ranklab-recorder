import socket
import boto3
from config import config
from log import log


class EC2Client:
    def __init__(self):
        self.client = boto3.client(
            "ec2",
            region_name="eu-west-2",
            aws_access_key_id=config["aws_access_key_id"],
            aws_secret_access_key=config["aws_secret_access_key"],
        )
        self.instance_id = config["ec2_instance_id"]

    def start_instance(self):
        if not self.instance_id:
            return
        log.info(f"Starting EC2 instance {self.instance_id}")
        self.client.start_instances(InstanceIds=[self.instance_id])
        self.client.get_waiter("instance_running").wait(InstanceIds=[self.instance_id])
        instance_description = self.client.describe_instances(
            InstanceIds=[self.instance_id]
        )
        private_ip = instance_description["Reservations"][0]["Instances"][0][
            "PrivateIpAddress"
        ]
        if not self._check_rdp_reachable(private_ip):
            raise Exception("RDP service is not reachable")
        log.info("Started EC2 instance")

    def stop_instance(self):
        if not self.instance_id:
            return
        log.info("Stopping EC2 instance")
        self.client.stop_instances(InstanceIds=[self.instance_id])
        self.client.get_waiter("instance_stopped").wait(InstanceIds=[self.instance_id])
        log.info("Stopped EC2 instance")

    def _check_rdp_reachable(self, ip_address, port=3389, timeout=30):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        log.info(f"Checking if RDP port is reachable at {ip_address}:{port}")
        try:
            sock.connect((ip_address, port))
            log.info("RDP port is reachable")
            return True
        except socket.error:
            return False
        finally:
            sock.close()
