# YouTube Audio Downloader

A Python script to download audio from YouTube live streams or stored live videos. Uses free, open-source tools (`yt-dlp` and `ffmpeg`) and works completely offline.

## Features

- **Live Streams**: Downloads audio from the past N hours of currently streaming videos
- **Stored Live Videos**: Downloads full audio from videos that were previously live streams
- **Audio Transcription**: Automatically transcribes audio to text (English, Hindi, or mixed)
- **Translation**: Translates Hindi/mixed content to English automatically
- Converts to MP3 format
- Batch processing from a list of URLs
- Automatically detects live streams vs stored videos
- Organizes files: audio in `downloads/audio/`, transcripts in `downloads/text_files/`
- Completely offline and free (uses Whisper for transcription)

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
- **Whisper** - Speech-to-text and translation (installed via requirements.txt)
- **PyTorch** - Required for Whisper (installed via requirements.txt)
- **TextBlob** - Sentiment analysis (installed via requirements.txt, lightweight)
- **Matplotlib** - Chart generation (installed via requirements.txt)

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
    'https://www.youtube.com/watch?v=O2ZU-tpRHZ8',
    # 'https://www.youtube.com/watch?v=STORED_LIVE_VIDEO_ID',
]

# For live streams: download past 1 hour of audio
# For stored videos: download full video audio
# Automatically transcribes to text (English, Hindi, or mixed)
stats = download_from_list(
    video_urls=urls,
    past_hours=1,
    output_dir='downloads',
    auto_transcribe=True,  # Enable automatic transcription
    transcription_model='base'  # Whisper model: 'tiny', 'base', 'small', 'medium', 'large'
)

print(f"Downloaded {stats['downloaded']} audio files")
print(f"Live streams: {stats['live_streams']}")
print(f"Stored videos: {stats['stored_videos']}")
```

### Method 3: Transcribe existing audio files

```python
from audio_transcriber import transcribe_directory

# Transcribe all audio files in downloads folder
stats = transcribe_directory(
    audio_dir='downloads',
    output_dir='downloads/text_files',
    audio_storage_dir='downloads/audio',
    model_size='base'  # 'tiny', 'base', 'small', 'medium', 'large'
)

print(f"Transcribed {stats['processed']} files")
```

### Method 4: Analyze stock sentiment from transcriptions

```python
from stock_sentiment_analyzer import analyze_transcriptions

# Analyze transcribed files and generate stock predictions
results = analyze_transcriptions(
    text_files_dir='downloads/text_files',
    output_dir='downloads/analysis',
    create_chart=True
)

# Results are saved to downloads/analysis/stock_predictions.json
# Chart saved to downloads/analysis/stock_performance_chart.png
```

Or from command line:
```bash
python stock_sentiment_analyzer.py
```

## Configuration

- `past_hours`: For live streams, download audio from the past N hours (default: 1)
- `output_dir`: Directory to save downloaded audio files (default: 'downloads')
- `auto_transcribe`: Automatically transcribe downloaded audio (default: True)
- `transcription_model`: Whisper model size (default: 'base')
  - `tiny`: Fastest, least accurate (~39MB model)
  - `base`: Good balance, recommended (~74MB model)
  - `small`: Better accuracy (~244MB model)
  - `medium`: High accuracy (~769MB model)
  - `large`: Best accuracy, slowest (~1550MB model)

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

## Output Structure

```
downloads/
├── audio/                    # Audio files (MP3)
│   └── {video_title} - {video_id}.mp3
├── text_files/              # Transcriptions
│   ├── {video_title} - {video_id}_transcribed.txt
│   └── {video_title} - {video_id}_metadata.json
└── analysis/                 # Sentiment analysis results
    ├── stock_predictions.json
    └── stock_performance_chart.png
```

- **Audio files**: Saved as MP3 format in `downloads/audio/`
- **Text files**: Transcribed text (translated to English) in `downloads/text_files/`
- **Metadata files**: JSON files with language detection, segments, etc.
- **Analysis files**: 
  - `stock_predictions.json`: Company sentiment scores, predictions, and confidence levels
  - `stock_performance_chart.png`: Visual chart showing predicted performance

## Notes

- Works completely offline (no API keys needed)
- Uses free, open-source tools only (`yt-dlp`, `ffmpeg`, `whisper`)
- Respects YouTube's terms of service
- Audio quality: Best available (VBR 0)
- For live streams: Downloads whatever buffer is available and trims to the last N hours
- Requires `ffprobe` (comes with ffmpeg) for duration detection
- **Transcription**: 
  - Supports English, Hindi, and mixed (Hindi + English) content
  - Automatically translates to English
  - First run downloads the Whisper model (~74MB for 'base' model)
  - Transcription happens automatically after download (if enabled)
  - Can also transcribe existing audio files separately

- **Stock Sentiment Analysis**:
  - Analyzes transcribed text to extract company mentions
  - Performs sentiment analysis on company discussions
  - Predicts stock performance (Positive/Negative/Neutral)
  - Generates performance charts (horizontal bar chart)
  - Stores results in JSON format with confidence scores and sample contexts
  - Uses lightweight local libraries (TextBlob recommended, or keyword-based fallback)
  - Automatically downloads NLTK data on first run (TextBlob requirement)

