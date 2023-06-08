import pyautogui
import time
import os

ui_folder = os.path.dirname(__file__)

def find_element(image_path):
    return pyautogui.locateOnScreen(os.path.join(ui_folder, image_path), confidence=0.8, grayscale=True)

def wait_for_element(image_path, timeout=30):
    start_time = time.time()
    print(f"Waiting for UI element {image_path}")
    while time.time() < start_time + timeout:
        element = find_element(image_path)
        if element:
            return element
    raise Exception(f'Element {image_path} not found')

def click_element(image_path, timeout=30):
    element = wait_for_element(image_path, timeout)
    pyautogui.click(pyautogui.center(element))
    print(f"Clicked UI element {image_path}")
