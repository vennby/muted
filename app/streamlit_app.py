import streamlit as st
import re

# === Define your regex patterns ===
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'(\+?\d[\d\s\-]{7,}\d)')

# === Deterministic cleaning function ===
def deterministic_clean(text: str) -> str:
    """Applies pattern-based deterministic PII scrubbing."""
    text = EMAIL_REGEX.sub("<EMAIL_REDACTED>", text)
    text = PHONE_REGEX.sub("<PHONE_REDACTED>", text)
    return text

# === UI ===
st.markdown("<h1 style='text-align: center;'>Welcome to Muted! 🤫</h1>", unsafe_allow_html=True)

text = '''
Hello there! Muted is a tool that was developed to quickly and effectively remove PII from unstructured data. 
It was developed by [venn](https://github.com/vennby), under guidelines received from [mik](https://github.com/Mik1337), for [Unmute](https://unmute.now/)!
'''

st.markdown(text, unsafe_allow_html=True)
st.subheader("Test it out here~")

# Functional text area
user_input = st.text_area("Enter text with PII to be cleaned:", height=200, placeholder="Type your text here...")

# Clean button
if st.button("Clean Text"):
    if user_input.strip() == "":
        st.warning("Please enter some text first!")
    else:
        cleaned_text = deterministic_clean(user_input)
        st.success("Text cleaned successfully!")
        st.text_area("Cleaned Text:", value=cleaned_text, height=200)
