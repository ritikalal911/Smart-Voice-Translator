import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import io
import pygame
from audio_recorder_streamlit import audio_recorder

def recognize_from_mic():
    # Use audio_recorder from the new package
    audio_bytes = audio_recorder()
    
    if audio_bytes:
        try:
            # Create a temporary file to store the audio
            with io.BytesIO(audio_bytes) as audio_file:
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_file) as source:
                    audio = recognizer.record(source)
                    text = recognizer.recognize_google(audio, language="en-IN")
                    return text
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError:
            return "Could not request results, check your internet connection."
        except Exception as e:
            return f"Error processing audio: {e}"
    return None

def translate_text(text, dest_lang):
    translator = Translator()
    try:
        translated = translator.translate(text, src='auto', dest=dest_lang)
        return translated.text if translated else "Translation failed."
    except Exception as e:
        return f"Translation error: {e}"

def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        pygame.mixer.init()
        pygame.mixer.music.load(audio_fp, 'mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    except Exception as e:
        st.error(f"Error in text-to-speech: {e}")

st.set_page_config(page_title="Speech Translator", layout="wide")
st.markdown("<h1 style='text-align: center;'>Speech Recognition & Translation App</h1>", unsafe_allow_html=True)

st.header("🎤 Speech Recognition")
col1, col2 = st.columns(2)

with col1:
    if "recognized_text" not in st.session_state:
        st.session_state["recognized_text"] = ""
    
    # st.write("Click the microphone icon to start recording:")
    result = recognize_from_mic()
    if result:
        st.session_state["recognized_text"] = result
        
    st.text_area("Recognized Text", st.session_state["recognized_text"], height=150)

st.header("🌎 Translation")
language_groups = {
    "Indo-Aryan Languages": {"English": "en", "Hindi": "hi", "Punjabi": "pa", "Marathi": "mr", "Bengali": "bn", "Gujarati": "gu", "Urdu": "ur"},
    "South Indian Languages": {"Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml"},
    "European Languages": {"Spanish": "es", "French": "fr", "German": "de", "Italian": "it", "Dutch": "nl", "Portuguese": "pt", "Russian": "ru"},
    "East Asian Languages": {"Japanese": "ja", "Chinese": "zh-cn", "Korean": "ko"},
    "Middle Eastern Languages": {"Arabic": "ar"}
}

selected_group = st.selectbox("Select Language Group", list(language_groups.keys()))
selected_language = st.selectbox("Select Language for Translation", list(language_groups[selected_group].keys()))

with col2:
    if "translated_text" not in st.session_state:
        st.session_state["translated_text"] = ""
    if st.button("🔄 Translate", use_container_width=True):
        if st.session_state["recognized_text"]:
            st.session_state["translated_text"] = translate_text(st.session_state["recognized_text"], language_groups[selected_group][selected_language])
        else:
            st.warning("Please recognize speech first before translating.")
    st.text_area("Translated Text", st.session_state["translated_text"], height=150)

st.header("🔊 Speak Translation")
if st.button("📢 Play Audio", use_container_width=True):
    if st.session_state["translated_text"]:
        speak_text(st.session_state["translated_text"], language_groups[selected_group][selected_language])
    else:
        st.warning("Please translate text first before playing audio.")
