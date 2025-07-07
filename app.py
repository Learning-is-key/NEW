import streamlit as st
import fitz  # PyMuPDF
from db import init_db, register_user, login_user, save_upload, get_user_history
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # Make sure to set this in .streamlit/secrets.toml
init_db()

st.set_page_config(page_title="LegalEase 2.0", layout="wide", page_icon="📜")

# --- GLOBAL STYLES ---
st.markdown("""
    <style>
    .big-font { font-size: 28px !important; font-weight: bold; }
    .section-title { font-size: 22px !important; margin-top: 30px; }
    .small-text { font-size: 14px; color: gray; }
    .center { text-align: center; }
    .highlight { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    .sidebar-title { font-size: 18px !important; font-weight: bold; padding-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- HEADER ---
st.markdown("<h1 class='center'>📜 LegalEase 2.0</h1>", unsafe_allow_html=True)
st.caption("⚖️ Simplify legal jargon with AI | Secure, fast, and built just for you.")

# --- LOGIN / SIGNUP ---
def login_section():
    st.markdown("<div class='section-title'>🔐 Login</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        email = st.text_input("Email", key="login_email")
    with col2:
        password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login", use_container_width=True):
        user = login_user(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success(f"Welcome back, {email}!")
        else:
            st.error("Invalid credentials. Please try again.")

def signup_section():
    st.markdown("<div class='section-title'>📝 Sign Up</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        email = st.text_input("New Email", key="signup_email")
    with col2:
        password = st.text_input("New Password", type="password", key="signup_pass")
    if st.button("Sign Up", use_container_width=True):
        if register_user(email, password):
            st.success("Account created! You can now login.")
        else:
            st.error("User already exists. Try logging in.")

# --- MAIN APP ---
def app_main():
    st.sidebar.markdown("<div class='sidebar-title'>📚 Navigation</div>", unsafe_allow_html=True)
    choice = st.sidebar.radio("Go to", ["📤 Upload & Simplify", "📂 My History", "🚪 Logout"])

    if choice == "📤 Upload & Simplify":
        st.markdown("<div class='section-title'>📤 Upload Your Legal Document (PDF)</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Select a legal PDF", type=["pdf"])

        if uploaded_file:
            with st.spinner("Reading PDF..."):
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = "".join(page.get_text() for page in doc)

            st.success("✅ PDF uploaded and text extracted.")
            st.text_area("📄 Extracted Text", full_text, height=300)

            if st.button("🧠 Simplify Document", use_container_width=True):
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
        st.markdown("<div class='section-title'>📂 Your Uploaded History</div>", unsafe_allow_html=True)
        history = get_user_history(st.session_state.user_email)
        if not history:
            st.info("No uploads yet.")
        else:
            for file, summary, time in history:
                with st.expander(f"📄 {file} | 🕒 {time}"):
                    st.text_area("Summary", summary, height=200)

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.success("Logged out. Refresh the page to login again.")

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
st.markdown("<hr><p class='center small-text'>© 2025 LegalEase. Built with ❤️ using Streamlit.</p>", unsafe_allow_html=True)
