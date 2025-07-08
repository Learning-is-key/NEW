import streamlit as st
import fitz  # PyMuPDF
from db import init_db, register_user, login_user, save_upload, get_user_history
from openai import OpenAI

# 🔐 API Key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- INIT DB ---
init_db()

# --- PAGE CONFIG ---
st.set_page_config(page_title="LegalLite", layout="centered", page_icon="⚖️")

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- GLOBAL STYLING ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
        }
        .stTextInput>div>input, .stTextArea>div>textarea {
            border-radius: 6px;
            border: 1px solid #ccc;
        }
        .stButton>button {
            background-color: #29465B;
            color: white;
            font-weight: 600;
            border-radius: 6px;
            padding: 0.5em 1.5em;
        }
        .summary-box {
            background-color: #f7f9fb;
            border: 1px solid #e1e1e1;
            border-radius: 8px;
            padding: 1rem;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>⚖️ LegalLite</h1>", unsafe_allow_html=True)
st.caption("Your AI legal document explainer — with login, upload history, and document simplification.")

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
            st.success(f"Welcome back, {email}!")
        else:
            st.error("Invalid email or password.")

def signup_section():
    st.subheader("📝 Sign Up")
    email = st.text_input("New Email")
    password = st.text_input("New Password", type="password")
    if st.button("Create Account"):
        if register_user(email, password):
            st.success("🎉 Account created! You can now log in.")
        else:
            st.error("User already exists.")

# --- MAIN APP ---
if st.button("🧠 Simplify Document"):
    with st.spinner("Processing with AI..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You're a legal document simplifier."},
                    {"role": "user", "content": full_text}
                ]
            )
            simplified = response.choices[0].message.content
            save_upload(st.session_state.user_email, uploaded_file.name, simplified)

            st.subheader("✅ Simplified Summary")
            st.markdown(f"<div class='summary-box'>{simplified}</div>", unsafe_allow_html=True)

            # 📥 Download button for summary
            st.download_button(
                label="📥 Download Summary as TXT",
                data=simplified,
                file_name=f"{uploaded_file.name}_summary.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"OpenAI error: {str(e)}")

    elif choice == "📂 History":
        st.subheader("📂 Your Upload History")
        history = get_user_history(st.session_state.user_email)
        if not history:
            st.info("No previous uploads found.")
        else:
            for file, summary, time in history:
                with st.expander(f"📄 {file} | 🕒 {time}"):
                    st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.success("✅ Logged out. Refresh to login again.")

# --- ROUTING ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    with tab1:
        login_section()
    with tab2:
        signup_section()
else:
    app_main()

# --- FOOTER ---
st.markdown("<hr><p style='text-align: center; color: gray;'>© 2025 LegalLite. Built with ❤️ using Streamlit.</p>", unsafe_allow_html=True)
