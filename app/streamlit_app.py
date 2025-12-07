import json
import streamlit as lit
from utils.logic import full_redact, clean_json_file

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
lit.set_page_config(page_title="Muted!", page_icon="🤫")

# ----------------------------------------------------
# HEADER
# ----------------------------------------------------
lit.markdown(
    "<h1 style='text-align: center; margin-bottom: 0;'>Muted! 🤫</h1>",
    unsafe_allow_html=True
)

lit.markdown(
    """
Hello there! **Muted** is a tool built to effectively remove PII from unstructured data.  
It was developed by [venn](https://github.com/vennby) under guidance from [mik](https://github.com/Mik1337), for **[Unmute](https://unmute.now/)**!

---

### Why does Unmute use Muted?

Workplace harassment in India often goes unreported. Unmute tackles this by collecting **anonymous**, self-reported experiences and analyzing them to uncover patterns across roles, sectors, and identities.

One of Unmute's core values is **compassion for victims**, which is why all collected data  
must be completely stripped of Personally Identifiable Information (PII) before analysis.
    """,
    unsafe_allow_html=True
)

lit.markdown("---")

# ----------------------------------------------------
# INPUT MODE SELECTION
# ----------------------------------------------------
lit.subheader("Test it out here!")
mode = lit.radio("Choose input type:", ["Text", "JSON File"], horizontal=True)

# ----------------------------------------------------
# TEXT MODE
# ----------------------------------------------------
if mode == "Text":
    user_input = lit.text_area(
        "Enter text with PII:",
        height=200,
        placeholder="Type your text here..."
    )

    if lit.button("Clean Text"):
        if not user_input.strip():
            lit.warning("Please enter some text.")
        else:
            cleaned_text = full_redact(user_input)
            lit.success("Cleaned successfully!")
            lit.text_area("Cleaned Text:", cleaned_text, height=200)

# ----------------------------------------------------
# JSON MODE
# ----------------------------------------------------
else:
    uploaded_file = lit.file_uploader("Upload JSON list", type=["json"])

    if uploaded_file:
        try:
            raw_data = json.load(uploaded_file)
        except Exception:
            lit.error("Invalid JSON file.")
            raw_data = None

        if raw_data and lit.button("Clean JSON File"):
            try:
                cleaned_data = clean_json_file(raw_data)

                lit.success("Cleaned JSON:")
                lit.json(cleaned_data)

                lit.download_button(
                    label="Download cleaned_output.json",
                    data=json.dumps(cleaned_data, indent=4),
                    file_name="cleaned_output.json",
                    mime="application/json"
                )

            except Exception as e:
                lit.error(f"Error during cleaning: {str(e)}")
