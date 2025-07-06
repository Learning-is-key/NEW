import streamlit as st
import fitz  # PyMuPDF
from db import init_db, register_user, login_user, save_upload, get_user_history

# --- INIT DB ---
init_db()

# --- CONFIG ---
st.set_page_config(page_title="LegalEase 2.0", layout="centered", page_icon="📜")

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center;'>📜 LegalEase 2.0</h1>", unsafe_allow_html=True)
st.caption("Your personal AI legal document explainer — now with login and history.")

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
                # Fake GPT output based on filename
                name = uploaded_file.name.lower()
                if "rental" in name:
                    summary = "- This is a rental agreement...\n- Monthly rent: ₹18,000\n- Duration: 11 months\n- 1-month notice required."
                elif "nda" in name:
                    summary = "- This NDA restricts sharing confidential info\n- Valid for 3 years\n- Legal action if broken."
                elif "employment" in name:
                    summary = "- This is an employment offer\n- ₹12 LPA salary\n- 6-month probation\n- No competing jobs for 1 year."
                else:
                    summary = "- Document read but not recognized. Please rename file to include 'rental', 'nda', or 'employment'."

                st.subheader("✅ Simplified Summary")
                st.success(summary)
                save_upload(st.session_state.user_email, uploaded_file.name, summary)

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
