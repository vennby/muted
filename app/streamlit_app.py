import streamlit as lit

lit.set_page_config(
    page_title="About Muted",   # This name appears in browser tab + sidebar
    page_icon="🤫",
    layout="wide"
)

from PIL import Image
import io
import base64

img = Image.open("app/assets/logo.png")
buffered = io.BytesIO()
img.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

lit.markdown(f"""
<div style="text-align: center;">
    <img src="data:image/png;base64,{img_str}" width="200">
</div>
""", unsafe_allow_html=True)

lit.markdown("<h1 style='text-align: center;'>Welcome to Muted! 🤫</h1>", unsafe_allow_html=True)

display_text = '''
Hello there! Muted is a tool that was developed to quickly and effectively remove PII from unstructured data. It was developed by [venn](https://github.com/vennby), under guidelines received from [mik](https://github.com/Mik1337), for [Unmute](https://unmute.now/)!

### Why does Unmute used Muted?
Most workplace harassment in India goes unreported, and Unmute addresses this by collecting **anonymous**, self-reported experiences and analyzing them to uncover patterns across roles, sectors, and identities to identify gaps in the ecosystem.

One of Unmute's core values is compassion towards the victims, due to which all the data that is collected and used for analysis has to be scrubbed clean of Personally Identifiable Information (PII).

### How does Muted work?
Muted takes a layered approach to redacting PII from user data.

- Layer 1: Deterministic Cleaning
    - Using Regex
- Layer 2: Contextual Cleaning
    - Using LLMs
'''

lit.markdown(display_text, unsafe_allow_html=True)
