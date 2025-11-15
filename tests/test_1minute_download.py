#!/usr/bin/env python3
"""
Test script to download 1 minute of audio, transcribe, and run all sentiment analyzers
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the downloader
from src.core.youtube_downloader import download_from_list
from scripts.run_all_analyzers import SENTIMENT_ANALYZERS, run_analyzer

def main():
    # Video URL
    video_url = "https://www.youtube.com/watch?v=J-egHhWJjus"
    
    # Calculate 1 minute in hours (1/60)
    past_minutes = 1
    past_hours = past_minutes / 60.0
    
    print("="*60)
    print("Testing 1-Minute Download and Full Analysis Pipeline")
    print("="*60)
    print(f"Video: {video_url}")
    print(f"Duration: {past_minutes} minute(s)")
    print("="*60)
    print()
    
    # Step 1: Download audio
    print("Step 1: Downloading audio...")
    download_stats = download_from_list(
        video_urls=[video_url],
        past_hours=past_hours,  # 1 minute = 1/60 hours
        output_dir='downloads',
        auto_transcribe=True,
        transcription_model='base',
        auto_hindi_transcribe=False,
        auto_hindi_sentiment=False,  # We'll run all analyzers manually
        run_all_sentiment=False
    )
    
    print(f"\nDownload stats: {download_stats}\n")
    
    # Step 2: Check if transcription files exist
    text_dir = Path('downloads/text_files')
    text_files = list(text_dir.glob('*_transcribed.txt'))
    # Exclude Hindi transcribed files
    text_files = [f for f in text_files if '_hindi_transcribed.txt' not in str(f)]
    
    if not text_files:
        print("✗ No transcribed files found. Transcription may have failed.")
        return
    
    print(f"Step 2: Found {len(text_files)} transcribed file(s)")
    for tf in text_files:
        print(f"  - {tf.name}")
    print()
    
    # Step 3: Run all sentiment analyzers
    print("Step 3: Running all sentiment analyzers...")
    output_dir = 'downloads/analysis'
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    for idx, (analyzer_name, description) in enumerate(SENTIMENT_ANALYZERS):
        print(f"\n[{idx+1}/{len(SENTIMENT_ANALYZERS)}] Running {description}...")
        if run_analyzer(analyzer_name, str(text_dir), output_dir, no_chart=False):
            print(f"  ✓ {analyzer_name} completed successfully")
            results[analyzer_name] = "success"
        else:
            print(f"  ✗ {analyzer_name} failed")
            results[analyzer_name] = "failed"
    
    # Step 4: Show results
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    # List JSON files
    json_files = list(Path(output_dir).glob('*_predictions.json'))
    if json_files:
        print(f"\nPrediction Files ({len(json_files)}):")
        for jf in sorted(json_files):
            print(f"  - {jf.name}")
            # Read and show summary
            try:
                import json
                with open(jf, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if 'overall_sentiment' in data:
                            print(f"    Overall Sentiment: {data['overall_sentiment']}")
                        if 'average_score' in data:
                            print(f"    Average Score: {data['average_score']:.3f}")
            except:
                pass
    
    # List chart files
    chart_files = list(Path(output_dir).glob('*.png'))
    if chart_files:
        print(f"\nChart Files ({len(chart_files)}):")
        for cf in sorted(chart_files):
            print(f"  - {cf.name}")
    
    # Show analyzer results
    print(f"\nAnalyzer Results:")
    for name, status in results.items():
        status_icon = "✓" if status == "success" else "✗"
        print(f"  {status_icon} {name}: {status}")
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print(f"Output directory: {output_dir}")
    print("="*60)

if __name__ == '__main__':
    main()

