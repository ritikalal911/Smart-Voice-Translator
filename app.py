import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import io

def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)  # Helps prevent background noise errors
            st.info("Listening... Please speak now.")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="en-IN")
            return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Could not request results, check your internet connection."
    except Exception as e:
        return f"Error: {e}"

def translate_text(text, dest_lang):
    translator = Translator()
    try:
        translated = translator.translate(text, src='auto', dest=dest_lang)
        return translated.text if translated else "Translation failed."
    except Exception as e:
        return f"Translation error: {e}"

def speak_text(text, lang_code):
    try:
        if not text.strip():
            st.warning("No text to speak.")
            return
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # Play audio directly in Streamlit
        st.audio(audio_fp, format='audio/mp3')
    except Exception as e:
        st.error(f"Error in text-to-speech: {e}")

# UI Layout Optimized for Mobile
st.set_page_config(page_title="Speech Translator", layout="centered")
st.title("🌍 Speech Recognition & Translation App")

st.subheader("🎤 Speech Recognition")
if "recognized_text" not in st.session_state:
    st.session_state["recognized_text"] = ""

if st.button("🎙️ Start Listening", use_container_width=True):
    st.session_state["recognized_text"] = recognize_speech()

st.text_area("Recognized Text", st.session_state["recognized_text"], height=100)

st.subheader("🌎 Translation")
language_groups = {
    "Indo-Aryan Languages": {"English": "en", "Hindi": "hi", "Punjabi": "pa", "Marathi": "mr", "Bengali": "bn", "Gujarati": "gu", "Urdu": "ur"},
    "South Indian Languages": {"Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml"},
    "European Languages": {"Spanish": "es", "French": "fr", "German": "de", "Italian": "it", "Dutch": "nl", "Portuguese": "pt", "Russian": "ru"},
    "East Asian Languages": {"Japanese": "ja", "Chinese": "zh-cn", "Korean": "ko"},
    "Middle Eastern Languages": {"Arabic": "ar"}
}

selected_group = st.selectbox("Select Language Group", list(language_groups.keys()))
selected_language = st.selectbox("Select Translation Language", list(language_groups[selected_group].keys()))

if "translated_text" not in st.session_state:
    st.session_state["translated_text"] = ""

if st.button("🔄 Translate", use_container_width=True):
    if st.session_state["recognized_text"]:
        st.session_state["translated_text"] = translate_text(st.session_state["recognized_text"], language_groups[selected_group][selected_language])
    else:
        st.warning("Please recognize speech first before translating.")

st.text_area("Translated Text", st.session_state["translated_text"], height=100)

st.subheader("🔊 Speak Translation")
if st.button("📢 Play Audio", use_container_width=True):
    if st.session_state["translated_text"]:
        speak_text(st.session_state["translated_text"], language_groups[selected_group][selected_language])
    else:
        st.warning("Please translate text first before playing audio.")
