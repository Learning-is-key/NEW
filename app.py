import streamlit as st
from openai import OpenAI
import fitz  # PyMuPDF

# 🔑 Replace with your real OpenAI API key
client = OpenAI(api_key="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")

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
            prompt = (
                "You are a helpful assistant that explains legal documents in simple language. "
                "Read this and explain every important point like you would to a regular person:\n\n"
                + full_text
            )

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.6,
                    max_tokens=1500
                )
                result = response.choices[0].message.content
                st.subheader("✅ Simplified Explanation:")
                st.text_area("Easy-to-Understand Legal Summary", result, height=300)

            except Exception as e:
                st.error(f"Error: {e}")
