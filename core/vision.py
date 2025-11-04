"""
Enhanced computer vision engine with OCR, caching, and object detection framework.
"""
import pyautogui
import time
from PIL import Image
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import json


class VisionEngine:
    """Analyzes screen content with OCR, caching, and object detection."""
    
    def __init__(self, cache_size: int = 3):
        self.last_screenshot = None
        self.last_analysis = None
        self.screenshot_cache = deque(maxlen=cache_size)  # Cache last N screenshots
        self.ocr_cache = deque(maxlen=cache_size)  # Cache last N OCR results
        self._ocr_available = None
        self._check_ocr_availability()
    
    def _check_ocr_availability(self):
        """Check if pytesseract is available."""
        try:
            import pytesseract
            self._ocr_available = True
        except ImportError:
            self._ocr_available = False
    
    def capture_screen(self, region: Tuple[int, int, int, int] = None) -> Image.Image:
        """Capture current screen or region and cache it."""
        screenshot = pyautogui.screenshot(region=region)
        self.last_screenshot = screenshot
        self.screenshot_cache.append({
            'image': screenshot,
            'timestamp': time.time(),
            'region': region
        })
        return screenshot
    
    def get_ocr_text(self, screenshot: Image.Image = None) -> str:
        """
        Extract text from screenshot using OCR.
        Returns cached result if available.
        """
        if screenshot is None:
            screenshot = self.last_screenshot or self.capture_screen()
        
        if not self._ocr_available:
            return ""
        
        try:
            import pytesseract
            # Convert to grayscale for better OCR
            gray = screenshot.convert('L')
            text = pytesseract.image_to_string(gray)
            
            # Cache result
            self.ocr_cache.append({
                'text': text,
                'timestamp': time.time(),
                'image_size': screenshot.size
            })
            
            return text
        except Exception as e:
            print(f"OCR error: {e}")
            return ""
    
    def get_ocr_with_positions(self, screenshot: Image.Image = None) -> List[Dict]:
        """
        Get OCR text with bounding boxes and positions.
        Returns list of dicts with text, position, and bounding box.
        """
        if screenshot is None:
            screenshot = self.last_screenshot or self.capture_screen()
        
        if not self._ocr_available:
            return []
        
        try:
            import pytesseract
            gray = screenshot.convert('L')
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            elements = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text and int(data['conf'][i]) > 0:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    elements.append({
                        'text': text,
                        'position': (center_x, center_y),
                        'bbox': (x, y, w, h),
                        'confidence': float(data['conf'][i])
                    })
            
            return elements
        except Exception as e:
            print(f"OCR with positions error: {e}")
            return []
    
    def analyze_screen(self, prompt: str = "What is on the screen?") -> Dict:
        """
        Analyze current screen with OCR and element detection.
        Returns comprehensive analysis dict.
        """
        screenshot = self.capture_screen()
        ocr_text = self.get_ocr_text(screenshot)
        ocr_elements = self.get_ocr_with_positions(screenshot)
        
        # Detect UI elements (buttons, inputs, etc.)
        ui_elements = self._detect_ui_elements(ocr_elements)
        
        analysis = {
            'description': f"Screen captured: {len(ocr_elements)} text elements detected",
            'timestamp': time.time(),
            'size': screenshot.size,
            'ocr_text': ocr_text,
            'elements': ocr_elements,
            'ui_elements': ui_elements,
            'element_count': len(ocr_elements)
        }
        
        self.last_analysis = analysis
        return analysis
    
    def _detect_ui_elements(self, ocr_elements: List[Dict]) -> List[Dict]:
        """
        Detect UI elements from OCR results.
        Identifies buttons, input fields, etc. based on text patterns and positions.
        """
        ui_elements = []
        
        # Common button patterns
        button_keywords = ['button', 'click', 'submit', 'save', 'cancel', 'ok', 
                         'login', 'logout', 'sign in', 'sign up', 'search',
                         'bold', 'italic', 'underline', 'file', 'edit', 'view']
        
        # Input field indicators
        input_indicators = ['input', 'enter', 'type', 'search', 'email', 'password']
        
        for element in ocr_elements:
            text_lower = element['text'].lower()
            elem_type = 'text'
            
            # Detect buttons
            if any(keyword in text_lower for keyword in button_keywords):
                elem_type = 'button'
            # Detect input fields (often have placeholders or labels)
            elif any(indicator in text_lower for indicator in input_indicators):
                elem_type = 'input'
            
            ui_elements.append({
                **element,
                'type': elem_type
            })
        
        return ui_elements
    
    def find_text_on_screen(self, text: str, case_sensitive: bool = False) -> List[Tuple[int, int, Tuple[int, int, int, int]]]:
        """
        Find text on screen using OCR.
        Returns list of (x, y, bbox) tuples where text appears.
        bbox is (x, y, width, height)
        """
        if not self._ocr_available:
            return []
        
        try:
            screenshot = self.capture_screen()
            elements = self.get_ocr_with_positions(screenshot)
            
            positions = []
            for elem in elements:
                elem_text = elem['text']
                if (text.lower() in elem_text.lower() if not case_sensitive else text in elem_text):
                    positions.append((
                        elem['position'][0],
                        elem['position'][1],
                        elem['bbox']
                    ))
            
            return positions
        except Exception as e:
            print(f"Find text error: {e}")
            return []
    
    def find_element_by_type(self, element_type: str) -> List[Dict]:
        """
        Find UI elements by type (button, input, etc.).
        """
        analysis = self.analyze_screen()
        return [elem for elem in analysis.get('ui_elements', []) 
                if elem.get('type') == element_type]
    
    def get_screen_description(self) -> str:
        """Get a natural language description of what's on screen."""
        analysis = self.analyze_screen()
        ocr_text = analysis.get('ocr_text', '')
        element_count = analysis.get('element_count', 0)
        
        if ocr_text:
            preview = ocr_text[:200] + "..." if len(ocr_text) > 200 else ocr_text
            return f"Screen has {element_count} elements. Text: {preview}"
        return f"Screen captured with {element_count} detected elements"
    
    def answer_question_about_screen(self, question: str) -> str:
        """
        Answer a question about what's currently on screen.
        Enhanced with OCR and element detection.
        """
        analysis = self.analyze_screen()
        ocr_text = analysis.get('ocr_text', '')
        elements = analysis.get('elements', [])
        ui_elements = analysis.get('ui_elements', [])
        
        question_lower = question.lower()
        
        if 'button' in question_lower:
            buttons = [e for e in ui_elements if e.get('type') == 'button']
            if buttons:
                button_texts = [e['text'] for e in buttons[:5]]
                return f"Found buttons: {', '.join(button_texts)}"
            return "No buttons detected on screen."
        
        if 'text' in question_lower or 'say' in question_lower or 'read' in question_lower:
            if ocr_text.strip():
                preview = ocr_text[:300] + "..." if len(ocr_text) > 300 else ocr_text
                return f"Text on screen: {preview}"
            return "No text detected on screen."
        
        if 'element' in question_lower or 'item' in question_lower:
            return f"Found {len(elements)} text elements and {len(ui_elements)} UI elements"
        
        return f"Screen analysis: {len(elements)} elements detected. Use 'read text' or 'find [button]' for details."
