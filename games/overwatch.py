import time
from game import Game
import pyautogui
import ui


class Overwatch(Game):
    def __init__(self, ssh_client, data):
        super().__init__(game_id="overwatch", exe_path="C:\\Program Files (x86)\\Overwatch\\Overwatch Launcher.exe",
                         window_title="Overwatch", recording_ended_element="replay-ended.png", ssh_client=ssh_client)
        self.replay_code = data['replay_code']

    def stop(self):
        super().stop()
        self.ssh_client.kill("Battle.net.exe")
        self.ssh_client.kill("Overwatch.exe")

    def after_start(self):
        super().after_start()
        self.try_click('popup-close.png')
        self.click('play.png')

    def before_recording(self):
        super().before_recording()
        self.click('career-profile.png')
        self.click('history.png')
        self.click('replays.png')
        self.click('import.png')
        pyautogui.typewrite(self.replay_code)
        self.click('ok.png')
        self.try_click('ok.png')
        self.click('competitive.png')
        self.click('view.png')
        self.wait_for('ready-for-battle.png')
