"""
Muted CLI — A simple command-line tool to redact PII (emails, phones, names, locations).

Usage:
    python muted.py input.json output.json

The input JSON must be a list of objects:
[
  { "id": 1,
    "text": "Some text containing PII"
},
  ...
]

The output will be written to the specified output file.
"""

import os
import re
import json
import argparse
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# ----------------------------------------------------
# ENV + CLIENT SETUP
# ----------------------------------------------------
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
if HF_API_KEY is None:
    raise ValueError("Please set HF_API_KEY in your environment variables!")

client = InferenceClient(provider="auto", api_key=HF_API_KEY)

# ----------------------------------------------------
# CONSTANTS & REGEX
# ----------------------------------------------------
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE_REGEX = re.compile(r'\+?\d[\d\s\-]{7,}\d')

EMAIL_TOKEN = "<EMAIL_REDACTED>"
PHONE_TOKEN = "<PHONE_REDACTED>"
GEN_TOKEN = "<REDACTED>"

CONTEXT_WORDS = [
    "my name is",
    "i am",
    "this is",
    "call me",
    "name is"
]


# ----------------------------------------------------
# UTILITIES
# ----------------------------------------------------
def collapse_repeated_redacted(text: str) -> str:
    """
    Collapse multiple consecutive <REDACTED> tokens into a single one.
    """
    return re.sub(r'(?:<REDACTED>){2,}', '<REDACTED>', text)


def get_regex_spans(text: str):
    """
    Find spans for emails and phone numbers using regex.
    Returns: list of {"start": int, "end": int, "replacement": str}
    """
    spans = []

    for m in EMAIL_REGEX.finditer(text):
        spans.append({"start": m.start(), "end": m.end(), "replacement": EMAIL_TOKEN})

    for m in PHONE_REGEX.finditer(text):
        spans.append({"start": m.start(), "end": m.end(), "replacement": PHONE_TOKEN})

    return spans


def normalize_for_ner(text: str) -> str:
    """
    Slight normalization for better NER detection.
    Must NOT change overall length of text.
    """
    if not text:
        return text

    t = text

    # Capitalize first character
    t = t[0].upper() + t[1:]

    # Capitalize probable names after contextual words
    for ctx in CONTEXT_WORDS:
        pattern = re.compile(rf"{ctx}\s+([a-z][a-z]+)", re.IGNORECASE)

        def repl(m):
            name = m.group(1)
            return f"{m.group(0)[:-len(name)]}{name.capitalize()}"

        t = pattern.sub(repl, t)

    return t


def get_ner_spans(text: str, model="dslim/bert-base-NER"):
    """
    Run NER using HuggingFace Inference API.
    Returns spans for PERSON/ORG/LOCATION entities.
    """
    if not text:
        return []

    normalized = normalize_for_ner(text)

    try:
        ner_results = client.token_classification(normalized, model=model)
    except Exception as e:
        print("⚠️  NER error:", e)
        return []

    spans = []
    for ent in ner_results:
        label = (ent.get("entity_group") or ent.get("label") or "").upper()
        start = ent.get("start")
        end = ent.get("end")

        if start is None or end is None:
            continue

        if label in {"PER", "PERSON", "LOC", "LOCATION", "ORG", "ORGANIZATION"}:
            spans.append({
                "start": start,
                "end": end,
                "replacement": GEN_TOKEN
            })

    return spans


def merge_spans(regex_spans, ner_spans):
    """
    Merge regex spans and NER spans into a single list of non-overlapping spans.
    Email/phone (regex) always overrides NER.
    """
    all_spans = regex_spans + ner_spans
    all_spans.sort(key=lambda s: (s["start"], -(s["end"] - s["start"])))

    merged = []

    for span in all_spans:
        if not merged:
            merged.append(span)
            continue

        last = merged[-1]

        # If there's no overlap, just append
        if span["start"] >= last["end"]:
            merged.append(span)
            continue

        # Regex wins over NER
        last_is_regex = last["replacement"] in {EMAIL_TOKEN, PHONE_TOKEN}
        curr_is_regex = span["replacement"] in {EMAIL_TOKEN, PHONE_TOKEN}

        if last_is_regex:
            continue

        if curr_is_regex:
            merged[-1] = span
            continue

        # Otherwise choose the one with the larger span
        if (span["end"] - span["start"]) > (last["end"] - last["start"]):
            merged[-1] = span

    return merged


def full_redact(text: str) -> str:
    """
    Full PII redaction pipeline:
    - Regex PII
    - NER-based PERSON / ORG / LOCATION
    - Merge spans
    - Replace text
    - Cleanup duplicates
    """
    if not text:
        return text

    regex_spans = get_regex_spans(text)
    ner_spans = get_ner_spans(text)
    spans = merge_spans(regex_spans, ner_spans)

    output = []
    idx = 0

    for sp in spans:
        if sp["start"] > idx:
            output.append(text[idx:sp["start"]])
        output.append(sp["replacement"])
        idx = sp["end"]

    if idx < len(text):
        output.append(text[idx:])

    result = "".join(output)
    return collapse_repeated_redacted(result)


def process_json(data):
    """
    Redact a list of JSON objects of the form:
    { "id": ..., "text": ... }
    """
    if not isinstance(data, list):
        raise ValueError("JSON root must be a list")

    cleaned = []
    for obj in data:
        if "text" not in obj:
            raise KeyError("Each JSON object must contain a 'text' field")

        cleaned.append({
            "id": obj.get("id"),
            "cleaned_text": full_redact(obj["text"])
        })

    return cleaned


# ----------------------------------------------------
# CLI ENTRYPOINT
# ----------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Muted CLI — PII Redaction Tool")
    parser.add_argument("input", help="Path to input JSON file")
    parser.add_argument("output", help="Path to output JSON file")

    args = parser.parse_args()

    # Load input data
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load input JSON: {e}")
        return

    print("🔍 Redacting PII... (this may take a few seconds)")

    try:
        cleaned = process_json(data)
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return

    # Write output file
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=4)
    except Exception as e:
        print(f"❌ Failed to write output JSON: {e}")
        return

    print(f"✅ Done! Cleaned output saved to: {args.output}")


if __name__ == "__main__":
    main()
