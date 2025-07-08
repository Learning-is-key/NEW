import streamlit as st
import fitz  # PyMuPDF
from db import init_db, register_user, login_user, save_upload, get_user_history
from openai import OpenAI

# 🔐 Your OpenAI API Key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- INIT DB ---
init_db()

# --- CONFIG ---
st.set_page_config(page_title="LegalEase 2.0", layout="centered", page_icon="📜")

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
        }
        .stButton>button {
            border-radius: 8px;
            background-color: #29465B;
            color: white;
            font-weight: 600;
        }
        .stTextInput>div>input, .stTextArea>div>textarea {
            border-radius: 6px;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>📜 LegalEase 2.0</h1>", unsafe_allow_html=True)
st.caption("Your personal AI legal document explainer — with login, upload history, and document simplification.")

# --- AUTH SECTIONS ---
def login_section():
    st.subheader("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success(f"✅ Welcome back, {email}!")
        else:
            st.error("❌ Invalid email or password.")

def signup_section():
    st.subheader("📝 Sign Up")
    email = st.text_input("New Email")
    password = st.text_input("New Password", type="password")
    if st.button("Create Account"):
        if register_user(email, password):
            st.success("🎉 Account created! You can now log in.")
        else:
            st.error("⚠️ User already exists.")

# --- MAIN APP SECTION ---
def app_main():
    with st.sidebar:
        st.image("https://img.icons8.com/ios/100/law.png", width=60)
        st.title("📚 LegalEase")
        choice = st.radio("Navigate", ["📤 Upload & Simplify", "📂 My History", "🚪 Logout"])

    if choice == "📤 Upload & Simplify":
        st.subheader("Upload Your Legal PDF")
        uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

        if uploaded_file:
            with st.spinner("📖 Reading your PDF..."):
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = "".join([page.get_text() for page in doc])
            st.success("✅ PDF uploaded and text extracted.")
            st.text_area("📄 Extracted Text", full_text, height=300)

            if st.button("🧠 Simplify Document"):
                with st.spinner("Using AI to simplify..."):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You're a legal document simplifier."},
                                {"role": "user", "content": full_text}
                            ]
                        )
                        simplified = response.choices[0].message.content
                        st.subheader("✅ Simplified Summary")
                        st.success(simplified)
                        save_upload(st.session_state.user_email, uploaded_file.name, simplified)
                    except Exception as e:
                        st.error(f"OpenAI Error: {str(e)}")

    elif choice == "📂 My History":
        st.subheader("Your Uploaded Files")
        history = get_user_history(st.session_state.user_email)
        if not history:
            st.info("ℹ️ No uploads yet.")
        else:
            for file, summary, time in history:
                with st.expander(f"📄 {file} | 🕒 {time}"):
                    st.text(summary)

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.success("✅ You have been logged out. Refresh to log in again.")

# --- ROUTING ---
if not st.session_state.logged_in:
    login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])
    with login_tab:
        login_section()
    with signup_tab:
        signup_section()
else:
    app_main()

# --- FOOTER ---
st.markdown("<hr><p style='text-align: center; color: gray;'>© 2025 LegalEase. Built with ❤️ using Streamlit.</p>", unsafe_allow_html=True)

