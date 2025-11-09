from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
AUDIO_DIR = DATA_DIR / "raw_audio"
TRANS_DIR = DATA_DIR / "transcriptions"
ANALYSIS_DIR = DATA_DIR / "analysis_results"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRANS_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# How many minutes per segment; we’ll use 60 for hourly runs
SEGMENT_MINUTES = int(os.getenv("SEGMENT_MINUTES", "60"))
