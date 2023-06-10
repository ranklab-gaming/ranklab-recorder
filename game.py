import ui
import os
from log import log


class Game:
    def __init__(
        self, ssh_client, game_id, exe_path, window_title, recording_ended_element
    ):
        self.ssh_client = ssh_client
        self.game_id = game_id
        self.exe_path = exe_path
        self.window_title = window_title
        self.recording_ended_element = recording_ended_element

    def click(self, element, timeout=30):
        ui.click_element(os.path.join(self.game_id, element), timeout)

    def wait_for(self, element, timeout=30):
        ui.find_element(os.path.join(self.game_id, element), timeout)

    def start(self):
        log.info(f"Executing start {self.game_id}")

    def after_start(self):
        log.info(f"Executing after_start {self.game_id}")

    def before_recording(self):
        log.info(f"Executing before_recording {self.game_id}")

    def stop(self):
        log.info(f"Executing stop {self.game_id}")
