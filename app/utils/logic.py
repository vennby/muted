import re
import json

# === Define your regex patterns ===
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'(\+?\d[\d\s\-]{7,}\d)')

# === Deterministic cleaning function ===
def deterministic_clean(text: str) -> str:
    """Applies pattern-based deterministic PII scrubbing."""
    text = EMAIL_REGEX.sub("<EMAIL_REDACTED>", text)
    text = PHONE_REGEX.sub("<PHONE_REDACTED>", text)
    return text

# ======================================================
# ✅ Updated Batch Cleaner (matches EXACT output format)
# ======================================================
def clean_json_batch(data, text_key="text", save_to=None):
    """
    Cleans PII from a list of JSON objects and outputs:
    { "id": <id>, "cleaned_text": <cleaned> }
    """

    # Case: File path
    if isinstance(data, str):
        with open(data, "r", encoding="utf-8") as f:
            data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Input must be a list of objects or a JSON file path.")

    cleaned_data = []

    for item in data:
        if text_key not in item:
            raise KeyError(f"Key '{text_key}' not found in JSON item: {item}")

        cleaned_text = deterministic_clean(item[text_key])

        cleaned_item = {
            "id": item.get("id"),
            "cleaned_text": cleaned_text
        }

        cleaned_data.append(cleaned_item)

    # Save output
    if save_to:
        with open(save_to, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, indent=4)

    return cleaned_data