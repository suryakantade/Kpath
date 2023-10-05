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

    # Initialize the event log file
    self.log_file_path = os.path.join(self.folder_path, "events_log.txt")
    with open(self.log_file_path, "w") as log_file:
      log_file.write("Event Log:\n\n")

    # Click counter for detecting double clicks
    self.click_counter = 0

    # Lock for synchronization
    self.lock = threading.Lock()

    self.screenshot_thread = threading.Thread(target=self._take_screenshots, daemon=True)
    self.mouse_listener = mouse.Listener(on_click=self._on_click, on_scroll=self._on_scroll)
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
    with self.lock:
      if pressed:
        self.click_counter += 1
        timestamp = int(time.time() * 1e9)  # Convert seconds to nanoseconds
        event_info = f"{timestamp}: Mouse Pressed at ({x}, {y}) with {button}\n"
        print(event_info)
        self._log_event(event_info)

        # Check for double-click
        if self.click_counter == 2:
          event_info = f"{timestamp}: Mouse Double-Clicked at ({x}, {y}) with {button}\n"
          print(event_info)
          self._log_event(event_info)
          self.click_counter = 0
      else:
        timestamp = int(time.time() * 1e9)  # Convert seconds to nanoseconds
        event_info = f"{timestamp}: Mouse Released at ({x}, {y}) with {button}\n"
        print(event_info)
        self._log_event(event_info)

  def _on_scroll(self, x, y, dx, dy):
    with self.lock:
      timestamp = int(time.time() * 1e9)  # Convert seconds to nanoseconds
      event_info = f"{timestamp}: Scrolled at ({x}, {y}) with delta ({dx}, {dy})\n"
      print(event_info)
      self._log_event(event_info)

  def _on_key_press(self, key):
    with self.lock:
      try:
        timestamp = int(time.time() * 1e9)  # Convert seconds to nanoseconds
        event_info = f"{timestamp}: Key pressed: {key.char}\n"
        print(event_info)
        self._log_event(event_info)
      except AttributeError:
        pass  # Ignore special keys

  def _on_key_release(self, key):
    with self.lock:
      timestamp = int(time.time() * 1e9)  # Convert seconds to nanoseconds
      event_info = f"{timestamp}: Key released: {key}\n"
      print(event_info)
      self._log_event(event_info)

  def _log_event(self, event_info):
    with open(self.log_file_path, "a") as log_file:
      log_file.write(event_info)

if __name__ == "__main__":
  capture = ScreenCapture()

  try:
    capture.screenshot_thread.join()
  except KeyboardInterrupt:
    print("Stopping the screen capture utility...")
    capture.mouse_listener.stop()
    capture.keyboard_listener.stop()
    capture.screenshot_thread.join()
