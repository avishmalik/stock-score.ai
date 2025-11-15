#!/usr/bin/env python3
"""
Helper script to run sentiment analysis on already transcribed files.
Use this if transcription completed but analysis didn't run automatically.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from scripts.run_all_analyzers import run_analyzer, SENTIMENT_ANALYZERS

def main():
    text_dir = Path('downloads/text_files')
    output_dir = Path('downloads/analysis')
    
    if not text_dir.exists():
        print(f"✗ Text directory not found: {text_dir}")
        print("  Please run transcription first.")
        return
    
    # Check if transcribed files exist
    text_files = list(text_dir.glob('*_transcribed.txt'))
    text_files = [f for f in text_files if '_hindi_transcribed.txt' not in str(f)]
    
    if not text_files:
        print(f"✗ No transcribed files found in {text_dir}")
        print("  Please run transcription first.")
        return
    
    print("="*60)
    print("Running Sentiment Analysis on Transcribed Files")
    print("="*60)
    print(f"Found {len(text_files)} transcribed file(s)")
    print(f"Text directory: {text_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    
    for idx, (analyzer_name, description) in enumerate(SENTIMENT_ANALYZERS):
        print(f"\n[{idx+1}/{len(SENTIMENT_ANALYZERS)}] Running {description}...")
        
        if run_analyzer(analyzer_name, str(text_dir), str(output_dir), no_chart=False):
            success_count += 1
        else:
            failed_count += 1
    
    print("\n" + "="*60)
    print("Analysis Summary")
    print("="*60)
    print(f"Successfully completed: {success_count}/{len(SENTIMENT_ANALYZERS)}")
    print(f"Failed: {failed_count}")
    print(f"Results saved to: {output_dir}")
    print()
    
    # List generated files
    json_files = list(output_dir.glob('*_predictions.json'))
    chart_files = list(output_dir.glob('*.png'))
    
    if json_files:
        print("Generated prediction files:")
        for f in sorted(json_files):
            print(f"  - {f.name}")
    
    if chart_files:
        print(f"\nGenerated {len(chart_files)} chart file(s)")

if __name__ == '__main__':
    main()

