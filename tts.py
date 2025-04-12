# tts.py
import pyttsx3
import numpy as np

class TextToSpeechService:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    
    def synthesize(self, text: str) -> tuple[int, np.ndarray]:
        """
        Synthesizes text to speech and returns audio data.
        Note: pyttsx3 doesn't directly provide audio arrays, so we'll simulate
        this for compatibility with the original code structure.
        """
        # For actual audio array output, we'd need additional processing
        # This is a simplified version that plays directly
        self.engine.say(text)
        self.engine.runAndWait()
        
        # Return dummy audio array for compatibility
        sample_rate = 22050  # Standard audio sample rate
        duration = len(text) * 0.1  # Rough estimate
        audio_array = np.zeros(int(sample_rate * duration), dtype=np.float32)
        return sample_rate, audio_array

    def long_form_synthesize(self, text: str) -> tuple[int, np.ndarray]:
        """Wrapper for compatibility with original code."""
        return self.synthesize(text)