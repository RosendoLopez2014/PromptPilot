"""
Voice recognition module for speech-to-text.
"""
import speech_recognition as sr
import threading
from typing import Callable, Optional


class VoiceRecognizer:
    """Handles voice recognition for speech-to-text."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.callback: Optional[Callable[[str], None]] = None
        
        # Initialize microphone
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception as e:
            print(f"Warning: Could not initialize microphone: {e}")
    
    def start_listening(self, callback: Callable[[str], None]):
        """Start listening for voice input in background thread."""
        if self.is_listening:
            return
        
        if self.microphone is None:
            callback("Microphone not available")
            return
        
        self.callback = callback
        self.is_listening = True
        
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
    
    def stop_listening(self):
        """Stop listening for voice input."""
        self.is_listening = False
    
    def _listen_loop(self):
        """Background thread loop for listening."""
        if self.microphone is None:
            if self.callback:
                self.callback("Microphone not available")
            return
        
        try:
            with self.microphone as source:
                self.callback("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            try:
                text = self.recognizer.recognize_google(audio)
                if self.callback and self.is_listening:
                    self.callback(text)
            except sr.UnknownValueError:
                if self.callback:
                    self.callback("Could not understand audio")
            except sr.RequestError as e:
                if self.callback:
                    self.callback(f"Recognition error: {e}")
        except sr.WaitTimeoutError:
            if self.callback:
                self.callback("Listening timeout")
        except Exception as e:
            if self.callback:
                self.callback(f"Error: {e}")
        finally:
            self.is_listening = False

