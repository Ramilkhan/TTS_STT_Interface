import streamlit as st
import requests
import base64
import os

# -------------------------
# CONFIGURE AZURE CREDENTIALS
# -------------------------
AZURE_KEY = "FS4yBV3YjzD9gw2g8Xzcz1k8OVpIXR8QaB0NuZt5ODQmappDVzirJQQJ99BKAC3pKaRXJ3w3AAAYACOGhPZt"
AZURE_REGION = "eastasia"
AZURE_ENDPOINT = "https://eastasia.api.cognitive.microsoft.com/"

# -------------------------
# STREAMLIT UI SETTINGS
# -------------------------
st.set_page_config(page_title="Azure Speech Studio", page_icon="🎤", layout="wide")

st.markdown("""
<style>
    .big-font {font-size:30px !important; font-weight:bold;}
    .section-title {color:#4CAF50; font-size:22px; font-weight:600;}
    .stButton>button {
        background:#4CAF50;
        color:white;
        padding:10px 20px;
        border-radius:10px;
    }
    .stTextInput>div>div>input {
        border-radius:10px;
        padding:10px;
    }
    .uploadedAudio {
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🎤 Azure Speech-to-Text & Text-to-Speech</p>', unsafe_allow_html=True)
st.write("Convert text to speech or speech to text using Azure AI Speech.")

# ===========================
#       TEXT → SPEECH
# ===========================
st.markdown('<p class="section-title">🔊 Text → Speech</p>', unsafe_allow_html=True)

text_input = st.text_area("Enter text to convert into speech:", height=120)

if st.button("Convert Text to Speech"):
    if not text_input.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Converting text to speech..."):
            tts_url = f"{AZURE_ENDPOINT}tts/cognitiveservices/v1"

            ssml = f"""
            <speak version='1.0' xml:lang='en-US'>
                <voice xml:lang='en-US' name='en-US-AriaNeural'>
                    {text_input}
                </voice>
            </speak>
            """

            headers = {
                "Ocp-Apim-Subscription-Key": AZURE_KEY,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
            }

            response = requests.post(tts_url, headers=headers, data=ssml.encode("utf-8"))

            if response.status_code == 200:
                audio_data = response.content
                b64 = base64.b64encode(audio_data).decode()

                st.audio(audio_data, format="audio/mp3")
                st.download_button(
                    label="Download MP3",
                    data=audio_data,
                    file_name="tts_audio.mp3",
                    mime="audio/mp3"
                )
            else:
                st.error(f"TTS Error: {response.text}")

st.write("---")

# ===========================
#       SPEECH → TEXT
# ===========================
st.markdown('<p class="section-title">🎧 Speech → Text</p>', unsafe_allow_html=True)

uploaded_audio = st.file_uploader("Upload an audio file (WAV/MP3)", type=["wav", "mp3", "m4a"])

if uploaded_audio is not None:
    st.audio(uploaded_audio, format="audio/wav")
    audio_bytes = uploaded_audio.read()

if st.button("Convert Speech to Text"):
    if uploaded_audio is None:
        st.warning("Please upload an audio file first.")
    else:
        with st.spinner("Transcribing..."):
            stt_url = f"https://{AZURE_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"

            headers = {
                "Ocp-Apim-Subscription-Key": AZURE_KEY,
                "Content-Type": "audio/wav"  # works for mp3 as well
            }

            response = requests.post(stt_url, headers=headers, data=audio_bytes)

            if response.status_code == 200:
                try:
                    result = response.json()
                    st.success("Transcription Successful!")
                    st.write("### Output Text:")
                    st.write(result.get("DisplayText", "No text recognized."))
                except:
                    st.error("Error reading transcription response.")
            else:
                st.error(f"STT Error: {response.text}")
