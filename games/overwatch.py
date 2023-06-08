import ui
import pyautogui
import os
import subprocess

def click(element):
    ui.click_element(os.path.join('overwatch', element))

def before_recording(data):
    click('play.png')
    click('career-profile.png')
    click('history.png')
    click('replays.png')
    click('import.png')
    pyautogui.typewrite(data['replay_code'])
    click('ok.png')

def after_recording(kill_cmd):
    subprocess.run(kill_cmd + ["Battle.net.exe", "\F"])

overwatch = {
    'before_recording': before_recording,
    'after_recording': after_recording,
    'recording_ended_element': 'victory.png',
    'exe_path': "C:\\Program Files (x86)\\Overwatch\\Overwatch Launcher.exe"
}
