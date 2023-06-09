import paramiko
from config import config
from log import log


class SSHClient:
    def __init__(self, session_id):
        self._session_id = session_id
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        log.info(f"Starting SSH session on {config['recorder_host']}")
        self.client.connect(
            hostname=config["recorder_host"],
            username=config["recorder_user"],
            password=config["recorder_password"],
        )

    def close(self):
        if self.client is None:
            return
        log.info("Stopping SSH session")
        self.client.close()
        self.client = None

    def exec_command(self, cmd, ignore_errors=False):
        if self.client is None:
            return
        filtered_cmd = cmd.replace(config["recorder_password"], "***").replace(
            config["recorder_user"], "***"
        )
        log.info(f"Executing SSH command: {filtered_cmd}")
        _, stdout, _ = self.client.exec_command(cmd)
        status = stdout.channel.recv_exit_status()
        if status != 0 and not ignore_errors:
            raise Exception(f"Command {filtered_cmd} failed with status {status}")
        value = stdout.read().decode("utf-8")
        return value

    def psexec(self, cmd, ignore_errors=False):
        self.exec_command(
            f"psexec64 -i {self._session_id} -u {config['recorder_user']} -p \"{config['recorder_password']}\" {cmd}",
            ignore_errors,
        )

    def kill(self, cmd, ignore_errors=True, force=True):
        flags = ""
        if force:
            flags += "/F"
        self.exec_command(f"taskkill /IM {cmd} {flags}", ignore_errors)

    def copy_file(self, remote_path, local_path):
        log.info(f"Copying {remote_path} to {local_path}")
        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        log.info("Finished copying file")
