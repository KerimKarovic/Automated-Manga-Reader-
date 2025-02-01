import pyttsx3

def speak_text(text: str):
    # Initialize the text-to-speech engine.
    engine = pyttsx3.init()
    # Say the provided text.
    engine.say(text)
    engine.runAndWait()
