import re
import streamlit as st
from PIL import Image
import google.generativeai as genai
from user_store import init_db, create_user_record, verify_user_record

init_db()

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Eco Chef AI", page_icon="👨‍🍳", layout="wide")

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
