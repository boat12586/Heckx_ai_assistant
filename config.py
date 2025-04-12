# config.py
class Config:
    WHISPER_MODEL = "base.en"
    SAMPLE_RATE = 16000
    CHANNELS = 1
    DTYPE = "int16"
    OLLAMA_MODEL = "gemma3:1b"  # Adjust based on your Ollama model
    AUDIO_THRESHOLD = 0.01  # Minimum audio level to consider as speech
    MAX_SILENCE_SECONDS = 2  # Seconds of silence before stopping recording
    CONVERSATION_HISTORY_LIMIT = 5  # Number of previous exchanges to keep