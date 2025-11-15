#!/usr/bin/env python3
"""
Run All Sentiment Analyzers
Runs all sentiment analysis algorithms (including XLM-RoBERTa) automatically.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# List of all sentiment analyzers (updated paths)
SENTIMENT_ANALYZERS = [
    ('src/analyzers/base', 'Base Sentiment Analyzer (TextBlob/VADER)'),
    ('src/analyzers/textblob', 'TextBlob Algorithm'),
    ('src/analyzers/vader', 'VADER Algorithm'),
    ('src/analyzers/keyword', 'Keyword-Based Algorithm'),
    ('src/analyzers/ngram', 'N-gram Based Algorithm'),
    ('src/analyzers/rulebased', 'Rule-Based Algorithm'),
    ('src/analyzers/finbert', 'FinBERT Algorithm'),
    ('src/analyzers/hindi', 'XLM-RoBERTa Algorithm (Multilingual)'),
]


def run_analyzer(analyzer_name: str, text_dir: str, output_dir: str, no_chart: bool = False) -> bool:
    """Run a single sentiment analyzer."""
    # Handle both old format (filename) and new format (path)
    if '/' in analyzer_name:
        analyzer_path = Path(project_root) / f'{analyzer_name}.py'
    else:
        analyzer_path = Path(project_root) / f'src/analyzers/{analyzer_name.replace("sentiment_analyzer_", "").replace("stock_sentiment_analyzer", "base").replace("hindi_sentiment_analyzer", "hindi")}.py'
    
    if not analyzer_path.exists():
        print(f"✗ Analyzer not found: {analyzer_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Running: {analyzer_name}")
    print('='*60)
    
    try:
        cmd = [
            sys.executable,
            str(analyzer_path),
            '--text-dir', text_dir,
            '--output-dir', output_dir
        ]
        
        if no_chart:
            cmd.append('--no-chart')
        
        # Special handling for hindi analyzer
        if 'hindi' in analyzer_name.lower():
            cmd.append('--analyze-only')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"✗ Error running {analyzer_name}:")
            if result.stderr:
                print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout running {analyzer_name}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run all sentiment analyzers automatically'
    )
    parser.add_argument(
        '--text-dir',
        default='downloads/text_files',
        help='Directory containing transcribed text files (default: downloads/text_files)'
    )
    parser.add_argument(
        '--output-dir',
        default='downloads/analysis',
        help='Directory to save analysis results (default: downloads/analysis)'
    )
    parser.add_argument(
        '--no-chart',
        action='store_true',
        help='Skip creating charts for all analyzers'
    )
    parser.add_argument(
        '--skip',
        nargs='+',
        help='Skip specific analyzers (e.g., --skip finbert xlmroberta)'
    )
    
    args = parser.parse_args()
    
    text_dir = Path(args.text_dir)
    if not text_dir.exists():
        print(f"✗ Directory not found: {text_dir}")
        return
    
    # Check if transcribed files exist
    text_files = list(text_dir.glob('*_transcribed.txt'))
    if not text_files:
        print(f"✗ No transcribed files found in {text_dir}")
        print("  Run transcription first: python youtube_audio_downloader.py")
        return
    
    print("="*60)
    print("Running All Sentiment Analyzers")
    print("="*60)
    print(f"Found {len(text_files)} transcribed file(s)")
    print(f"Text directory: {text_dir}")
    print(f"Output directory: {args.output_dir}")
    
    skip_list = [s.lower() for s in (args.skip or [])]
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for analyzer_name, description in SENTIMENT_ANALYZERS:
        # Check if this analyzer should be skipped
        if any(skip in analyzer_name.lower() for skip in skip_list):
            print(f"\n⏭ Skipping {analyzer_name}")
            skipped_count += 1
            continue
        
        if run_analyzer(analyzer_name, str(text_dir), args.output_dir, args.no_chart):
            success_count += 1
        else:
            failed_count += 1
    
    total_run = len(SENTIMENT_ANALYZERS) - skipped_count
    
    print("\n" + "="*60)
    print("Summary:")
    print(f"  Successfully completed: {success_count}/{total_run}")
    print(f"  Failed: {failed_count}")
    if skipped_count > 0:
        print(f"  Skipped: {skipped_count}")
    print(f"  Results saved to: {args.output_dir}")
    print("="*60)
    
    # List output files
    output_path = Path(args.output_dir)
    if output_path.exists():
        json_files = list(output_path.glob('*_predictions.json'))
        if json_files:
            print("\nGenerated prediction files:")
            for json_file in sorted(json_files):
                print(f"  - {json_file.name}")


if __name__ == '__main__':
    main()

