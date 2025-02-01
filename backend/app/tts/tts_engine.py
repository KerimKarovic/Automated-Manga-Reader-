
import pyttsx3

def speak_text(text: str):
    # Initialize the text-to-speech engine.
    engine = pyttsx3.init()
    # Say the provided text.

# app/tts/tts_engine.py
import pyttsx3

def speak_text(text: str):
    engine = pyttsx3.init()

    engine.say(text)
    engine.runAndWait()
