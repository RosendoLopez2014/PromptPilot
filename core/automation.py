"""
Automation engine for mouse, keyboard, and app control.
"""
import pyautogui
import webbrowser
import subprocess
import platform
import time
import pyperclip
from PIL import Image
from pathlib import Path


class AutomationEngine:
    """Handles all automation tasks."""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        self.system = platform.system()
    
    def open_url(self, url: str):
        """Open URL in default browser."""
        webbrowser.open(url)
        time.sleep(1)
    
    def launch_app(self, app_name: str):
        """Launch application by name."""
        app_name_lower = app_name.lower()
        
        # Windows
        if self.system == "Windows":
            apps = {
                "notepad": "notepad.exe",
                "paint": "mspaint.exe",
                "calculator": "calc.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "vs code": "code.exe",
                "code": "code.exe",
                "spotify": "spotify.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
            }
            if app_name_lower in apps:
                subprocess.Popen([apps[app_name_lower]])
            else:
                # Try to launch by name
                subprocess.Popen([app_name])
        
        # macOS
        elif self.system == "Darwin":
            apps = {
                "notepad": "TextEdit",
                "paint": "Preview",
                "calculator": "Calculator",
                "chrome": "Google Chrome",
                "firefox": "Firefox",
                "vs code": "Visual Studio Code",
                "code": "Visual Studio Code",
                "spotify": "Spotify",
                "notes": "Notes",
            }
            if app_name_lower in apps:
                subprocess.Popen(["open", "-a", apps[app_name_lower]])
            else:
                subprocess.Popen(["open", "-a", app_name])
        
        # Linux
        else:
            apps = {
                "notepad": "gedit",
                "paint": "kolourpaint",
                "calculator": "gnome-calculator",
                "chrome": "google-chrome",
                "firefox": "firefox",
                "vs code": "code",
                "code": "code",
                "spotify": "spotify",
            }
            if app_name_lower in apps:
                subprocess.Popen([apps[app_name_lower]])
            else:
                subprocess.Popen([app_name])
        
        time.sleep(2)  # Wait for app to launch
    
    def type_text(self, text: str, delay: float = 0.05):
        """Type text using keyboard."""
        pyautogui.write(text, interval=delay)
    
    def press_key(self, key: str):
        """Press a key."""
        pyautogui.press(key)
    
    def click(self, x: int = None, y: int = None):
        """Click at coordinates or current position."""
        if x is not None and y is not None:
            pyautogui.click(x, y)
        else:
            pyautogui.click()
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to coordinates."""
        pyautogui.moveTo(x, y, duration=duration)
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0):
        """Drag mouse from start to end."""
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot and save to Desktop."""
        if filename is None:
            filename = f"screenshot_{int(time.time())}.png"
        
        # Get Desktop path
        if self.system == "Windows":
            desktop = Path.home() / "Desktop"
        elif self.system == "Darwin":
            desktop = Path.home() / "Desktop"
        else:
            desktop = Path.home() / "Desktop"
        
        desktop.mkdir(parents=True, exist_ok=True)
        filepath = desktop / filename
        
        screenshot = pyautogui.screenshot()
        screenshot.save(str(filepath))
        return str(filepath)
    
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        pyperclip.copy(text)
    
    def paste_from_clipboard(self):
        """Paste from clipboard."""
        pyautogui.hotkey('ctrl', 'v') if self.system != "Darwin" else pyautogui.hotkey('cmd', 'v')
    
    def draw_circle(self, center_x: int, center_y: int, radius: int):
        """Draw a circle using mouse movements."""
        import math
        
        # Move to starting point
        start_x = center_x + radius
        start_y = center_y
        self.move_mouse(start_x, start_y)
        
        # Draw circle
        points = []
        for angle in range(0, 361, 5):
            rad = math.radians(angle)
            x = int(center_x + radius * math.cos(rad))
            y = int(center_y + radius * math.sin(rad))
            points.append((x, y))
        
        # Click and drag
        pyautogui.mouseDown()
        for x, y in points:
            self.move_mouse(x, y, duration=0.01)
        pyautogui.mouseUp()
    
    def search_in_app(self, query: str):
        """Perform search in current app (opens search box and types)."""
        # Try common search shortcuts
        if self.system == "Darwin":
            pyautogui.hotkey('cmd', 'f')
        else:
            pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a') if self.system != "Darwin" else pyautogui.hotkey('cmd', 'a')
        self.type_text(query)
        time.sleep(0.5)
        pyautogui.press('enter')
    
    def wait(self, seconds: float):
        """Wait for specified time."""
        time.sleep(seconds)

