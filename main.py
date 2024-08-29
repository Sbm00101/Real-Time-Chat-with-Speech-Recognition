from dotenv import load_dotenv
import os
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import json

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("API key not found")

recognizer = sr.Recognizer()
client = genai.GenerativeModel("gemini-1.5-flash")
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

history_file = 'conversation_history.json'

def load_history():
    """Load conversation history from a file."""
    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            return json.load(file)
    return []

def save_history(history):
    """Save conversation history to a file."""
    with open(history_file, 'w') as file:
        json.dump(history, file)

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Capture and recognize speech using the microphone."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

def generate_response(query, history):
    """Generate a response using the Google Gemini LLM, including conversation history."""
    context = " ".join(history)
    full_query = f"{context} {query}"
    response = client.generate_content(full_query)
    if response is None:
        return "No response generated"
    return response.text

def main():
    history = load_history()
    while True:
        user_input = listen()

        if user_input:
            history.append(f"User: {user_input}")
            response = generate_response(user_input, history)
            print(f"Assistant: {response}")
            speak(response)
            history.append(f"Assistant: {response}")
            save_history(history)

        if user_input and "exit" in user_input.lower():
            speak("Goodbye!")
            break

if __name__ == "__main__":
    main()
