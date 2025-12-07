import os
import re
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
if HF_API_KEY is None:
    raise ValueError("Please set HF_API_KEY in your environment variables!")

client = InferenceClient(provider="auto", api_key=HF_API_KEY)

# ----------------------------------------------------
# REGEX PATTERNS
# ----------------------------------------------------
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE_REGEX = re.compile(r'\+?\d[\d\s\-]{7,}\d')

EMAIL_TOKEN = "<EMAIL_REDACTED>"
PHONE_TOKEN = "<PHONE_REDACTED>"
GEN_TOKEN = "<REDACTED>"
CONTEXT_WORDS = ["my name is", "i am", "this is", "call me", "name is"]


# ----------------------------------------------------
# COLLAPSE DUPLICATE <REDACTED> TOKENS
# ----------------------------------------------------
def collapse_repeated_redacted(text: str) -> str:
    return re.sub(r'(?:<REDACTED>){2,}', '<REDACTED>', text)


# ----------------------------------------------------
# REGEX SPANS
# ----------------------------------------------------
def get_regex_spans(text):
    spans = []

    for m in EMAIL_REGEX.finditer(text):
        spans.append({"start": m.start(), "end": m.end(), "replacement": EMAIL_TOKEN})

    for m in PHONE_REGEX.finditer(text):
        spans.append({"start": m.start(), "end": m.end(), "replacement": PHONE_TOKEN})

    return spans


# ----------------------------------------------------
# NORMALIZATION FOR NER ONLY
# ----------------------------------------------------
def normalize_for_ner(text: str) -> str:
    t = text

    if not t:
        return t

    # Capitalize first char
    t = t[0].upper() + t[1:]

    # Capitalize names after contextual words
    for ctx in CONTEXT_WORDS:
        pattern = re.compile(rf"{ctx}\s+([a-z][a-z]+)", re.IGNORECASE)

        def repl(m):
            name = m.group(1)
            return f"{m.group(0)[:-len(name)]}{name.capitalize()}"

        t = pattern.sub(repl, t)

    return t


# ----------------------------------------------------
# NER SPANS
# ----------------------------------------------------
def get_ner_spans(text, model="dslim/bert-base-NER"):
    if not text:
        return []

    normalized = normalize_for_ner(text)

    try:
        ner_results = client.token_classification(normalized, model=model)
    except Exception as e:
        print("NER error:", e)
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


# ----------------------------------------------------
# MERGE SPANS
# ----------------------------------------------------
def merge_spans(regex_spans, ner_spans):
    all_spans = regex_spans + ner_spans
    all_spans.sort(key=lambda s: (s["start"], - (s["end"] - s["start"])))

    merged = []

    for span in all_spans:
        if not merged:
            merged.append(span)
            continue

        last = merged[-1]

        if span["start"] >= last["end"]:
            merged.append(span)
            continue

        # regex overrides NER
        last_is_regex = last["replacement"] in {EMAIL_TOKEN, PHONE_TOKEN}
        curr_is_regex = span["replacement"] in {EMAIL_TOKEN, PHONE_TOKEN}

        if last_is_regex:
            continue

        if curr_is_regex:
            merged[-1] = span
        else:
            if span["end"] - span["start"] > last["end"] - last["start"]:
                merged[-1] = span

    return merged


# ----------------------------------------------------
# FULL REDACTION PIPELINE
# ----------------------------------------------------
def full_redact(text: str) -> str:
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

    # 🔥 FIX APPLIED HERE
    result = collapse_repeated_redacted(result)

    return result


# ----------------------------------------------------
# CLEAN JSON LIST
# ----------------------------------------------------
def clean_json_file(data):
    if not isinstance(data, list):
        raise ValueError("Uploaded JSON must be a list of objects")

    cleaned = []

    for obj in data:
        if "text" not in obj:
            raise KeyError("Each JSON object must contain a `text` field")

        redacted = full_redact(obj["text"])

        cleaned.append({
            "id": obj.get("id"),
            "cleaned_text": redacted
        })

    return cleaned

