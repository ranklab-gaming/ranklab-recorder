import ui
import pyautogui
import os

def click(element, timeout=30):
    ui.click_element(os.path.join('overwatch', element), timeout)

def wait_for(element, timeout=30):
    ui.wait_for_element(os.path.join('overwatch', element), timeout)

def stop(kill):
    kill("Battle.net.exe")
    kill("Overwatch.exe")

def after_start():
    click('play.png')

def before_recording(data):
    click('career-profile.png')
    click('history.png')
    click('replays.png')
    click('import.png')
    pyautogui.typewrite(data['replay_code'])
    click('ok.png')
    
    try:
        click('ok.png', timeout=5)
    except Exception as e:
        if "not found" in str(e):
            pass
        else:
            raise e
        
    click('competitive.png')
    click('view.png')
    wait_for('ready-for-battle.png')

overwatch = {
    'before_recording': before_recording,
    'after_start': after_start,
    'stop': stop,
    'window_title': 'Overwatch',
    'recording_ended_element': 'replay-ended.png',
    'exe_path': "C:\\Program Files (x86)\\Overwatch\\Overwatch Launcher.exe"
}
