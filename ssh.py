import paramiko
from config import config
from log import log


class SSHClient:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        log.info(f"Starting SSH session on {config['recorder_host']}")
        self.client.connect(hostname=config['recorder_host'],
                            username=config['recorder_user'], password=config['recorder_password'])

    def close(self):
        if self.client is None:
            return
        log.info("Stopping SSH session")
        self.client.close()
        self.client = None

    def exec_command(self, cmd, wait=True, ignore_errors=False):
        log.info(f"Running SSH command: {cmd}")
        _, stdout, _ = self.client.exec_command(cmd)
        if wait:
            status = stdout.channel.recv_exit_status()
            if status != 0 and not ignore_errors:
                raise Exception(f"Command {cmd} failed with status {status}")

    def psexec(self, cmd, wait=True, ignore_errors=False):
        self.exec_command(
            f"psexec64 -i 0 -u {config['recorder_user']} -p {config['recorder_password']} {cmd}", wait, ignore_errors)

    def kill(self, cmd, wait=True, ignore_errors=True, force=True):
        flags = ''
        if force:
            flags = '/F'
        self.exec_command(f"taskkill /IM {cmd} {flags}", wait, ignore_errors)

    def copy_file(self, remote_path, local_path):
        log.info(f"Copying {remote_path} to {local_path}")
        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        log.info(f"Finished copying {remote_path} to {local_path}")
