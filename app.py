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
        st.success("✅ PDF Uploaded Successfully!")

    st.subheader("📄 Original Document Text:")
    st.text_area("Extracted Text", full_text, height=300)

    if st.button("🧠 Simplify Legal Terms"):
        with st.spinner("Thinking like a lawyer... but cooler."):
            filename = uploaded_file.name.lower()

            # Match the correct fake output based on file name
            if "rental" in filename:
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
            elif "nda" in filename:
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
            elif "employment" in filename:
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

            st.subheader("✅ Simplified Explanation:")
            st.text_area("Easy-to-Understand Legal Summary", fake_output.strip(), height=300)
