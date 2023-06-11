import pyautogui
import os
from log import log
import time

ui_folder = os.path.dirname(__file__)
pyautogui.useImageNotFoundException()


def find_element(image_path, timeout=20):
    log.info(f"Looking for UI element {image_path}")
    return pyautogui.locateOnScreen(
        os.path.join(ui_folder, image_path), timeout, confidence=0.9, grayscale=True
    )


def click_element(image_path, timeout=20):
    element = find_element(image_path, timeout)
    pyautogui.click(pyautogui.center(element))
    log.info(f"Clicked UI element {image_path}")
    time.sleep(1)
