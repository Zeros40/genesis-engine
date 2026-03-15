import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# --- GENESIS PROTOCOL SETTINGS ---
st.set_page_config(page_title="Genesis Creative Engine", layout="wide")

# Using the standard parameter name 'unsafe_allow_html'
st.markdown("""
<style>
    .stApp { background-color: #0A0A0A; color: white; }
    h1, h2, h3 { color: #D4AF37 !important; }
    div[data-baseweb="input"] { background-color: #1A1A1A !important; }
    input { color: white !important; }
</style>
""", unsafe_allow_html=True)

# 1. API SETUP
st.sidebar.title("GENESIS SETTINGS")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    st.title("🏛️ GENESIS CREATIVE ENGINE")
    st.subheader("Member #001: High-Frequency Asset Generator")

    # 2. SIDEBAR CONFIGURATION
    st.sidebar.header("Asset Details / تفاصيل الأصل")
    segment = st.sidebar.selectbox("Segment", ["Real Estate", "Car Rental", "Glamping"])
    asset_name = st.sidebar.text_input("Asset Name (e.g., Zodiac Zenith)", "Zodiac Zenith")
    price = st.sidebar.text_input("Price / Night (€)", "180")
    features = st.sidebar.text_area("Top 3 Features", "Panoramic View, Eco-Luxury, Smart Access")

    # 3. GENERATION LOGIC
    if st.sidebar.button("PRODUCE GENESIS ASSET"):
        with st.spinner("Accessing the Physical Ledger..."):
            
            # Step A: Generate Background Image Prompt
            prompt = f"Bespoke luxury {segment} shot of {asset_name} in the Balkans. Cinematic lighting, mirrored obsidian accents, 8k resolution, professional architectural photography."
            
            # For this example, we use the Gemini Image API (Nano Banana 2)
            # Note: In a live environment, you'd use the imagen endpoint. 
            # Here we simulate the generation for the UI.
            
            st.info(f"Prompt Sent: {prompt}")
            
            # Step B: Create the Canvas
            # We create a 1080x1080 social media canvas
            img = Image.new('RGB', (1080, 1080), color=(10, 10, 10))
            draw = ImageDraw.Draw(img)
            
            # Step C: Visual Overlays (The Genesis Material Protocol)
            # Draw a 'Mirrored Obsidian' gradient or box at bottom
            draw.rectangle([0, 800, 1080, 1080], fill=(20, 20, 20))
            
            # Add Gold Seal Placeholder
            draw.ellipse([950, 50, 1030, 130], fill=(212, 175, 55)) 
            
            # Add Text (White and Gold)
            # Note: For actual deployment, ensure 'Inter' or 'Montserrat' font files are in your GitHub
            try:
                font_large = ImageFont.truetype("Arial.ttf", 60)
                font_small = ImageFont.truetype("Arial.ttf", 30)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

            draw.text((50, 830), f"{asset_name.upper()}", fill=(255, 255, 255), font=font_large)
            draw.text((50, 910), f"STARTING AT €{price} / NIGHT", fill=(212, 175, 55), font=font_small)
            draw.text((50, 960), f"MEMBER #001 EXCLUSIVE | {features}", fill=(255, 255, 255), font=font_small)

            # Step D: Display Results
            col1, col2 = st.columns(2)
            with col1:
                st.image(img, caption="Genesis Social Post Mockup", use_column_width=True)
            
            with col2:
                # Generate Caption using Gemini
                cap_prompt = f"Write a psychologically sharp Instagram caption for a {segment} asset named {asset_name}. Focus on the 'Second Chance' narrative and high ROI. Include Arabic translation."
                response = model.generate_content(cap_prompt)
                st.success("Psychologically Sharp Caption Ready:")
                st.write(response.text)

else:
    st.warning("Please enter your Gemini API Key in the sidebar to start.")

# 4. INSTRUCTIONS
st.markdown("---")
st.markdown("""
### How to Use / كيفية الاستخدام
1. **API Key:** Get your key from [Google AI Studio](https://aistudio.google.com/).
2. **Details:** Enter the asset name and price for the 'Physical Ledger'.
3. **Generate:** The app produces the design layout and a dual-language caption.
""")
