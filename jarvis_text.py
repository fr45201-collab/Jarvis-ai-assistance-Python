import datetime
import wikipedia
import webbrowser
import pywhatkit
import speech_recognition as sr
import pyttsx3
import sys
import re

# ----------------- TEXT TO SPEECH -----------------
engine = pyttsx3.init()

def speak_text(text: str) -> None:
    print("Jarvis:", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        # If TTS fails, at least show text
        pass

# ----------------- LISTEN (VOICE + TYPE FALLBACK) -----------------
def listen_command() -> str:
    recognizer = sr.Recognizer()

    # Try microphone first
    try:
        # device_index=None = use default mic
        with sr.Microphone(device_index=None) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.7)
            print("Listening...")
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=6)

        try:
            command = recognizer.recognize_google(audio, language="en-IN")
            print("You (voice):", command)
            return command.lower()
        except sr.UnknownValueError:
            speak_text("Sorry, I didn't understand. Please type your command.")
        except sr.RequestError:
            speak_text("Voice service unreachable. Please type your command.")
    except Exception as e:
        print("Mic error:", e)
        speak_text("Microphone problem. Please type your command.")

    # Fallback to typed input
    text = input("You (type): ")
    return text.strip().lower()

# ----------------- ACTION HELPERS -----------------
def _open_site(arg: str) -> None:
    url = arg.strip()
    if not url:
        speak_text("Tell me which site to open.")
        return
    if not url.startswith("http"):
        url = "https://" + url
    speak_text(f"Opening {url}")
    webbrowser.open(url)

def _play_song(arg: str) -> None:
    song = arg.strip()
    if not song:
        speak_text("Tell me which song to play.")
        return
    speak_text(f"Playing {song} on YouTube...")
    try:
        pywhatkit.playonyt(song)
    except Exception:
        speak_text("I couldn't play the song. Maybe check your internet.")

def _wikipedia_search(arg: str) -> None:
    topic = arg.strip()
    if not topic:
        speak_text("Say the topic after 'wikipedia'.")
        return
    try:
        summary = wikipedia.summary(topic, sentences=2)
        speak_text(summary)
    except Exception:
        speak_text("I couldn't find that on Wikipedia.")

def _say_time(arg: str | None = None) -> None:
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak_text(f"The time is {now}")

def _unknown(arg: str) -> None:
    speak_text("Unknown command. Try: time, wikipedia <topic>, play <song>, open <site>.")

# ----------------- COMMAND PARSER -----------------
def parse_and_exec(command: str) -> None:
    """
    Understand a free-text command and perform actions.
    Supported:
      - time
      - wikipedia <topic>
      - play <song>
      - open <site>
      - exit / quit / stop
    """
    if not command:
        return

    low = command.lower()

    # exit
    if any(word in low for word in ("exit", "quit", "stop", "bye")):
        speak_text("Goodbye!")
        raise SystemExit

    # time
    if "time" in low:
        _say_time(None)
        return

    # wikipedia
    m = re.match(r"^(wikipedia|wiki)\s+(.+)$", low)
    if m:
        _wikipedia_search(m.group(2))
        return

    # play
    m = re.match(r"^(play)\s+(.+)$", low)
    if m:
        _play_song(m.group(2))
        return

    # open
    m = re.match(r"^(open|go to|visit)\s+(.+)$", low)
    if m:
        _open_site(m.group(2))
        return

    # if looks like url
    if re.match(r"^[\w\-.]+\.\w{2,}$", low):
        _open_site(low)
        return

    # fallback
    _unknown(command)

# ----------------- HANDLE + MAIN -----------------
def handle_command(command: str) -> None:
    command = command.strip()
    if not command:
        return
    parse_and_exec(command)

def main() -> None:
    speak_text("Hello, I am Jarvis! Say or type a command.")
    while True:
        cmd = listen_command()
        handle_command(cmd)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        speak_text("Stopping. Goodbye!")
        sys.exit(0)
