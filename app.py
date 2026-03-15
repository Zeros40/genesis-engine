import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
from elevenlabs import generate, save, set_api_key
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import os

# --- GENESIS PROTOCOL SETTINGS ---
st.set_page_config(page_title="Genesis Creative Engine", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0A0A0A; color: white; }
    h1, h2, h3 { color: #D4AF37 !important; }
    div[data-baseweb="input"] { background-color: #1A1A1A !important; }
    input { color: white !important; }
</style>
""", unsafe_allow_html=True)

# 1. API SETUP (Sidebar)
st.sidebar.title("GENESIS COMMAND CENTER")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
eleven_key = st.sidebar.text_input("ElevenLabs API Key (For Voice)", type="password")

if gemini_key:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    st.title("🏛️ GENESIS CREATIVE ENGINE")
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Asset Specifications")
        segment = st.selectbox("Business Segment", ["Real Estate", "Car Rental", "Glamping"])
        asset_name = st.text_input("Asset Name", "Zodiac Zenith")
        price = st.text_input("Price per Night/Day (€)", "180")
        description = st.text_area("Narration Script (What the AI will say)", 
                                   f"Welcome to the {asset_name}. A second chance at luxury, starting at {price} euros.")

    with col2:
        st.subheader("Media Upload")
        uploaded_video = st.file_uploader("Upload Drone/Asset Video (MP4)", type=["mp4", "mov"])

    # 2. GENERATION LOGIC
    if st.button("PRODUCE GENESIS REEL / تصميم الفيديو"):
        if not eleven_key and uploaded_video:
            st.error("Please provide an ElevenLabs key for Voice-over.")
        elif uploaded_video:
            with st.spinner("Generating Voice and Processing Video..."):
                # A. Generate Voice-over
                set_api_key(eleven_key)
                audio = generate(text=description, voice="Josh", model="eleven_multilingual_v2")
                save(audio, "temp_voice.mp3")

                # B. Process Video with MoviePy
                # Save uploaded file locally first
                with open("input_video.mp4", "wb") as f:
                    f.write(uploaded_video.read())
                
                video = VideoFileClip("input_video.mp4")
                
                # C. Overlay Text (Floating HUD Style)
                # Note: 'ffmpeg' must be in packages.txt for this to work on Streamlit
                txt_overlay = TextClip(f"{asset_name.upper()}\n€{price}", 
                                       fontsize=70, color='white', font='Arial-Bold', 
                                       method='caption', size=(video.w, None)).set_duration(video.duration).set_position('center')
                
                # D. Merge Audio & Video
                final_audio = AudioFileClip("temp_voice.mp3")
                final_reel = video.set_audio(final_audio)
                result_video = CompositeVideoClip([final_reel, txt_overlay])
                
                result_video.write_videofile("genesis_output.mp4", codec="libx264", audio_codec="aac")
                
                st.video("genesis_output.mp4")
                st.success("Bespoke Luxury Reel Ready for Upload.")

else:
    st.warning("Awaiting Gemini API Key to activate the Physical Ledger...")
