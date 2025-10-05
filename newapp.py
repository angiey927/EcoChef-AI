import re
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
from user_store import init_db, create_user_record, verify_user_record

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

init_db()

# ===============================
# PAGE CONFIG
# ===============================

# Configure Gemini (use your key)
genai.configure(api_key="AIzaSyB1beDaF1kv__v4pIhw8VsoCXxPmuiGL7I")

# ===============================
# SESSION STATE
# ===============================
if "modal" not in st.session_state:
    st.session_state.modal = None  # None | 'signup' | 'login'
if "su_show_errors" not in st.session_state:
    st.session_state.su_show_errors = False
if "li_show_errors" not in st.session_state:
    st.session_state.li_show_errors = False
# auth
if "is_authed" not in st.session_state:
    st.session_state.is_authed = False
if "display_name" not in st.session_state:
    st.session_state.display_name = ""
# manual ingredients + detected-from-image
if "ingredients" not in st.session_state:
    st.session_state.ingredients = []  # list[{name, category, qty, unit}]
if "detected_ingredients_text" not in st.session_state:
    st.session_state.detected_ingredients_text = ""  # raw text from Gemini vision

def open_modal(name: str):
    st.session_state.modal = name
    st.rerun()

def close_modal():
    st.session_state.modal = None
    st.rerun()

# ===============================
# VALIDATION HELPERS
# ===============================
ALLOWED_DOMAINS = ("gmail.com", "yahoo.com", "hotmail.com", "school.edu")
EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+-]+@(?:gmail\.com|yahoo\.com|hotmail\.com|school\.edu)$"
)
PWD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$")

def validate_name(name: str):
    if not (name or "").strip():
        return False, "Full name is required."
    return True, None

def validate_email(email: str):
    email = (email or "").strip()
    if not email:
        return False, "Email is required."
    if not EMAIL_RE.match(email):
        if "@" in email and email.split("@")[-1] not in ALLOWED_DOMAINS:
            return False, f"Email must end with one of: {', '.join(ALLOWED_DOMAINS)}."
        return False, "Enter a valid email address."
    return True, None

def validate_password(pwd: str):
    if not pwd:
        return False, "Password is required."
    if not PWD_RE.match(pwd):
        return False, "Use letters & numbers only, include at least one letter and one number, minimum 6 characters."
    return True, None

def name_from_email(email: str) -> str:
    local = (email or "").split("@")[0]
    local = local.replace(".", " ").replace("_", " ").replace("-", " ")
    return local.title() if local else "there"

# ===============================
# CSS (green theme + inline errors + welcome banner)
# ===============================
st.markdown("""
<style>
:root { --primary-color:#00b050; }
body { background:#f6fff6; }

.main-title{font-size:3rem;text-align:center;font-weight:800;color:#1d1d1d;margin:.25rem 0;}
.subtitle{ text-align:center;font-size:1.1rem;color:#4d4d4d;margin-top:.25rem;}

.cta{ display:flex; justify-content:center; margin-top:24px; }
.cta .stButton>button{
  background:#00b050 !important; color:#fff !important;
  padding:12px 28px !important; border-radius:12px !important;
  font-size:1.05rem !important; font-weight:600 !important; border:none !important;
  box-shadow:0 6px 18px rgba(0,176,80,.25) !important; transition:all .2s ease-in-out !important;
}
.cta .stButton>button:hover{ background:#009645 !important; transform:translateY(-2px); }

.stDialog > div{ border-radius:20px !important; }
.stDialog h1,.stDialog h2,.stDialog h3{ text-align:center; margin-bottom:0; }
.stDialog p.lead{ text-align:center; color:#536066; margin:6px 0 18px; }

.stDialog div[data-testid="stTextInput"] input{
  border-radius:12px; padding:12px 14px; border:1px solid #e2e8f0;
}

.stDialog button[kind="primary"],
.stDialog button[data-testid="baseButton-primary"]{
  background:#00b050 !important; color:#fff !important; border:none !important;
  border-radius:9999px !important; padding:10px 22px !important;
  display:block !important; margin:8px auto 0 !important;
  width:auto !important; min-width:110px !important;
  box-shadow:0 8px 20px rgba(0,176,80,.25) !important; transition:all .2s ease-in-out !important;
}
.stDialog button[kind="primary"]:hover{ background:#009645 !important; transform:translateY(-2px); }

.cta-legend{ text-align:center; font-size:.95rem; color:#4b5563; margin:10px 0 6px; }

.field-error{ color:#e11d48; font-size:0.90rem; margin:6px 2px 0; }

.welcome {
  max-width: 720px; margin: 18px auto 0; padding: 10px 14px;
  border-radius: 14px; background: #e9f8ef; border: 1px solid #bfead0;
  color: #14532d; text-align: center; font-weight: 600;
}

/* manual bar */
.manual-card{ background:#f3fdf7; border:1px solid #bfead0; border-radius:14px; padding:14px 16px; box-shadow:0 6px 18px rgba(0,176,80,.06); }
.manual-card input, .manual-card select{ border-color:#118a3a !important; }
.ingredient-chip{
  display:inline-flex; align-items:center; gap:8px; padding:6px 10px;
  margin:6px 6px 0 0; background:#e9f8ef; border:1px solid #bfead0; border-radius:9999px;
  font-size:0.92rem; color:#14532d;
}
.ingredient-chip small{ opacity:.75; }
</style>
""", unsafe_allow_html=True)

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
<style>
.manual-card{
  background: transparent;   /* no green */
  border: none;              /* no border */
  border-radius: 0;
  padding: 0;                /* no extra top space */
}
/* Optional: also remove Streamlit’s default expander body padding */
[data-testid="stExpander"] > details > div[role='group']{
  padding-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)



# ===============================
# HEADER
# ===============================
st.markdown("<h1 class='main-title'>👨‍🍳 Eco Chef <span style='color:#00b050;'>AI</span></h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Cook it, don’t waste it.</p>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Turn your leftover ingredients into delicious recipes with AI-powered suggestions.</p>", unsafe_allow_html=True)

# Welcome banner
if st.session_state.is_authed and st.session_state.display_name:
    st.markdown(f"<div class='welcome'>👋 Welcome, {st.session_state.display_name}!</div>", unsafe_allow_html=True)

# ===============================
# LANDING CTA (centered) — hidden when authed
# ===============================
if not st.session_state.is_authed:
    left, center, right = st.columns([1, 0.2, 1])
    with center:
        st.markdown("<div class='cta'>", unsafe_allow_html=True)
        if st.button("✨ Get Started"):
            open_modal("signup")
        st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# SIGNUP MODAL
# ===============================
@st.dialog("Get Started", width="large")
def signup_modal():
    st.markdown("<p class='lead'>Create an account to start reducing food waste</p>", unsafe_allow_html=True)
    show = st.session_state.su_show_errors

    with st.form("signup_form", clear_on_submit=False):
        full_name = st.text_input("Full Name", placeholder="John Doe", key="su_name")
        name_err = validate_name(full_name)[1] if show else None
        if name_err: st.markdown(f"<div class='field-error'>{name_err}</div>", unsafe_allow_html=True)

        email = st.text_input("Email Address", placeholder="you@example.com", key="su_email")
        email_err = validate_email(email)[1] if show else None
        if email_err: st.markdown(f"<div class='field-error'>{email_err}</div>", unsafe_allow_html=True)

        pwd = st.text_input("Password", type="password", placeholder="••••••••", key="su_pwd")
        pwd_err = validate_password(pwd)[1] if show else None
        if pwd_err: st.markdown(f"<div class='field-error'>{pwd_err}</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Create Account", type="primary")
        if submitted:
            st.session_state.su_show_errors = True
            ok_name, _ = validate_name(full_name)
            ok_email, _ = validate_email(email)
            ok_pwd,  _ = validate_password(pwd)
            if ok_name and ok_email and ok_pwd:
                ok, msg = create_user_record(full_name, email, pwd)
                if not ok:
                    st.error(msg)
                else:
                    st.session_state.is_authed = True
                    st.session_state.display_name = full_name.strip()
                    st.session_state.su_show_errors = False
                    st.success(f"🎉 Welcome, {full_name.strip()}! Your account has been created successfully.")
                    close_modal()

    c1, c2, c3 = st.columns([1, 0.3, 1])
    with c2:
        st.markdown("<div class='cta-legend'>Already a user?</div>", unsafe_allow_html=True)
        if st.button("Login", type="primary", key="open_login"):
            open_modal("login")

# ===============================
# LOGIN MODAL
# ===============================
@st.dialog("Login", width="large")
def login_modal():
    st.markdown("<p class='lead'>Welcome back! Log in to continue reducing food waste.</p>", unsafe_allow_html=True)
    show = st.session_state.li_show_errors

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email Address", placeholder="you@example.com", key="login_email")
        if show:
            ok_email, email_err = validate_email(email)
            if not ok_email: st.markdown(f"<div class='field-error'>{email_err}</div>", unsafe_allow_html=True)

        pwd = st.text_input("Password", type="password", placeholder="••••••••", key="login_pwd")
        if show:
            ok_pwd, pwd_err = validate_password(pwd)
            if not ok_pwd: st.markdown(f"<div class='field-error'>{pwd_err}</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Login", type="primary")
        if submitted:
            st.session_state.li_show_errors = True
            ok_email, _ = validate_email(email)
            ok_pwd,   _ = validate_password(pwd)
            if ok_email and ok_pwd:
                ok, name = verify_user_record(email, pwd)
                if not ok:
                    st.error("Invalid email or password.")
                else:
                    st.session_state.is_authed = True
                    st.session_state.display_name = name
                    st.session_state.li_show_errors = False
                    st.success(f"✅ Welcome back, {name}!")
                    close_modal()

    d1, d2, d3 = st.columns([1, 0.3, 1])
    with d2:
        st.markdown("<div class='cta-legend'>New here?</div>", unsafe_allow_html=True)
        if st.button("Create Account", type="primary", key="back_signup"):
            open_modal("signup")

# ===============================
# RENDER ACTIVE MODAL
# ===============================
if st.session_state.modal == "signup":
    signup_modal()
elif st.session_state.modal == "login":
    login_modal()

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

# ===============================
# MANUAL INGREDIENT ENTRY (inside a section)
# ===============================
CATEGORIES = [
    "Vegetable", "Fruit", "Protein", "Dairy", "Grain",
    "Spice/Herb", "Canned", "Condiment", "Frozen", "Other"
]
UNITS = ["unit", "g", "kg", "ml", "l", "tsp", "tbsp", "cup", "oz", "lb"]

with st.expander("🧺 Add ingredients manually", expanded=False):
    st.markdown("<div class='manual-card'>", unsafe_allow_html=True)

    # --- header row (captions only) ---
    h1, h2, h3, h4, h5 = st.columns([5, 3, 1.2, 1.6, 2])
    with h1: st.caption("Ingredient")
    with h2: st.caption("Category")
    with h3: st.caption("Qty")
    with h4: st.caption("Unit")
    with h5: st.caption(" ")  # empty header over the button

    # --- inputs row (labels collapsed) ---
    c1, c2, c3, c4, c5 = st.columns([5, 3, 1.2, 1.6, 2])
    with c1:
        in_name = st.text_input("Ingredient", placeholder="e.g., eggs",
                                key="man_name", label_visibility="collapsed")
    with c2:
        in_cat = st.selectbox("Category", CATEGORIES,
                              index=CATEGORIES.index("Other"),
                              key="man_cat", label_visibility="collapsed")
    with c3:
        in_qty = st.number_input("Qty", min_value=0.0, step=1.0, value=1.0,
                                 key="man_qty", label_visibility="collapsed")
    with c4:
        in_unit = st.selectbox("Unit", UNITS,
                               index=UNITS.index("unit"),
                               key="man_unit", label_visibility="collapsed")
    with c5:
        add_clicked = st.button("Add Ingredient", type="primary",
                                key="man_add", use_container_width=True)

    # rest of your add handler + chips stays the same...
    if add_clicked:
        name = (in_name or "").strip()
        if not name:
            st.error("Please enter an ingredient name.")
        else:
            st.session_state.ingredients.append(
                {"name": name, "category": in_cat, "qty": in_qty, "unit": in_unit}
            )
            st.session_state.man_name = ""

    if st.session_state.ingredients:
        st.markdown("**In your fridge (manual):**")
        rem_cols = st.columns(4)
        for i, item in enumerate(st.session_state.ingredients):
            with rem_cols[i % 4]:
                st.markdown(
                    f"<span class='ingredient-chip'>{item['name']} "
                    f"<small>· {item['category']} · {item['qty']} {item['unit']}</small></span>",
                    unsafe_allow_html=True
                )
                if st.button("Remove", key=f"rm_{i}"):
                    st.session_state.ingredients.pop(i)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


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