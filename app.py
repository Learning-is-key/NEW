import streamlit as st
import fitz  # PyMuPDF
from db import init_db, register_user, login_user, save_upload, get_user_history
from openai import OpenAI

# --- INIT DB ---
init_db()

# --- CONFIG ---
st.set_page_config(page_title="LegalEase 2.0", layout="centered", page_icon="📜")

# --- OPENAI CLIENT ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- STYLES ---
st.markdown("""
    <style>
        .reportview-container .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 800px;
        }
        .stButton>button {
            background-color: #29465B;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 8px 20px;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
        }
        .stTextArea>div>textarea {
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center; color: #29465B;'>📜 LegalEase 2.0</h1>", unsafe_allow_html=True)
st.caption("Your personal AI legal document explainer — with login, history, and summaries.")

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

# --- MAIN APP ---
def app_main():
    st.sidebar.title("📚 Navigation")
    choice = st.sidebar.radio("Go to", ["📤 Upload & Simplify", "📂 My History", "🔓 Logout"])

    if choice == "📤 Upload & Simplify":
        st.subheader("Upload Your Legal Document (PDF)")
        uploaded_file = st.file_uploader("Upload your legal PDF below", type=["pdf"])

        if uploaded_file:
            with st.spinner("Extracting text from PDF..."):
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = "".join(page.get_text() for page in doc)

            st.success("✅ Text extracted successfully.")
            st.text_area("📄 Extracted Text", full_text, height=300)

            if st.button("🧠 Simplify Document"):
                try:
                    with st.spinner("Simplifying with OpenAI..."):
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
                    st.error(f"OpenAI error: {str(e)}")

    elif choice == "📂 My History":
        st.subheader("Your Uploaded History")
        history = get_user_history(st.session_state.user_email)
        if not history:
            st.info("No uploads yet.")
        else:
            for file, summary, time in history:
                with st.expander(f"📄 {file} | 🕒 {time}"):
                    st.text(summary)

    elif choice == "🔓 Logout":
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.success("Logged out. Refresh to login again.")

# --- ROUTING ---
if not st.session_state.logged_in:
    tab = st.tabs(["Login", "Sign Up"])
    with tab[0]:
        login_section()
    with tab[1]:
        signup_section()
else:
    app_main()

# --- FOOTER ---
st.markdown("<hr><p style='text-align: center; color: gray;'>© 2025 LegalEase. Built with ❤️ in Streamlit.</p>", unsafe_allow_html=True)
