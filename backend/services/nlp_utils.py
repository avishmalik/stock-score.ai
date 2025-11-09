import spacy

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# Load sentiment model (HuggingFace)

from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

model_name = "distilbert-base-uncased-finetuned-sst-2-english"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, use_safetensors=True)

sentiment_model = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer
)

# Stock/company mapping for India (extend this list manually as needed)
COMPANY_TO_TICKER = {
    "RELIANCE": "RELIANCE.NS",
    "TATA MOTORS": "TATAMOTORS.NS",
    "TCS": "TCS.NS",
    "INFOSYS": "INFY.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "AXIS BANK": "AXISBANK.NS",
    "HINDUSTAN UNILEVER": "HINDUNILVR.NS",
    "ICICI BANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "ITC": "ITC.NS",
}

def extract_companies(text: str):
    """
    Uses spaCy NER to detect ORG/company names from transcript.
    """
    doc = nlp(text)
    entities = [ent.text.upper() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT"]]

    matched = {}
    for ent in entities:
        for known_company in COMPANY_TO_TICKER:
            if known_company in ent:
                matched[ent] = COMPANY_TO_TICKER[known_company]

    return matched

def sentiment_score(text: str):
    """
    Sentiment → score between -1 to +1
    """
    result = sentiment_model(text[:500])  # analyze first 500 chars
    label = result[0]["label"]

    return {
        "NEGATIVE": -1,
        "NEUTRAL": 0,
        "POSITIVE": +1
    }.get(label.upper(), 0)
