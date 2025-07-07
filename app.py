import streamlit as st
import fitz  # PyMuPDF
import requests
from db import init_db, register_user, login_user, save_upload, get_user_history

# Load Hugging Face token
hf_token = st.secrets["HF_TOKEN"]

# --- INIT DB ---
init_db()

# --- CONFIG ---
st.set_page_config(page_title="LegalEase 2.0", layout="centered", page_icon="📜")

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "mode" not in st.session_state:
    st.session_state.mode = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "mode_chosen" not in st.session_state:
    st.session_state.mode_chosen = False

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center;'>📜 LegalEase 2.0</h1>", unsafe_allow_html=True)
st.caption("Your personal AI legal document explainer — with login, history, and dual modes.")

# --- AUTH ---
def login_section():
    st.subheader("🔐 Login to Your Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success(f"Welcome back, {email}!")
        else:
            st.error("Invalid email or password.")

def signup_section():
    st.subheader("📝 Create an Account")
    email = st.text_input("New Email")
    password = st.text_input("New Password", type="password")
    if st.button("Sign Up"):
        if register_user(email, password):
            st.success("Account created! You can now login.")
        else:
            st.error("User already exists.")

# --- MODE SELECTOR ---
def choose_mode():
    st.subheader("Choose how you'd like to use LegalEase:")
    mode = st.radio("Select Mode", ["Demo Mode (no real AI)", "Use Your Own OpenAI API Key", "Use Open-Source AI via Hugging Face"])

    if mode == "Use Your Own OpenAI API Key":
        api_key = st.text_input("Paste your OpenAI API Key", type="password")
    else:
        api_key = ""

    if st.button("Continue"):
        if mode == "Use Your Own OpenAI API Key" and not api_key:
            st.warning("Please enter your API key to continue.")
        else:
            st.session_state.mode = mode
            st.session_state.api_key = api_key
            st.session_state.mode_chosen = True

# --- HUGGING FACE API WRAPPER ---
@st.cache_data
@st.cache_data
def query_huggingface_api(prompt):
    API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
    headers = {"Authorization": f"Bearer {hf_token}"}

    try:
        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200},
            "options": {"wait_for_model": True}
        })

        if response.status_code != 200:
            return f"❌ API Error {response.status_code}: {response.text}"

        output = response.json()

        if isinstance(output, list) and len(output) > 0:
            return output[0].get("generated_text", str(output[0]))
        else:
            return f"⚠️ Unexpected output: {output}"

    except Exception as e:
        return f"❌ Exception: {str(e)}"


# --- MAIN APP ---
def app_main():
    st.sidebar.title("📚 Navigation")
    choice = st.sidebar.radio("Go to", ["Upload & Simplify", "My History", "Logout"])

    if choice == "Upload & Simplify":
        st.subheader("📤 Upload Your Legal Document (PDF)")
        uploaded_file = st.file_uploader("Select a legal PDF", type=["pdf"])

        if uploaded_file:
            with st.spinner("Reading PDF..."):
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = ""
                for page in doc:
                    full_text += page.get_text()

            st.success("✅ PDF uploaded and text extracted.")
            st.text_area("📄 Extracted Text", full_text, height=300)

            if st.button("🧠 Simplify Document"):
                name = uploaded_file.name.lower()

                if st.session_state.mode == "Use Your Own OpenAI API Key":
                    try:
                        from openai import OpenAI
                        from openai.error import RateLimitError
                        client = OpenAI(api_key=st.session_state.api_key)
                        with st.spinner("Simplifying with OpenAI..."):
                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You're a legal document simplifier."},
                                    {"role": "user", "content": full_text}
                                ]
                            )
                            simplified = response.choices[0].message.content
                    except Exception as e:
                        st.error(f"OpenAI error: {str(e)}")
                        return

                elif st.session_state.mode == "Use Open-Source AI via Hugging Face":
                    prompt = f"""You are a legal assistant. Simplify the following legal document in plain English:

{full_text}

Simplified version:"""
                    with st.spinner("Simplifying using Hugging Face Inference API..."):
                        simplified = query_huggingface_api(prompt)

                else:
                    if "rental" in name:
                        simplified = "Demo summary for rental agreement."
                    elif "nda" in name:
                        simplified = "Demo summary for NDA document."
                    elif "employment" in name:
                        simplified = "Demo summary for employment contract."
                    else:
                        simplified = "Sample summary: Could not identify document type."

                st.subheader("✅ Simplified Summary")
                st.success(simplified)
                save_upload(st.session_state.user_email, uploaded_file.name, simplified)

    elif choice == "My History":
        st.subheader("📂 Your Uploaded History")
        history = get_user_history(st.session_state.user_email)
        if not history:
            st.info("No uploads yet.")
        else:
            for file, summary, time in history:
                with st.expander(f"📄 {file} | 🕒 {time}"):
                    st.text(summary)

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.mode = ""
        st.session_state.api_key = ""
        st.session_state.mode_chosen = False
        st.success("Logged out. Refresh to login again.")

# --- ROUTING ---
if not st.session_state.logged_in:
    tab = st.tabs(["Login", "Sign Up"])
    with tab[0]:
        login_section()
    with tab[1]:
        signup_section()
else:
    if not st.session_state.mode_chosen:
        choose_mode()
    else:
        app_main()

# --- FOOTER ---
st.markdown("<hr><p style='text-align: center; color: gray;'>© 2025 LegalEase. Built with ❤️ in Streamlit.</p>", unsafe_allow_html=True)
