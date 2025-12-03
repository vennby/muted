import streamlit as lit
import json
from utils.logic import clean_json_batch

lit.set_page_config(page_title="Muted!", page_icon="🤫")

lit.markdown("<h1 style='text-align: center;'>Muted! 🤫</h1>", unsafe_allow_html=True)
lit.subheader("Batch JSON Cleaning")

uploaded_file = lit.file_uploader("Upload a JSON file", type=["json"])

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)

        lit.success("File uploaded successfully!")

        if lit.button("Clean JSON Batch"):
            cleaned = clean_json_batch(data)

            # Convert cleaned JSON to bytes for download
            cleaned_bytes = json.dumps(cleaned, indent=4).encode("utf-8")

            lit.download_button(
                label="Download Cleaned JSON",
                data=cleaned_bytes,
                file_name="cleaned_output.json",
                mime="application/json"
            )

    except Exception as e:
        lit.error(f"Invalid JSON file: {e}")