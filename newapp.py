import streamlit as st
from PIL import Image
import google.generativeai as genai
import io

# --------------------
# APP CONFIG
# --------------------
st.set_page_config(page_title="Eco Chef AI", page_icon="👨‍🍳", layout="wide")

# Replace with your actual Gemini API key
genai.configure(api_key="AIzaSyB1beDaF1kv__v4pIhw8VsoCXxPmuiGL7I")

# Custom CSS to make it look modern
st.markdown("""
    <style>
    body {$ streamlit run newapp.py
        background-color: #f6fff6;
    }
    .main-title {
        font-size: 3em;
        text-align: center;
        font-weight: 700;
        color: #1d1d1d;
    }
    .subtitle {
        text-align: center;
        font-size: 1.3em;
        color: #4d4d4d;
    }
    .cta {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    .stButton button {
        background-color: #008f3d;
        color: white;
        padding: 0.75em 2em;
        border-radius: 10px;
        font-size: 1.1em;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------
# HEADER SECTION
# --------------------
st.markdown("<h1 class='main-title'>👨‍🍳 Eco Chef <span style='color:#0c8f38;'>AI</span></h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Cook it, don’t waste it.</p>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Turn your leftover ingredients into delicious recipes with AI-powered suggestions.</p>", unsafe_allow_html=True)

# --------------------
# CTA BUTTON
# --------------------
st.markdown("<div class='cta'>", unsafe_allow_html=True)
if st.button("✨ Get Started Now"):
    st.session_state['start'] = True
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --------------------
# FEATURE CARDS
# --------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 📝 List Ingredients")
    st.write("Type in the ingredients you have at hand")

with col2:
    st.markdown("### 📸 Upload Image")
    st.write("Or snap a photo of your ingredients")

with col3:
    st.markdown("### 🍳 Get Recipes")
    st.write("Receive AI-powered recipe suggestions")

st.markdown("---")

# --------------------
# IMAGE UPLOAD + AI INTEGRATION
# --------------------
uploaded = st.file_uploader("📤 Upload your fridge or ingredient photo", type=["jpg", "jpeg", "png"])

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Your Uploaded Image", use_container_width=True)

    with st.spinner("Detecting ingredients using Gemini..."):
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content([
            "List all visible fruits, vegetables, and food items in this fridge image.",
            image
        ])
        ingredients = response.text

    st.success("Detected Ingredients")
    st.write(ingredients)

    with st.spinner("Generating recipes..."):
        recipe_model = genai.GenerativeModel("models/gemini-2.5-flash")
        recipe_response = recipe_model.generate_content([
            f"Suggest 3 quick healthy recipes using only these ingredients: {ingredients}"
        ])
    st.markdown("## 🍽️ Recipe Ideas")
    st.write(recipe_response.text)
