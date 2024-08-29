import threading
from dotenv import load_dotenv
import os
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import json
import streamlit as st

# Load environment variables
load_dotenv()

# Initialize Google Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API key not found")

# Initialize speech recognition, TTS, and history handling
recognizer = sr.Recognizer()
client = genai.GenerativeModel("gemini-1.5-flash")
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

history_file = 'conversation_history.json'

def load_history():
    """Load conversation history from a file, handling empty or corrupted files."""
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    return []

def save_history(history):
    """Save conversation history to a file."""
    with open(history_file, 'w') as file:
        json.dump(history, file)

def speak(text):
    """Convert text to speech in a separate thread to avoid loop conflicts."""
    def _speak():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak).start()

def generate_response(query, history):
    """Generate a response using the Google Gemini LLM, including conversation history."""
    context = " ".join(history)
    full_query = f"{context} {query}"
    response = client.generate_content(full_query)
    if response is None:
        return "No response generated"
    return response.text

# Streamlit Interface
st.title("Real-Time Chat with Speech Recognition")

if st.button("Start Listening"):
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            user_input = recognizer.recognize_google(audio)
            st.write(f"You said: {user_input}")

            # Load history
            history = load_history()

            # Generate response
            if user_input:
                history.append(f"User: {user_input}")
                response = generate_response(user_input, history)
                st.write(f"Assistant: {response}")

                # Text-to-speech output
                speak(response)

                # Save history
                history.append(f"Assistant: {response}")
                save_history(history)

                if "exit" in user_input.lower():
                    st.write("Goodbye!")
        except sr.UnknownValueError:
            st.write("Sorry, I did not understand that.")
        except sr.RequestError as e:
            st.write(f"Could not request results; {e}")

if st.button("Clear History"):
    if os.path.exists(history_file):
        os.remove(history_file)
        st.write("Conversation history cleared.")
    else:
        st.write("No history to clear.")
