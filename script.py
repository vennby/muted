import json
import re
from pathlib import Path

# -----------------------------
# Regex Patterns
# -----------------------------

EMAIL_REGEX = re.compile(
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
)

PHONE_REGEX = re.compile(
    r"(\+?\d[\d\s\-]{7,}\d)"
)

ADDRESS_REGEX = re.compile(
    r"\b(?:road|street|st|rd|nagar|layout|hills|block|colony|avenue|district)\b.*",
    re.IGNORECASE
)

# -----------------------------
# Deterministic Cleaning
# -----------------------------

def deterministic_clean(text: str) -> str:
    """Applies pattern-based deterministic PII scrubbing."""
    
    text = EMAIL_REGEX.sub("<EMAIL_REDACTED>", text)
    text = PHONE_REGEX.sub("<PHONE_REDACTED>", text)
    text = ADDRESS_REGEX.sub("<ADDRESS_REDACTED>", text)

    return text


# -----------------------------
# JSON Ingestion + Cleaning
# -----------------------------

def clean_json(input_path: str, output_path: str):
    """
    Loads raw JSON, applies deterministic PII cleaning,
    and writes cleaned JSON to output_path.
    """

    # Load JSON file
    raw_data = json.loads(Path(input_path).read_text())

    cleaned_data = []
    for row in raw_data:
        text = row.get("text", "")
        cleaned_text = deterministic_clean(text)

        cleaned_data.append({
            "id": row.get("id"),
            "cleaned_text": cleaned_text
        })

    # Save cleaned output
    Path(output_path).write_text(json.dumps(cleaned_data, indent=2))
    print(f"Cleaned JSON saved to: {output_path}")


# -----------------------------
# Example Usage
# -----------------------------

if __name__ == "__main__":
    clean_json("data.json", "cleaned_data.json")
