# main.py
import time
import threading
import numpy as np
import whisper
import sounddevice as sd
from queue import Queue
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from tts import TextToSpeechService
from config import Config

console = Console()
stt = whisper.load_model(Config.WHISPER_MODEL)
tts = TextToSpeechService()

# Enhanced prompt template with personality
template = """
You are Heckx, a witty and helpful AI assistant created by bobo. You provide concise, accurate answers with a touch of humor.
Keep responses under 30 words unless asked for more detail. Use the conversation history to stay context-aware.

Conversation history:
{history}

User's input: {input}

Your response:
"""
PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
chain = ConversationChain(
    prompt=PROMPT,
    verbose=False,
    memory=ConversationBufferMemory(
        ai_prefix="Heckx:",
        human_prefix="You:",
        k=Config.CONVERSATION_HISTORY_LIMIT
    ),
    llm=Ollama(model=Config.OLLAMA_MODEL),
)

class VoiceAssistant:
    def __init__(self):
        self.console = console
        self.data_queue = Queue()
        self.stop_event = threading.Event()
        self.is_recording = False

    def record_audio(self):
        """Captures audio and puts it in the queue."""
        def callback(indata, frames, time, status):
            if status:
                self.console.print(f"[red]Audio Error: {status}")
            if self.is_recording:
                audio_level = np.abs(indata).mean()
                if audio_level > Config.AUDIO_THRESHOLD:
                    self.data_queue.put(bytes(indata))

        with sd.RawInputStream(
            samplerate=Config.SAMPLE_RATE,
            dtype=Config.DTYPE,
            channels=Config.CHANNELS,
            callback=callback
        ):
            while not self.stop_event.is_set():
                time.sleep(0.1)

    def transcribe(self, audio_np: np.ndarray) -> str:
        """Transcribes audio to text."""
        result = stt.transcribe(audio_np, fp16=False)
        text = result["text"].strip()
        return text

    def get_response(self, text: str) -> str:
        """Gets response from LLM."""
        response = chain.predict(input=text)
        if response.startswith("Heckx:"):
            response = response[len("Heckx:"):].strip()
        return response

    def play_audio(self, sample_rate: int, audio_array: np.ndarray):
        """Plays audio array."""
        sd.play(audio_array, sample_rate)
        sd.wait()

    def display_welcome(self):
        """Displays welcome message."""
        welcome_text = Text.assemble(
            ("Welcome to your AI Voice Assistant!\n", "cyan bold"),
            ("Press Enter to speak, Enter again to stop.\n", "white"),
            ("Ctrl+C to exit. Let's chat!", "cyan")
        )
        self.console.print(Panel(welcome_text, title="Heckx", border_style="blue"))

    def run(self):
        """Main loop for the assistant."""
        self.display_welcome()
        
        try:
            while True:
                self.console.input(
                    "[green]Press Enter to start speaking...[/green]"
                )
                
                self.data_queue = Queue()
                self.stop_event.clear()
                self.is_recording = True
                
                recording_thread = threading.Thread(
                    target=self.record_audio
                )
                recording_thread.start()

                self.console.input(
                    "[yellow]Speaking... Press Enter to stop[/yellow]"
                )
                
                self.is_recording = False
                self.stop_event.set()
                recording_thread.join()

                audio_data = b"".join(list(self.data_queue.queue))
                audio_np = (
                    np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                )

                if audio_np.size > 0:
                    with self.console.status("[blue]Transcribing...", spinner="dots"):
                        text = self.transcribe(audio_np)
                    self.console.print(Panel(
                        f"You: {text}",
                        title="Your Input",
                        border_style="yellow"
                    ))

                    with self.console.status("[blue]Thinking...", spinner="moon"):
                        response = self.get_response(text)
                        sample_rate, audio_array = tts.long_form_synthesize(response)

                    self.console.print(Panel(
                        f"Heckx: {response}",
                        title="Heckx's Response",
                        border_style="cyan"
                    ))
                    
                    self.play_audio(sample_rate, audio_array)
                else:
                    self.console.print(
                        Panel(
                            "No audio detected. Check your microphone!",
                            title="Error",
                            border_style="red"
                        )
                    )

        except KeyboardInterrupt:
            self.console.print("\n[red]Shutting down gracefully...")
            self.stop_event.set()
            self.console.print(Panel(
                "Thanks for chatting! Come back anytime!",
                title="Goodbye",
                border_style="blue"
            ))

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()