import os
import time
import threading
from mss import mss
from pynput import mouse, keyboard

class ScreenCapture:
  def __init__(self, interval=0.02):  # Set interval to 0.02 for 20 milliseconds
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

    # Mouse listener
    self.mouse_listener = mouse.Listener(on_click=self._on_click, on_scroll=self._on_scroll)

    # Keyboard listener
    self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)

    # Start both listeners
    self.mouse_listener.start()
    self.keyboard_listener.start()

    # Start the screenshot thread
    self.screenshot_thread = threading.Thread(target=self._take_screenshots, daemon=True)
    self.screenshot_thread.start()

  def _take_screenshots(self):
    with mss() as sct:
      while True:
        screenshot_path = os.path.join(self.folder_path, f"screenshot_{int(time.time() * 1e3)}.png")  # Added millisecond timestamp
        sct.shot(output=screenshot_path)
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
    # The screenshot_thread is a daemon thread and will automatically terminate when the main program exits
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    print("Stopping the screen capture utility...")
    capture.mouse_listener.stop()
    capture.keyboard_listener.stop()
    capture.screenshot_thread.join()
