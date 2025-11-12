# YouTube Audio Downloader

A Python script to download audio from YouTube live streams or stored live videos. Uses free, open-source tools (`yt-dlp` and `ffmpeg`) and works completely offline.

## Features

- **Live Streams**: Downloads audio from the past N hours of currently streaming videos
- **Stored Live Videos**: Downloads full audio from videos that were previously live streams
- Converts to MP3 format
- Batch processing from a list of URLs
- Automatically detects live streams vs stored videos
- Completely offline and free

## Setup

### Quick Setup (Recommended)

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

### Manual Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

3. **Install Python dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install ffmpeg** (system package):
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg` or `sudo yum install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Dependencies

- **yt-dlp** - YouTube downloader (installed via requirements.txt)
- **ffmpeg** - Audio/video processing (system package, must be installed separately)

## Usage

### Method 1: Edit the script directly

1. **Activate virtual environment** (if not already active):
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

2. Open `youtube_audio_downloader.py`
3. Add your YouTube URLs to the `video_urls` list
4. Adjust `PAST_HOURS` if needed
5. Run: `python youtube_audio_downloader.py`

### Method 2: Use as a module

```python
from youtube_audio_downloader import download_from_list

# List of YouTube URLs (live streams or stored live videos)
urls = [
    'https://www.youtube.com/watch?v=LIVE_STREAM_ID',
    'https://www.youtube.com/watch?v=STORED_LIVE_VIDEO_ID',
]

# For live streams: download past 1 hour of audio
# For stored videos: download full video audio
stats = download_from_list(
    video_urls=urls,
    past_hours=1,
    output_dir='downloads'
)

print(f"Downloaded {stats['downloaded']} audio files")
print(f"Live streams: {stats['live_streams']}")
print(f"Stored videos: {stats['stored_videos']}")
```

## Configuration

- `past_hours`: For live streams, download audio from the past N hours (default: 1)
- `output_dir`: Directory to save downloaded audio files (default: 'downloads')

## How It Works

1. **Live Streams** (`live_status: 'is_live'`):
   - Downloads the available stream buffer
   - Automatically trims to keep only the last N hours using ffmpeg
   - If stream duration is shorter than requested hours, keeps the full stream

2. **Stored Live Videos** (`live_status: 'was_live'` or `'post_live'`):
   - Downloads the complete video audio
   - No trimming applied

3. **Regular Videos**:
   - Skipped (only processes live streams and stored live videos)

## Output

- Audio files are saved as MP3 format
- Filename format: `{video_title} - {video_id}.mp3`
- Files are saved in the specified `output_dir` directory

## Notes

- Works completely offline (no API keys needed)
- Uses free, open-source tools only (`yt-dlp` and `ffmpeg`)
- Respects YouTube's terms of service
- Audio quality: Best available (VBR 0)
- For live streams: Downloads whatever buffer is available and trims to the last N hours
- Requires `ffprobe` (comes with ffmpeg) for duration detection

