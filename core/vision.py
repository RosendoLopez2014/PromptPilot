"""
Computer vision engine for understanding what's on screen.
"""
import pyautogui
import time
from PIL import Image
from typing import Dict, List, Tuple, Optional
import base64
import io
import json


class VisionEngine:
    """Analyzes screen content to understand visual elements."""
    
    def __init__(self):
        self.last_screenshot = None
        self.last_analysis = None
    
    def capture_screen(self, region: Tuple[int, int, int, int] = None) -> Image.Image:
        """Capture current screen or region."""
        screenshot = pyautogui.screenshot(region=region)
        self.last_screenshot = screenshot
        return screenshot
    
    def analyze_screen(self, prompt: str = "What is on the screen?") -> Dict:
        """
        Analyze current screen and understand what's visible.
        
        Options:
        1. Local analysis (OCR + basic detection)
        2. API-based analysis (OpenAI Vision, Google Vision)
        
        Returns dict with analysis results.
        """
        # Capture screen
        screenshot = self.capture_screen()
        
        # For now, basic analysis
        # TODO: Add OpenAI Vision API or Google Vision API integration
        analysis = {
            'description': 'Screen captured',
            'timestamp': time.time(),
            'size': screenshot.size,
            'elements': []  # Will contain detected elements
        }
        
        self.last_analysis = analysis
        return analysis
    
    def find_text_on_screen(self, text: str, case_sensitive: bool = False) -> List[Tuple[int, int]]:
        """
        Find text on screen using OCR.
        Returns list of (x, y) coordinates where text appears.
        """
        try:
            # Try to import pytesseract if available
            import pytesseract
            from PIL import Image
            
            screenshot = self.capture_screen()
            # Convert to grayscale for better OCR
            gray = screenshot.convert('L')
            
            # Use pytesseract to find text
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            positions = []
            for i, word in enumerate(data['text']):
                if text.lower() in word.lower() if not case_sensitive else text in word:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    positions.append((x, y))
            
            return positions
        except ImportError:
            # OCR not available
            return []
        except Exception as e:
            print(f"OCR error: {e}")
            return []
    
    def find_image_on_screen(self, template_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Find an image template on screen.
        Returns (x, y) center of found image, or None.
        """
        try:
            location = pyautogui.locateOnScreen(template_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return (center.x, center.y)
        except Exception as e:
            print(f"Image search error: {e}")
        return None
    
    def get_screen_description(self) -> str:
        """Get a natural language description of what's on screen."""
        analysis = self.analyze_screen()
        return analysis.get('description', 'Screen analysis unavailable')
    
    def answer_question_about_screen(self, question: str) -> str:
        """
        Answer a question about what's currently on screen.
        Example: "Where is the login button?" or "What text is visible?"
        """
        # For now, basic implementation
        # TODO: Integrate with vision API for intelligent answers
        
        if 'button' in question.lower():
            # Try to find buttons or clickable elements
            return "Button detection not yet implemented. Use 'click at x y' for now."
        
        if 'text' in question.lower() or 'say' in question.lower() or 'read' in question.lower():
            # Try OCR to read text
            try:
                import pytesseract
                screenshot = self.capture_screen()
                text = pytesseract.image_to_string(screenshot)
                if text.strip():
                    return f"Text found on screen: {text[:200]}..." if len(text) > 200 else f"Text found: {text}"
                else:
                    return "No text detected on screen."
            except ImportError:
                return "OCR not available. Install pytesseract for text reading."
        
        return "Visual analysis available. Try: 'what text is on screen?' or 'find [button name]'"

