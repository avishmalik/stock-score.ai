# Web Interface Guide

## Quick Start

1. **Install Flask** (if not already installed):
   ```bash
   pip install flask
   ```

2. **Start the web server**:
   ```bash
   python app.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Paste YouTube URLs**: Enter one or more YouTube URLs in the text area. You can:
   - Paste URLs one per line
   - Paste URLs separated by spaces
   - Mix full URLs (`https://www.youtube.com/watch?v=...`) and short URLs (`https://youtu.be/...`)

2. **Configure Options**:
   - **Past Hours**: For live streams, how many hours of audio to download (default: 1)
   - **Transcription Model**: Choose the Whisper model size (default: base)

3. **Click "Analyze"**: The system will:
   - Download audio from all YouTube videos
   - Transcribe audio to text (with translation if Hindi/Hinglish)
   - Run all 8 sentiment analyzers:
     - Base Sentiment Analyzer (TextBlob/VADER)
     - TextBlob Algorithm
     - VADER Algorithm
     - Keyword-Based Algorithm
     - N-gram Based Algorithm
     - Rule-Based Algorithm
     - FinBERT Algorithm
     - XLM-RoBERTa Algorithm (Multilingual)

4. **View Results**: Each analyzer produces separate files in `downloads/analysis/`:
   - `stock_predictions.json` - Base analyzer results
   - `sentiment_textblob_predictions.json` - TextBlob results
   - `sentiment_vader_predictions.json` - VADER results
   - `sentiment_keyword_predictions.json` - Keyword-based results
   - `sentiment_ngram_predictions.json` - N-gram results
   - `sentiment_rulebased_predictions.json` - Rule-based results
   - `sentiment_finbert_predictions.json` - FinBERT results
   - `sentiment_xlmroberta_hindi_predictions.json` - XLM-RoBERTa results
   - Plus corresponding chart files (`.png`)

## Features

- **Real-time Progress**: See progress updates as analysis runs
- **Error Handling**: Any errors are displayed in the interface
- **Multiple Videos**: Process multiple YouTube videos in one batch
- **Separate Analysis Files**: Each model produces its own file for easy comparison

## Notes

- The web interface runs analysis in the background, so you can close the browser tab and check back later
- Analysis results are saved to `downloads/analysis/` directory
- Audio files are saved to `downloads/audio/`
- Transcribed text files are saved to `downloads/text_files/`

## Troubleshooting

- **Port already in use**: Change the port in `app.py` (last line): `app.run(..., port=5001)`
- **Dependencies missing**: Make sure `yt-dlp` and `ffmpeg` are installed
- **Analysis fails**: Check the error messages in the web interface

