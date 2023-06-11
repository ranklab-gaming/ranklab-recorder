import time
from game import Game
import pyautogui


class Overwatch(Game):
    def __init__(self, ssh_client, data):
        super().__init__(
            game_id="overwatch",
            exe_path="C:\\Program Files (x86)\\Overwatch\\Overwatch Launcher.exe",
            window_title="Overwatch",
            recording_ended_element="replay-ended.png",
            ssh_client=ssh_client,
        )
        self.replay_code = data["replay_code"]
        self.player_position = int(data["player_position"])

    def stop(self):
        super().stop()
        self.ssh_client.kill("Battle.net.exe")
        self.ssh_client.kill("Overwatch.exe")

    def after_start(self):
        super().after_start()
        try:
            self.click("play.png")
        except pyautogui.ImageNotFoundException:
            self.click("popup-close.png")
            self.click("play.png")

    def before_recording(self):
        super().before_recording()
        self.click("career-profile.png")
        self.click("history.png")
        self.click("replays.png")
        self.click("import.png")
        pyautogui.typewrite(self.replay_code)
        self.click("ok.png")
        self.click("view.png")
        self.find("team-1.png")
        time.sleep(1)
        pyautogui.press(f"f{self.player_position + 1}")
