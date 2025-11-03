"""
Command parser that interprets natural language prompts.
"""
import re
import platform
import pyautogui
from typing import Dict, Tuple, Optional
from core.automation import AutomationEngine


class CommandParser:
    """Parses natural language prompts into executable commands."""
    
    def __init__(self, automation: AutomationEngine):
        self.automation = automation
    
    def parse(self, prompt: str) -> Tuple[str, Dict]:
        """
        Parse prompt and return (action_type, params).
        Returns: ('status_message', {'action': callable, 'args': ...})
        """
        prompt_lower = prompt.lower().strip()
        
        # Google Sheets creation
        if re.search(r'(make|create|new).*google.*sheet', prompt_lower):
            sheet_name = self._extract_name(prompt_lower, ['sheet', 'called', 'named'])
            return ("Opening Google Sheets...", {
                'action': self._create_google_sheet,
                'args': (sheet_name or 'Untitled',)
            })
        
        # Open application
        if re.search(r'open\s+([\w\s]+)', prompt_lower):
            app_match = re.search(r'open\s+(?:the\s+)?([\w\s]+?)(?:\s+app)?(?:$|\s+and|\s+then)', prompt_lower)
            if app_match:
                app_name = app_match.group(1).strip()
                return (f"Opening {app_name}...", {
                    'action': self.automation.launch_app,
                    'args': (app_name,)
                })
        
        # Type text in app
        if re.search(r'type\s+["\'](.+?)["\']', prompt_lower) or re.search(r'type\s+([^in]+?)\s+in\s+', prompt_lower):
            text_match = re.search(r'type\s+["\'](.+?)["\']', prompt_lower)
            if not text_match:
                text_match = re.search(r'type\s+([^in]+?)\s+in\s+', prompt_lower)
            
            if text_match:
                text_to_type = text_match.group(1).strip()
                app_match = re.search(r'in\s+([\w\s]+)', prompt_lower)
                app_name = app_match.group(1).strip() if app_match else "notepad"
                
                return (f"Opening {app_name} and typing...", {
                    'action': self._type_in_app,
                    'args': (text_to_type, app_name)
                })
        
        # Draw circle in Paint
        if re.search(r'draw\s+(?:a\s+)?(?:red\s+)?circle\s+in\s+paint', prompt_lower):
            return ("Opening Paint and drawing circle...", {
                'action': self._draw_circle_in_paint,
                'args': ()
            })
        
        # Screenshot
        if re.search(r'take\s+(?:a\s+)?screenshot', prompt_lower):
            return ("Taking screenshot...", {
                'action': self.automation.take_screenshot,
                'args': ()
            })
        
        # Spotify search/play
        if re.search(r'open\s+spotify', prompt_lower):
            play_match = re.search(r'play\s+([\w\s]+)', prompt_lower)
            query = play_match.group(1).strip() if play_match else None
            
            return ("Opening Spotify...", {
                'action': self._open_spotify_and_search,
                'args': (query,)
            })
        
        # Generic URL opening
        if re.search(r'open\s+(https?://[^\s]+)', prompt_lower):
            url_match = re.search(r'open\s+(https?://[^\s]+)', prompt_lower)
            if url_match:
                url = url_match.group(1)
                return (f"Opening {url}...", {
                    'action': self.automation.open_url,
                    'args': (url,)
                })
        
        # Copy to clipboard
        if re.search(r'copy\s+["\'](.+?)["\']', prompt_lower):
            text_match = re.search(r'copy\s+["\'](.+?)["\']', prompt_lower)
            if text_match:
                text = text_match.group(1)
                return ("Copying to clipboard...", {
                    'action': self.automation.copy_to_clipboard,
                    'args': (text,)
                })
        
        # Default: try to open as URL or app name
        if prompt_lower.startswith('open '):
            target = prompt_lower[5:].strip()
            if '.' in target and not ' ' in target:
                # Might be a URL
                url = target if target.startswith('http') else f'https://{target}'
                return (f"Opening {url}...", {
                    'action': self.automation.open_url,
                    'args': (url,)
                })
            else:
                # Treat as app name
                return (f"Opening {target}...", {
                    'action': self.automation.launch_app,
                    'args': (target,)
                })
        
        # Unknown command
        return ("Unknown command. Try: 'open chrome', 'type hello in notepad', 'take screenshot'", {
            'action': None,
            'args': ()
        })
    
    def _extract_name(self, prompt: str, keywords: list) -> Optional[str]:
        """Extract a name from prompt after keywords."""
        for keyword in keywords:
            pattern = rf'{keyword}\s+(["\']?)([\w\s]+)\1'
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(2).strip()
        return None
    
    def _create_google_sheet(self, name: str):
        """Create a new Google Sheet."""
        self.automation.open_url("https://sheets.new")
        self.automation.wait(3)
        
        # Type sheet name
        self.automation.wait(1)
        # Click on title area (common position)
        screen_width, screen_height = pyautogui.size()
        self.automation.click(screen_width // 2, 100)
        self.automation.wait(0.5)
        
        # Select all and type name
        if platform.system() == "Darwin":
            self.automation.press_key('cmd+a')
        else:
            self.automation.press_key('ctrl+a')
        
        self.automation.type_text(name)
        self.automation.wait(0.5)
        self.automation.press_key('enter')
    
    def _type_in_app(self, text: str, app_name: str):
        """Open app and type text."""
        self.automation.launch_app(app_name)
        self.automation.wait(2)
        self.automation.type_text(text)
    
    def _draw_circle_in_paint(self):
        """Open Paint and draw a circle."""
        import pyautogui
        
        self.automation.launch_app("paint")
        self.automation.wait(3)
        
        # Get screen center
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        radius = 100
        
        # Draw circle
        self.automation.draw_circle(center_x, center_y, radius)
    
    def _open_spotify_and_search(self, query: Optional[str] = None):
        """Open Spotify and optionally search."""
        self.automation.launch_app("spotify")
        self.automation.wait(3)
        
        if query:
            # Search in Spotify
            self.automation.search_in_app(query)

