from pathlib import Path
import whisper
from backend.config import TRANS_DIR

# Load a small model first; switch to "medium" later if you want higher accuracy
_model = whisper.load_model("small")  # Apple Silicon supports MPS acceleration

def transcribe_to_english(audio_path: Path) -> Path:
    """
    Transcribes audio and translates to English automatically.
    """
    result = _model.transcribe(str(audio_path), task="translate")
    text = result.get("text", "").strip()
    out_path = TRANS_DIR / (audio_path.stem + ".txt")
    out_path.write_text(text, encoding="utf-8")
    return out_path
