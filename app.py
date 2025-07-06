import streamlit as st
import fitz  # PyMuPDF

# Page config
st.set_page_config(page_title="LegalEase - AI Legal Doc Explainer", page_icon="📜", layout="centered")

# Header section
st.markdown("""
    <div style='text-align: center; padding-bottom: 1rem;'>
        <h1 style='font-size: 2.8rem;'>📜 LegalEase</h1>
        <p style='font-size: 1.1rem; color: gray;'>Your smart AI assistant for simplifying legal documents</p>
    </div>
""", unsafe_allow_html=True)

# Instruction box
with st.expander("📌 How it works (click to expand)", expanded=True):
    st.markdown("""
    - Upload a legal PDF like a **rental agreement**, **job contract**, or **NDA**.
    - The app will "analyze" and give you a simple English explanation.
    - If you're using the free version, it shows fake GPT-style outputs.
    """)

# File uploader
st.markdown("### 📤 Upload Your Legal PDF")
uploaded_file = st.file_uploader("Supported formats: PDF", type=["pdf"])

# Text extraction + fake GPT logic
if uploaded_file:
    with st.spinner("📚 Reading your document..."):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()

    st.success("✅ PDF uploaded and text extracted!")
    st.markdown("### 🧾 Extracted Text")
    st.text_area("Raw Legal Content", full_text, height=250)

    if st.button("🧠 Simplify This"):
        with st.spinner("Thinking like a legal assistant..."):
            filename = uploaded_file.name.lower()
            if "rental" in filename:
                fake_output = """
- This is a rental agreement between a landlord and tenant.
- Rent is ₹18,000/month with ₹36,000 as deposit.
- The agreement lasts for 11 months.
- Subletting is not allowed.
- Either party must give 1-month notice to terminate.
                """
            elif "nda" in filename:
                fake_output = """
- This NDA is between TechNova and Kiran.
- Kiran agrees to keep company info confidential.
- It covers client info, designs, strategies, and data.
- The NDA lasts 3 years, even after the project ends.
- Breaking it can lead to legal action.
                """
            elif "employment" in filename:
                fake_output = """
- This is an offer letter for Priya as a Senior Software Engineer.
- Salary: ₹12,00,000/year.
- 6-month probation with 15-day notice period.
- Full-time, 40+ hours/week, remote or hybrid.
- Cannot join competitor after leaving for 1 year.
                """
            else:
                fake_output = "Sorry, this type of document isn’t recognized. Try naming your PDF as `rental`, `nda`, or `employment`."

        st.markdown("### ✅ Simplified Summary")
        st.success(fake_output.strip())

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© 2025 LegalEase by [Your Name]. For educational use only.</p>", unsafe_allow_html=True)
