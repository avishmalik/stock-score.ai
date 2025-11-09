import json
from datetime import datetime
from pathlib import Path
from loguru import logger

from backend.workers.downloader import download_last_hour_audio
from backend.workers.transcriber import transcribe_to_english
from backend.workers.analyzer import analyze_transcript

ROOT = Path(__file__).resolve().parents[2]
STREAMS_FILE = ROOT / "streams_today.json"

from typing import Optional

def run_hourly_batch(end_time: Optional[datetime] = None):
    """
    1) Load today's curated URLs
    2) For each: download last hour, transcribe->English, analyze (stub)
    """
    end_time = end_time or datetime.now()
    if not STREAMS_FILE.exists():
        logger.error(f"No streams_today.json found at {STREAMS_FILE}")
        return

    streams = json.loads(STREAMS_FILE.read_text())
    for i, s in enumerate(streams, start=1):
        url = s["url"]
        name = s.get("name") or f"stream_{i}"
        logger.info(f"[{name}] Downloading last-hour audio…")
        audio = download_last_hour_audio(url, name, end_time=end_time)

        logger.info(f"[{name}] Transcribing…")
        transcript = transcribe_to_english(audio)

        logger.info(f"[{name}] Analyzing (stub)…")
        analysis = analyze_transcript(transcript)

        logger.success(f"[{name}] Done → {analysis}")
