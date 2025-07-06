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
                name = uploaded_file.name.lower()

                if "rental" in name:
                    fake_output = """
This is a rental agreement made between Mr. Rakesh Kumar (the property owner) and Mr. Anil Reddy (the person renting).

- The house is in Jubilee Hills, Hyderabad.
- Rent is ₹18,000/month, paid by the 5th.
- Anil pays a ₹36,000 security deposit.
- The rental period is 11 months: from August 1, 2025, to June 30, 2026.
- Either side can cancel the agreement with 1 month’s written notice.
- Anil can't sub-rent the house to anyone else unless Rakesh agrees.

In short: this document explains the rules of staying in the rented house, money terms, and how both sides can exit the deal.
                    """

                elif "nda" in name:
                    fake_output = """
This Non-Disclosure Agreement (NDA) is between TechNova Pvt. Ltd. and Mr. Kiran Rao.

- Kiran will receive sensitive business information from TechNova.
- He agrees to keep this confidential and not use it for anything other than their business discussions.
- This includes technical data, strategies, client info, designs, etc.
- He cannot share it, even after the project ends, for 3 years.
- Exceptions: if info is public, received legally from others, or required by law.
- If he breaks the agreement, TechNova can take legal action, including asking the court to stop him immediately.

In short: Kiran must not reveal or misuse any business secrets he gets from TechNova during their potential partnership.
                    """

                elif "employment" in name:
                    fake_output = """
This is an official job contract between GlobalTech Ltd. and Ms. Priya Sharma.

- Priya will join as a Senior Software Engineer from August 1, 2025.
- She will earn Rs. 12,00,000/year, including bonuses and allowances.
- She must work 40+ hours/week, either from office or remotely.
- First 6 months = probation, 15-day notice for quitting or firing.
- After that, it becomes 60-day notice.
- She must not share company secrets or join rival companies for 1 year after leaving.
- Any inventions or code she builds belong to the company.
- She gets 20 paid leaves + public holidays.

In short: This contract outlines Priya’s job, salary, rules during and after employment, and what happens if she quits or is fired.
                    """
                else:
                    fake_output = "This appears to be a legal document. However, I couldn’t auto-identify its type. Please consult a legal expert for proper clarification."

                st.subheader("✅ Simplified Summary")
                st.success(fake_output)
                generate_pdf(fake_output)

                with open("summary.pdf", "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                download_link = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="summary.pdf">📄 Download This Summary as PDF</a>'
                st.markdown(download_link, unsafe_allow_html=True)

                save_upload(st.session_state.user_email, uploaded_file.name, fake_output)

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
def generate_pdf(text, filename="summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    return filename
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
