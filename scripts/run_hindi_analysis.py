#!/usr/bin/env python3
"""
Quick script to run Hindi transcription and XLM-RoBERTa analysis on existing audio.
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.analyzers.hindi import process_audio_and_analyze
from pathlib import Path
import glob

# Find the audio file
audio_dir = Path('downloads/audio')
if audio_dir.exists():
    audio_files = list(audio_dir.glob('*.mp3'))
    if audio_files:
        # Use the most recent audio file
        audio_file = max(audio_files, key=lambda p: p.stat().st_mtime)
        print(f"Found audio file: {audio_file.name}\n")
        
        # Run the complete workflow
        results = process_audio_and_analyze(
            audio_path=str(audio_file),
            text_output_dir='downloads/text_files',
            analysis_output_dir='downloads/analysis',
            whisper_model_size='base',
            create_chart=True
        )
        
        if results:
            print(f"\n✓ Success! Results saved to downloads/analysis/")
            print(f"  - sentiment_xlmroberta_hindi_predictions.json")
            print(f"  - sentiment_xlmroberta_hindi_chart.png")
    else:
        print("No audio files found in downloads/audio/")
else:
    print("Audio directory not found: downloads/audio/")

