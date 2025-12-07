<h1 align="center"> Muted! 🤫 </h1>

<p align="center"> A smart PII redactor built for anonymizing unstructured string data. </p>

<img src="https://31.media.tumblr.com/86f44ac600a1cb34f9651961ce9a2038/tumblr_mhto9sEwaK1raym3wo1_500.gif" width="2000">

## How to run?

Muted comes with both a **CLI version** and a **GUI version**!

#### CLI Version
Muted requires a Hugging Face API token. You can set it up in either of the following ways:

#### - Using an Environment Variable

```bash
export HF_API_KEY="your_hugging_face_api_key_here"
```

#### - Using a `.env` file

1. Create a `.env` file in the project root.
2. Add the following line in the file:

```bash
HF_API_KEY=your_hugging_face_api_key_here
```
### 1. Install the required dependencies.

```bash
pip install -r requirements.txt
```
### 2. Run the following command in your terminal.

```bash
python muted.py data.json clean.json
```

### GUI Version
You can locally host the tool's GUI in the following steps. I used to `streamlit` to quickly build the app; this is only for a quick demonstration, and is not a **scalable tech stack for production environments**.

Ensure you already have your `requirements.txt` installed.

### 1. Navigate to the `app` folder in the repo using the terminal.

```bash
cd app
```

### 2. Run the app.

```bash
streamlit run
```

Or, you can simply try the tool here: [Muted! 🤫](https://muted-now.streamlit.app)

## Why did I pick `bert-base-NER`?

`bert-base-NER` is a fine-tuned BERT model (trained by David S. Lim, Stanford) that is ready to use for Named Entity Recognition and achieves state-of-the-art performance for the NER task. It has been trained to recognize four types of entities: location (LOC), organizations (ORG), person (PER) and Miscellaneous (MISC).

Specifically, this model is a bert-base-cased model that was fine-tuned on the English version of the standard **CoNLL-2003 Named Entity Recognition** dataset.

## What are some limitations of the tool?

1. It is unable to completely redact personal information when they are not punctuated appropriately. For example, the tool will redact `Santosh` but not `santosh`.
2. It is struggles with identifying certain uncommon names and redacting them efficiently. For example, it will redact `Vennela` as `<REDACTED>la`. The issue of uncommon names extends to certain locations as well.

## How to potentially deal with the tool's limitations?

1. The fix I have used for inappropriate punctuations for now is normalizing the given string inputs. It is not completely eliminating such issues, but it solves at the very least a part of it. `dslim/bert-base-NER` works much better when sentences are capitalized, the same way as many pre-trained NERs, since they often expect capitalized names/normal sentence casing and thus miss out on identifying short, informal patterns, even though they might be very common.
2. The `ai4bharat/IndicNER` model should theoretically be able to identify Indian names and locations well. However, since it is an older model (last updated in 2022), it is not deployable via the HF Inference API. With a bit more time and effort, either this approach can be taken, or a different method or a better model can be tried.

## Sample JSON Inputs and Outputs
Here is an example of the input:
```json
[
  {
    "id": 1,
    "text": "Please contact Santosh at santosh@unmute.now regarding the meeting at Koramangala for further steps."
  },
  {
    "id": 2,
    "text": "Radhika said you can call her on +91-98765-43210 before sending the documents to her office in Banjara Hills."
  }
]
```
Here is an example of the generated output:
```json
[
    {
        "id": 1,
        "cleaned_text": "Please contact <REDACTED>h at <EMAIL_REDACTED> regarding the meeting at <REDACTED> for further steps."
    },
    {
        "id": 2,
        "cleaned_text": "<REDACTED> said you can call her on <PHONE_REDACTED> before sending the documents to her office in <REDACTED>."
    }
]
```
Please feel free to use the `input.json` file attached in this repo for your testing purposes!

#### PS: I have used `venv` for my virtual environment, since that is what I have been most comfortable with.