import pyautogui
import time
import os

ui_folder = os.path.join(os.path.dirname(__file__), 'ui')

def find_element(element):
    return pyautogui.locateOnScreen(os.path.join(ui_folder, element), confidence=0.9, grayscale=True)

def click_element(element):
    start_time = time.time()
    while time.time() < start_time + 20:
        element = find_element(element)
        if element:
            center = pyautogui.center(element)
            pyautogui.click(center)
            return
        else:
            time.sleep(1)
    raise Exception(f'Element {element} not found')
