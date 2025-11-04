"""
Command parser that interprets natural language prompts.
"""
import re
import platform
import pyautogui
from typing import Dict, Tuple, Optional, List
from core.automation import AutomationEngine
from core.llm_agent import LLMAgent


class CommandParser:
    """Parses natural language prompts into executable commands."""
    
    def __init__(self, automation: AutomationEngine, vision=None):
        self.automation = automation
        self.vision = vision
        self.llm_agent = LLMAgent() if vision else None
    
    def parse(self, prompt: str) -> Tuple[str, Dict]:
        """
        Parse prompt and return (action_type, params).
        Returns: ('status_message', {'action': callable, 'args': ...})
        
        If LLM is available and prompt is complex, use LLM to generate plan.
        """
        prompt_lower = prompt.lower().strip()
        
        # Try LLM for complex/unrecognized commands
        if self.llm_agent and self.llm_agent.is_available() and self.vision:
            # Check if this is a complex prompt that needs LLM
            if self._needs_llm(prompt_lower):
                return self._parse_with_llm(prompt)
        
        # Vision-based commands
        if self.vision:
            # "What's on my screen?" or "describe screen"
            if re.search(r"(what'?s|what is|describe|show).*(on|my).*screen", prompt_lower):
                return ("Analyzing screen...", {
                    'action': self._describe_screen,
                    'args': ()
                })
            
            # "Find [text]" or "click [button name]"
            if re.search(r'(find|click|locate)\s+["\']?([^"\']+)["\']?', prompt_lower):
                match = re.search(r'(find|click|locate)\s+["\']?([^"\']+)["\']?', prompt_lower)
                action_type = match.group(1)
                target = match.group(2).strip()
                
                if action_type == 'click':
                    return (f"Finding and clicking '{target}'...", {
                        'action': self._find_and_click,
                        'args': (target,)
                    })
                else:
                    return (f"Searching for '{target}'...", {
                        'action': self._find_on_screen,
                        'args': (target,)
                    })
            
            # "Read text on screen" or "what text is visible?"
            if re.search(r'(read|what).*text.*(on|screen|visible)', prompt_lower):
                return ("Reading text on screen...", {
                    'action': self._read_screen_text,
                    'args': ()
                })
            
            # "Answer question about screen"
            if re.search(r'(answer|tell me|what|where|how many).*(about|on|screen)', prompt_lower):
                return ("Analyzing screen to answer question...", {
                    'action': self._answer_question,
                    'args': (prompt,)
                })
        
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
        
        # Unknown command - try LLM if available
        if self.llm_agent and self.llm_agent.is_available() and self.vision:
            return self._parse_with_llm(prompt)
        
        return ("Unknown command. Try: 'open chrome', 'type hello in notepad', 'take screenshot'", {
            'action': None,
            'args': ()
        })
    
    def _needs_llm(self, prompt_lower: str) -> bool:
        """Determine if prompt needs LLM interpretation."""
        # Simple commands don't need LLM
        simple_patterns = [
            r'^open\s+\w+$',
            r'^take\s+screenshot$',
            r'^copy\s+".*"$',
        ]
        
        import re
        for pattern in simple_patterns:
            if re.match(pattern, prompt_lower):
                return False
        
        # Complex commands need LLM
        complex_keywords = ['create', 'make', 'build', 'generate', 'set up', 
                           'configure', 'add', 'remove', 'update', 'change']
        if any(keyword in prompt_lower for keyword in complex_keywords):
            return True
        
        # Multi-step commands
        if any(word in prompt_lower for word in ['then', 'and', 'after', 'next']):
            return True
        
        return False
    
    def _parse_with_llm(self, prompt: str) -> Tuple[str, Dict]:
        """Use LLM to parse complex prompt and generate execution plan."""
        if not self.vision or not self.llm_agent:
            return ("LLM not available", {'action': None, 'args': ()})
        
        # Get current screen context
        analysis = self.vision.analyze_screen()
        ocr_text = analysis.get('ocr_text', '')
        ui_elements = analysis.get('ui_elements', [])
        
        # Generate plan
        plan = self.llm_agent.generate_plan(prompt, ocr_text, ui_elements)
        
        if not plan:
            return ("Could not generate plan. Try a simpler command.", {
                'action': None,
                'args': ()
            })
        
        return ("Executing intelligent plan...", {
            'action': self._execute_llm_plan,
            'args': (plan,)
        })
    
    def _execute_llm_plan(self, plan: List[Dict]):
        """Execute plan generated by LLM."""
        for step in plan:
            action = step.get('action')
            
            if action == 'open_url':
                url = step.get('url')
                if url:
                    self.automation.open_url(url)
                    self.automation.wait(2)
            
            elif action == 'click':
                bbox = None
                if 'text' in step:
                    # Find text and click
                    target = step['text']
                    positions = self.vision.find_text_on_screen(target)
                    if positions:
                        x, y, bbox = positions[0]
                        self.automation.click(x, y, bbox=bbox)
                elif 'x' in step and 'y' in step:
                    x, y = step['x'], step['y']
                    self.automation.click(x, y, bbox=bbox)
                self.automation.wait(0.5)
            
            elif action == 'type':
                text = step.get('text', '')
                if text:
                    self.automation.type_text(text)
                    self.automation.wait(0.3)
            
            elif action == 'wait' or action == 'wait_for':
                seconds = step.get('seconds', step.get('timeout', 2))
                self.automation.wait(seconds)
            
            elif action == 'press_key':
                key = step.get('key')
                if key:
                    self.automation.press_key(key)
                    self.automation.wait(0.3)
        
        return "✓ Plan executed successfully"
    
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
    
    # Vision-based methods
    def _describe_screen(self):
        """Get description of what's on screen."""
        if not self.vision:
            return "Vision engine not available"
        analysis = self.vision.analyze_screen()
        return f"Screen: {analysis.get('description', 'Analysis complete')}"
    
    def _find_and_click(self, target: str):
        """Find text/image on screen and click it."""
        if not self.vision:
            return "Vision engine not available"
        
        # Try to find text first
        positions = self.vision.find_text_on_screen(target)
        if positions:
            # Click first occurrence with bbox for highlight
            x, y, bbox = positions[0]
            self.automation.click(x, y, bbox=bbox)
            return f"✓ Clicked '{target}' at ({x}, {y})"
        else:
            return f"✗ Could not find '{target}' on screen"
    
    def _find_on_screen(self, target: str):
        """Find something on screen and report location."""
        if not self.vision:
            return "Vision engine not available"
        
        positions = self.vision.find_text_on_screen(target)
        if positions:
            locations = ", ".join([f"#{i+1} at ({x},{y})" for i, (x, y) in enumerate(positions[:3])])
            return f"Found '{target}': {locations}"
        else:
            return f"'{target}' not found on screen"
    
    def _read_screen_text(self):
        """Read all text visible on screen."""
        if not self.vision:
            return "Vision engine not available"
        
        answer = self.vision.answer_question_about_screen("what text is on screen")
        return answer
    
    def _answer_question(self, question: str):
        """Answer a question about what's on screen."""
        if not self.vision:
            return "Vision engine not available"
        
        answer = self.vision.answer_question_about_screen(question)
        return f"Answer: {answer}"

