"""
LLM-powered intelligent command execution using Ollama.
"""
import json
import time
from typing import Dict, List, Optional, Any
import subprocess
import sys


class LLMAgent:
    """Intelligent automation agent powered by local LLM (Ollama)."""
    
    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model
        self.ollama_available = self._check_ollama()
        self.conversation_history = []
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is installed and available."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API and return response."""
        if not self.ollama_available:
            return None
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            print("Ollama request timed out")
        except Exception as e:
            print(f"Ollama error: {e}")
        
        return None
    
    def generate_plan(self, user_prompt: str, ocr_text: str, ui_elements: List[Dict]) -> List[Dict]:
        """
        Generate execution plan from user prompt using LLM.
        
        Returns list of action steps.
        """
        if not self.ollama_available:
            return []
        
        # Format UI elements for prompt
        elements_text = ""
        if ui_elements:
            buttons = [e for e in ui_elements if e.get('type') == 'button']
            inputs = [e for e in ui_elements if e.get('type') == 'input']
            if buttons:
                elements_text += f"Buttons: {', '.join([e['text'] for e in buttons[:10]])}\n"
            if inputs:
                elements_text += f"Input fields: {', '.join([e['text'] for e in inputs[:10]])}\n"
        
        # Build prompt
        system_prompt = """You are a desktop automation agent with vision capabilities.

Available actions:
- open_url: {"action": "open_url", "url": "https://example.com"}
- click: {"action": "click", "x": 100, "y": 200} or {"action": "click", "text": "Login"}
- type: {"action": "type", "text": "Hello"}
- wait_for: {"action": "wait_for", "text": "Page loaded", "timeout": 5}
- wait: {"action": "wait", "seconds": 2}
- press_key: {"action": "press_key", "key": "enter"}

Return ONLY a JSON array of action objects, no other text."""
        
        user_prompt_full = f"""Current screen OCR text:
{ocr_text[:1000]}

Detected UI elements:
{elements_text}

User command: {user_prompt}

Generate a step-by-step plan as JSON array:"""
        
        full_prompt = f"{system_prompt}\n\n{user_prompt_full}"
        
        response = self._call_ollama(full_prompt)
        if not response:
            return []
        
        # Try to extract JSON from response
        try:
            # Find JSON array in response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                plan = json.loads(json_str)
                if isinstance(plan, list):
                    return plan
        except json.JSONDecodeError:
            # Try to parse as single object
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    plan_obj = json.loads(json_str)
                    if isinstance(plan_obj, list):
                        return plan_obj
                    else:
                        return [plan_obj]
            except:
                pass
        
        return []
    
    def is_available(self) -> bool:
        """Check if LLM agent is available."""
        return self.ollama_available

