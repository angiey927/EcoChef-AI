import streamlit as st
from PIL import Image
import google.generativeai as genai
import io
import time
import re
from streamlit.components.v1 import html
import re
import pandas as pd
from PIL import Image
import base64
from io import BytesIO

def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --------------------
# APP CONFIG
# --------------------
# Load and resize icon
icon = Image.open("assets/Logo.png")
icon = icon.resize((200, 200), Image.Resampling.LANCZOS)  # Resize to appropriate icon size

st.set_page_config(page_title="Eco Chef AI", page_icon=icon, layout="wide")

# Add resized icon inline with title
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
        <img src="data:image/png;base64,{}" style="width: 40px; height: 40px; object-fit: contain;">
        <h1 class="main-title" style="margin: 0;">Eco Chef AI</h1>
    </div>
    """.format(
        image_to_base64(icon)
    ),
    unsafe_allow_html=True
)

# Replace with your actual Gemini API key
genai.configure(api_key="AIzaSyB1beDaF1kv__v4pIhw8VsoCXxPmuiGL7I")

# Custom CSS to make it look modern
st.markdown("""
     <style>
    /* Entire page background */
    [data-testid="stAppViewContainer"] {
        background-color: #f0fff0;  /* soft light green */
    }
    /* Main content container */
    [data-testid="stMainContainer"] {
    background-color: #f0fff0;
    }
    body {$ streamlit run newapp.py
        background-color: #f0fff0;
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
    Remove white gaps around Streamlit main area */
    .css-18e3th9 { background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# --------------------
# HEADER SECTION
# --------------------
#Tagline

# --- Tagline in script font ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">

<p style="
    text-align: center;
    font-size: 1em;
    color: #0c8f38;
    font-family: 'Pacifico', cursive;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
">
    Cook it, don’t waste it.
</p>
""", unsafe_allow_html=True)

#Description of features
# Inject HTML + CSS animation
st.markdown("""
<style>
.subtitle-container {
  position: relative;
  height: 2em;
  overflow: hidden;
  font-size: 1.5em;
  font-weight: 600;
  color: #228B22;
  text-align: center;
  margin: 1em auto;
  width: 80%;
}

.subtitle-container span {
  position: absolute;
  width: 100%;
  left: 0;
  opacity: 0;
  animation: cycleTaglines 9s infinite;
}

.subtitle-container span:nth-child(1) { animation-delay: 0s; }
.subtitle-container span:nth-child(2) { animation-delay: 3s; }
.subtitle-container span:nth-child(3) { animation-delay: 6s; }

@keyframes cycleTaglines {
  0% { opacity: 0; transform: translateY(100%); }
  10% { opacity: 1; transform: translateY(0%); }
  30% { opacity: 1; transform: translateY(0%); }
  40% { opacity: 0; transform: translateY(-100%); }
  100% { opacity: 0; }
}
            
* --- Mobile optimization --- */
@media (max-width: 768px) {
  .subtitle-text {
    font-size: 0.95em;
    animation: scroll-subtitle 20s linear infinite;
  }
  .subtitle-container {
    padding: 4px 0;
  }
}
</style>

<div class="subtitle-container">
  <span>Turn your leftover ingredients into delicious recipes with AI-powered suggestions.</span>
  <span>Connect your groceries list to shop smarter and greener.</span>
  <span>Show us what's in your fridge, and we'll supply the recipes, customized for you.</span>
</div>
            
</style>
""", unsafe_allow_html=True)

# --------------------
# CTA BUTTON
# --------------------
st.markdown("<div class='cta'>", unsafe_allow_html=True)
if st.button("✨ Get Started Now"):
    st.session_state['start'] = True
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# Add feature card styles
st.markdown("""
<style>
.feature-card {
    background-color: white;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border: 2px solid #228B22;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    border-color: #3B7A38;
}
.feature-card h3 {
    color: #228B22;
    margin-bottom: 1rem;
}
.feature-card p {
    color: #666;
    line-height: 1.5;
}
.features-container {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin: 2rem 0;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# --------------------
# FEATURE CARDS
# --------------------
st.markdown("<div class='features-container'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class='feature-card'>
        <h3>📝 List Ingredients</h3>
        <p>Type in the ingredients you have at hand</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
        <h3>📸 Upload Image</h3>
        <p>Or snap a photo of your ingredients</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='feature-card'>
        <h3>🍳 Get Recipes</h3>
        <p>Receive AI-powered recipe suggestions</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# --------------------
# CUSTOM CSS FOR GREEN THEME
# --------------------
st.markdown("""
<style>
/* Page background */
body, .css-18e3th9 { 
    background-color: #f0fff0;  /* soft light green */
}

/* File uploader container */
div.stFileUploader {
    border: 2px dashed #00a651;
    border-radius: 16px;
    padding: 1rem;
    background-color: #ffffff;
    color: #145A32;
    font-weight: 600;
    text-align: center;
}

/* Hover effect for uploader */
div.stFileUploader:hover {
    border-color: #008f3d;
    background-color:#f0fff0;
}

/* Uploaded image preview */
div.stImage img {
    border-radius: 12px;
    border: 2px solid #00a651;
}

/* Headings inside uploader */
div.stFileUploader label {
    color: #0c8f38;
    font-weight: bold;
    font-size: 1.1em;
}
</style>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("📤 Upload your fridge or ingredient photo", type=["jpg", "jpeg", "png"])

if uploaded:
    # Convert UploadedFile → PIL image
    image = Image.open(uploaded)

    # Inline preview (small thumbnail)
    st.image(image, width=150, caption="Preview")

    # Convert image to bytes (Gemini requires this)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    # Send to Gemini
    with st.spinner("🔍 Detecting ingredients using Gemini..."):
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content([
            "List all visible fruits, vegetables, and food items in this fridge image, "
            "grouped into categories (e.g., Fruits, Vegetables, Dairy, Protein, etc.). "
            "Output in a clean, structured bullet format.",
            {"mime_type": "image/jpeg", "data": img_bytes.getvalue()}
        ])
        ingredients_text = response.text.strip()

    st.success("✅ Detected Ingredients")

    # --------------------
    # Parse Gemini response into table robustly
    # --------------------
    # Strip everything before first header or bullet
    lines = ingredients_text.strip().split("\n")

    # Find index of first header/bullet line
    start_idx = 0
    for i, line in enumerate(lines):
        if re.match(r"^[-*•]\s+", line) or (line.strip() and not line.startswith("Here")):
            start_idx = i
            break

    # Only keep lines from start_idx onward
    lines = lines[start_idx:]

    data = {}
    current_header = None
    bullet_pattern = r"^[-*•]\s+"

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(bullet_pattern, line):
            if current_header:
                data[current_header].append(re.sub(bullet_pattern, "", line).strip())
        else:
            current_header = line.rstrip(":")
            data[current_header] = []

    # Normalize column lengths
    max_len = max(len(v) for v in data.values()) if data else 0
    for key in data:
        data[key] += [""] * (max_len - len(data[key]))

    df = pd.DataFrame(data)
    
    # Custom styling for the dataframe
    st.markdown("""
    <style>
    .stDataFrame {
        background-color: #f0fff0;
        border-radius: 16px;
        padding: 1rem;
        border: 2px solid #00a651;
        border-color: #3B7A38;
    }
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background-color: transparent !important;
    }
    .stDataFrame thead tr {
        background-color: #0c8f38 !important;
        color: white !important;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: rgba(12, 143, 56, 0.05);
    }
    .stDataFrame th, .stDataFrame td {
        border: none !important;
        text-align: left !important;
        padding: 8px 16px !important;
    }
    .stDataFrame [data-testid="StyledDataFrameDataCell"] {
        font-size: 0.95rem;
    }
    .stDataFrame [data-testid="StyledDataFrameRowHeaderCell"] {
        display: none !important;
    }
    .stDataFrame [data-testid="column-header-index"] {
        display: none !important;
    }
    .stDataFrame [data-testid="index"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(df, hide_index=True, use_container_width=True)


    # --------------------
    # GENERATE RECIPES
    # --------------------
    # Flatten all items in the dataframe into a comma-separated string
    ingredients_list = df.fillna("").values.flatten().tolist()
    ingredients_list = [i for i in ingredients_list if i]  # remove empty strings
    ingredients_str = ", ".join(ingredients_list)

    with st.spinner("Generating recipes..."):
        recipe_model = genai.GenerativeModel("models/gemini-2.5-flash")
        recipe_response = recipe_model.generate_content([
            f"Suggest 4 quick healthy recipes using only these ingredients: {ingredients_str}. Format it like 1. Recipe Name: Description. Ingredients. Concise numbered steps. Also, no preamble."
        ])
    st.markdown("## 🍽️ Recipe Ideas")
    # --- Parse Gemini's output into recipe cards ---
    recipes_raw = recipe_response.text.strip()

    # Remove common preamble phrases (case-insensitive)
    preamble_pattern = r"(?i)^(here|here's|here are|here is|the recipes are|these recipes).*?:?\s*"
    recipes_cleaned = re.sub(preamble_pattern, "", recipes_raw, count=1).strip()

    # Split by numbered or titled recipes
    recipe_blocks = re.split(r'\n\d+\.|\nRecipe\s*\d+:', recipes_cleaned)
    recipes = [r.strip() for r in recipe_blocks if r.strip()]

    # Optional: ensure each recipe has a title and description
    parsed_recipes = []
    for r in recipes:
        title_match = re.match(r"^([A-Z][A-Za-z\s,&'-]+):", r)
        title = title_match.group(1) if title_match else "Recipe"
        description = r[len(title):].strip() if title_match else r
        parsed_recipes.append((title, description))


    # Try splitting by numbers or bullets
    recipes = re.split(r'\n\d+\.\s*', recipes_raw)
    recipes = [r.strip() for r in recipes if r.strip()]

    # --- Build grid card layout ---
    card_html = """
    <style>
    .card-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1.5rem;
        padding: 1rem;
        margin: 0 auto;
        max-width: 1200px;
    }

    /* Recipe Card */
    .recipe-card {
        background-color: #ffffff;
        border: 2px solid #00a651;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        height: 200px;  /* Fixed height */
        position: relative;
    }

    .recipe-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.1);
        border-color: #0c8f38;
    }

    .recipe-card::after {
        content: '→';
        position: absolute;
        bottom: 1rem;
        right: 1rem;
        color: #0c8f38;
        font-size: 1.2em;
        opacity: 0;
        transition: opacity 0.2s ease;
        background: linear-gradient(transparent, #f0fff0 40%);
        padding: 2rem 1rem 0.5rem;
        margin: 0 -1.25rem;
        width: 100%;
        text-align: right;
    }

    .recipe-card:hover::after {
        opacity: 1;
    }

    .recipe-title {
        font-family: 'Source Sans Pro', 'Segoe UI', 'Roboto', sans-serif;
        font-weight: 700;
        color: #0c8f38;
        font-size: 1.25em;
        line-height: 1.3;
        border-bottom: 2px solid rgba(12, 143, 56, 0.1);
        padding-bottom: 0.5rem;
        margin: 0 0 0.75rem 0;
        flex-shrink: 0;  /* Prevent title from shrinking */
    }

    .preview-text {
        font-family: 'Source Sans Pro', 'Segoe UI', 'Roboto', sans-serif;
        font-size: 0.95em;
        color: #444;
        line-height: 1.5;
        overflow-y: auto;  /* Enable scrolling */
        padding-right: 0.5rem;  /* Space for scrollbar */
        margin-bottom: 2rem;  /* Space for arrow */
    }

    /* Scrollbar styling */
    .preview-text::-webkit-scrollbar {
        width: 6px;
    }

    .preview-text::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.05);
        border-radius: 3px;
    }

    .preview-text::-webkit-scrollbar-thumb {
        background: rgba(12, 143, 56, 0.2);
        border-radius: 3px;
    }

    .preview-text::-webkit-scrollbar-thumb:hover {
        background: rgba(12, 143, 56, 0.3);
    }

    /* Modal */
    .modal {
        display: none; 
        position: fixed; 
        z-index: 1000; 
        left: 0;
        top: 0;
        width: 100%; 
        height: 100%; 
        overflow: auto; 
        background-color: rgba(0,0,0,0.5);
    }

    .modal-content {
        background-color: #f0fff0;
        margin: 5% auto; 
        padding: 2.5rem;
        border: 2px solid #00a651;
        border-radius: 16px;
        width: 90%; 
        max-width: 700px;
        position: relative;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        animation: modalSlideIn 0.3s ease;
    }

    @keyframes modalSlideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .close-btn {
        color: #666;
        position: absolute;
        top: 1rem;
        right: 1.25rem;
        font-size: 1.5em;
        font-weight: normal;
        cursor: pointer;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: all 0.2s ease;
        background: rgba(0,0,0,0.05);
    }

    .close-btn:hover {
        background: rgba(0,0,0,0.1);
        color: #333;
    }

    .modal-content h3 {
        font-family: 'Source Sans Pro', 'Segoe UI', 'Roboto', sans-serif;
        color: #0c8f38;
        font-size: 1.5em;
        margin-top: 0;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(12, 143, 56, 0.1);
    }

    .modal-content p {
        font-family: 'Source Sans Pro', 'Segoe UI', 'Roboto', sans-serif;
        line-height: 1.6;
        color: #444;
        font-size: 1.05em;
        white-space: pre-line;
    }

    .made-btn {
        background-color: #0c8f38;
        color: white;
        border: none;
        padding: 0.75em 1.25em;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
        font-size: 0.95em;
        box-shadow: 0 2px 6px rgba(12, 143, 56, 0.2);
        min-width: 120px;
    }

    .made-btn:hover {
        background-color: #0a7f30;
        box-shadow: 0 3px 8px rgba(12, 143, 56, 0.3);
    }

    .made-btn.toggled {
        background-color: #666;
    }
    
    .made-btn.toggled:hover {
        background-color: #3B7A38;
    }
    </style>

    <div class="card-container">
    """

    # --- Add cards ---
    for i, r in enumerate(recipes, 1):
        title_match = re.match(r"^([\w\s,&'-]+):", r)
        title = title_match.group(1) if title_match else f"Recipe {i}"
        description = r[len(title):].strip() if title_match else r
        preview = description[:100] + ("..." if len(description) > 100 else "")

        # Unique IDs for modal & button
        modal_id = f"modal_{i}"
        btn_id = f"btn_{i}"

        card_html += f"""
        <div class="recipe-card" onclick="document.getElementById('{modal_id}').style.display='block'">
            <div class="recipe-title">{title}</div>
            <div class="preview-text">{preview}</div>
        </div>

        <!-- Modal -->
        <div id="{modal_id}" class="modal">
            <div class="modal-content">
                <span class="close-btn" onclick="document.getElementById('{modal_id}').style.display='none'">&times;</span>
                <button id="{btn_id}" class="made-btn" onclick="event.stopPropagation(); this.classList.toggle('toggled');">I made this!</button>
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
        </div>
        """

    # Close the card container div after all cards have been added
    card_html += "</div>"

    # Render in Streamlit
    html(card_html, height=400)