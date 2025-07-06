import streamlit as st
import fitz  # PyMuPDF

st.set_page_config(page_title="LegalEase - Simplify Legal Documents", layout="centered")

st.title("🧾 LegalEase")
st.caption("Understand complex legal documents in plain language – powered by AI.")

uploaded_file = st.file_uploader("📤 Upload your legal PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("📚 Reading the PDF..."):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        st.success("PDF Uploaded Successfully!")

    st.subheader("📄 Original Document Text:")
    st.text_area("Extracted Text", full_text, height=300)

    if st.button("🧠 Simplify Legal Terms"):
        with st.spinner("Thinking like a lawyer... but cooler."):
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
            st.subheader("✅ Simplified Explanation:")
            st.text_area("Easy-to-Understand Legal Summary", fake_output, height=300)
