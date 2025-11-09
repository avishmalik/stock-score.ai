import subprocess, shlex
from datetime import datetime, timedelta
from pathlib import Path
from backend.config import AUDIO_DIR, SEGMENT_MINUTES

def ts() -> str:
    return datetime.now().strftime("%Y%m%dT%H%M%S")

from typing import Optional

def download_last_hour_audio(url: str, stream_name: str, end_time: Optional[datetime] = None) -> Path:

    """
    Downloads ~last SEGMENT_MINUTES of audio from a live/recent YT stream.
    Produces an MP3 in data/raw_audio.
    """
    end_time = end_time or datetime.now()
    uid = f"{stream_name.replace(' ', '_')}_{end_time.strftime('%Y%m%dT%H%M')}"
    out_path = AUDIO_DIR / f"{uid}.mp3"

    # Strategy: let yt-dlp fetch audio, then ffmpeg trims to ~1h when needed.
    # For live, --download-sections "*-1:00:00" is not always reliable; we pipe and limit via ffmpeg -t.
    ytdlp = f'yt-dlp -f bestaudio -o - "{url}"'
    ffmpeg = f'ffmpeg -y -t {SEGMENT_MINUTES*60} -i pipe:0 -vn -acodec libmp3lame -b:a 64k "{out_path}"'
    cmd = f"{ytdlp} | {ffmpeg}"
    subprocess.check_call(cmd, shell=True)  # raise if fails
    return out_path
