import pyautogui
import time
import os
from log import log


ui_folder = os.path.dirname(__file__)


class ElementNotFoundError(Exception):
    pass


def find_element(image_path):
    return pyautogui.locateOnScreen(os.path.join(ui_folder, image_path), confidence=0.8, grayscale=True)


def wait_for_element(image_path, timeout=30):
    start_time = time.time()
    log.info(f"Waiting for UI element {image_path}")
    while time.time() < start_time + timeout:
        element = find_element(image_path)
        if element:
            return element
    raise ElementNotFoundError(f"Could not find UI element {image_path}")


def click_element(image_path, timeout=30):
    element = wait_for_element(image_path, timeout)
    pyautogui.click(pyautogui.center(element))
    log.info(f"Clicked UI element {image_path}")

def try_click_element(image_path, timeout=5):
    try:
        click_element(image_path, timeout)
    except ElementNotFoundError:
        pass
