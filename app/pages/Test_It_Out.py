import streamlit as lit
import re

from utils.logic import deterministic_clean

lit.set_page_config(page_title="Muted!", page_icon="🤫")

# === UI ===
lit.markdown("<h1 style='text-align: center;'>Muted! 🤫</h1>", unsafe_allow_html=True)

lit.subheader("Test it out here~")

# Functional text area
user_input = lit.text_area("Enter text with PII to be cleaned:", height=200, placeholder="Type your text here...")

# Clean button
if lit.button("Clean Text"):
    if user_input.strip() == "":
        lit.warning("Please enter some text first!")
    else:
        cleaned_text = deterministic_clean(user_input)
        lit.success("Text cleaned successfully!")
        lit.text_area("Cleaned Text:", value=cleaned_text, height=200)
