from pathlib import Path
import json
from backend.services.nlp_utils import extract_companies, sentiment_score
from backend.config import ANALYSIS_DIR

def analyze_transcript(transcript_path: Path) -> Path:
    """
    Extract stock mentions + sentiment score.
    """
    text = transcript_path.read_text(encoding="utf-8")

    companies = extract_companies(text)
    score = sentiment_score(text)

    analysis = {
        "file": transcript_path.name,
        "companies_detected": companies,
        "sentiment_score": score,
    }

    output_path = ANALYSIS_DIR / (transcript_path.stem + "_analysis.json")
    output_path.write_text(json.dumps(analysis, indent=2))
    return output_path
