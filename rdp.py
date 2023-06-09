from config import config
import subprocess
from log import log


class RDPClient:
    def __init__(self):
        self.process = None

    def connect(self):
        log.info(f"Starting RDP session on {config['recorder_host']}")

        self.process = subprocess.Popen([
            "xfreerdp",
            f"/u:{config['recorder_user']}",
            f"/p:{config['recorder_password']}",
            f"/v:{config['recorder_host']}",
            "/cert-ignore",
            "/log-level:FATAL",
            "/f",
            "/w:1280",
            "/h:720",
            "/network:lan",
            "/rfx",
            "/audio-mode:1"
        ])

    def close(self):
        if not self.process:
            return
        log.info("Stopping RDP session")
        self.process.terminate()
        self.process.wait()
        self.process = None
