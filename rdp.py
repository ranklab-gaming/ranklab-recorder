import time
from config import config
import subprocess
from log import log
import re
import threading


def flush_stdout(process):
    while True:
        process.stdout.readline()
        if process.poll() is not None:
            break
        time.sleep(1)


class RDPClient:
    def __init__(self):
        self.process = None
        self.session_id = None

    def connect(self):
        log.info(f"Starting RDP session on {config['recorder_host']}")
        self.process = subprocess.Popen(
            [
                "xfreerdp",
                f"/u:{config['recorder_user']}",
                f"/p:{config['recorder_password']}",
                f"/v:{config['recorder_host']}",
                "/cert-ignore",
                "/log-level:DEBUG",
                "/f",
                "/w:1280",
                "/h:720",
                "/network:lan",
                "/rfx",
                "/audio-mode:1",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        start_time = time.time()
        while True:
            line = self.process.stdout.readline().decode("utf-8")
            if (time.time() - start_time) > 120:
                raise Exception("RDP connection timed out")
            if "LogonInfoV2" in line:
                session_id = re.search("SessionId: 0x([0-9a-fA-F]+)", line).group(1)
                self.session_id = int(session_id, 16)
                break
            time.sleep(0.1)
        threading.Thread(target=flush_stdout, args=(self.process,)).start()

    def close(self):
        if not self.process:
            return
        log.info("Stopping RDP session")
        self.process.terminate()
        self.process.wait()
        self.process = None
