import os
import time
import threading
import pyautogui
from pynput import mouse, keyboard

class ScreenCapture:
  def __init__(self, interval=1):
    self.interval = interval
    self.base_dir = "screen_shots"

    # Create the base directory if it doesn't exist
    if not os.path.exists(self.base_dir):
      os.makedirs(self.base_dir)

    # Create a folder with the current timestamp
    self.folder_path = os.path.join(self.base_dir, time.strftime("%Y%m%d%H%M%S"))
    os.makedirs(self.folder_path)

    self.screenshot_thread = threading.Thread(target=self._take_screenshots, daemon=True)
    self.mouse_listener = mouse.Listener(on_click=self._on_click)
    self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)

    self.screenshot_thread.start()
    self.mouse_listener.start()
    self.keyboard_listener.start()

  def _take_screenshots(self):
    while True:
      screenshot_path = os.path.join(self.folder_path, f"screenshot_{int(time.time())}.png")
      screenshot = pyautogui.screenshot()
      screenshot.save(screenshot_path)

      time.sleep(self.interval)

  def _on_click(self, x, y, button, pressed):
    action = "Pressed" if pressed else "Released"
    print(f"Mouse {action} at ({x}, {y}) with {button}")

  def _on_key_press(self, key):
    try:
      print(f"Key pressed: {key.char}")
    except AttributeError:
      print(f"Special key {key} pressed")

  def _on_key_release(self, key):
    print(f"Key released: {key}")

if __name__ == "__main__":
  capture = ScreenCapture()

  try:
    capture.screenshot_thread.join()
  except KeyboardInterrupt:
    print("Stopping the screen capture utility...")
    capture.mouse_listener.stop()
    capture.keyboard_listener.stop()
    capture.screenshot_thread.join()
