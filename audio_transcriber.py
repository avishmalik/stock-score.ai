#!/usr/bin/env python3
"""
Audio Transcriber
Transcribes audio files to text and translates Hindi/mixed content to English.
Uses Whisper (local, free, offline) for speech-to-text and translation.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import json


def check_whisper_installed() -> bool:
    """Check if whisper is installed."""
    try:
        import whisper
        return True
    except ImportError:
        return False


def install_whisper():
    """Install whisper if not available."""
    print("Installing whisper...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"], 
                            capture_output=True)
        print("✓ Whisper installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install whisper: {e}")
        return False


def transcribe_audio(
    audio_path: str,
    output_dir: str = 'downloads/text_files',
    audio_storage_dir: str = 'downloads/audio',
    model_size: str = 'base'
) -> Optional[str]:
    """
    Transcribe audio file and translate to English if needed.
    
    Args:
        audio_path: Path to audio file
        output_dir: Directory to save text files
        audio_storage_dir: Directory to move audio files to
        model_size: Whisper model size (tiny, base, small, medium, large)
                   - tiny: fastest, least accurate
                   - base: good balance (recommended)
                   - small: better accuracy
                   - medium: high accuracy
                   - large: best accuracy, slowest
    
    Returns:
        Path to saved text file, or None if failed
    """
    try:
        import whisper
    except ImportError:
        print("Whisper not installed. Installing...")
        if not install_whisper():
            return None
        import whisper
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(audio_storage_dir, exist_ok=True)
    
    audio_file = Path(audio_path)
    if not audio_file.exists():
        print(f"✗ Audio file not found: {audio_path}")
        return None
    
    print(f"Loading Whisper model ({model_size})...")
    try:
        model = whisper.load_model(model_size)
    except Exception as e:
        print(f"✗ Failed to load Whisper model: {e}")
        print("  Note: First run will download the model (~150MB-3GB depending on size)")
        return None
    
    print(f"Transcribing: {audio_file.name}")
    
    # Improved approach for Hindi-English mixed content
    # Use better settings and prompts for financial/news content
    try:
        # Enhanced prompt for better translation quality
        initial_prompt = (
            "This is a financial news broadcast in Hindi and English. "
            "When translating Hindi to English, preserve English words exactly as spoken, "
            "especially company names (Reliance, TCS, Infosys), stock indices (Nifty, Sensex), "
            "financial terms (crore, lakh, rupees), and numbers. "
            "Translate only Hindi portions while keeping English portions unchanged."
        )
        
        # First, detect the language
        print("  Detecting language...")
        detect_result = model.transcribe(
            str(audio_file),
            language=None,
            task="transcribe",
            verbose=False
        )
        detected_language = detect_result.get('language', 'unknown')
        print(f"  Detected language: {detected_language}")
        
        # Translate with optimized settings
        print("  Translating to English...")
        result = model.transcribe(
            str(audio_file),
            language=detected_language if detected_language != 'unknown' else None,
            task="translate",
            initial_prompt=initial_prompt,
            condition_on_previous_text=True,  # Use context for better coherence
            temperature=0.0,  # Lower temperature for more consistent output
            best_of=2,  # Try multiple decodings
            beam_size=5,  # Beam search for better quality
            patience=1.0,
            compression_ratio_threshold=2.4,  # Filter out repetitive content
            logprob_threshold=-1.0,  # Filter low-confidence segments
            no_speech_threshold=0.6  # Better handling of silence
        )
        
        text = result.get('text', '').strip()
        
        # Post-process to improve quality
        # Fix common translation artifacts
        import re
        # Remove excessive spaces
        text = re.sub(r'\s+', ' ', text)
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*([A-Z])', r'\1 \2', text)
        # Fix common garbled patterns (very short words that are likely errors)
        words = text.split()
        cleaned_words = []
        for word in words:
            # Keep words that are meaningful (length > 2) or common short words
            if len(word) > 2 or word.lower() in ['is', 'in', 'on', 'at', 'to', 'of', 'it', 'we', 'he', 'be', 'do', 'go', 'no', 'so', 'up', 'if', 'my', 'me', 'us', 'an', 'as', 'or', 'am', 'hi', 'ok']:
                cleaned_words.append(word)
            # Skip very short garbled words (likely translation errors)
        text = ' '.join(cleaned_words)
        
        # If translation seems poor (too many short words), try with explicit language
        if detected_language == 'hi':
            words_check = text.split()
            if len(words_check) > 0:
                short_ratio = sum(1 for w in words_check if len(w) <= 2) / len(words_check)
                if short_ratio > 0.25:  # More than 25% very short words suggests poor translation
                    print("  Retrying with optimized Hindi translation settings...")
                    result = model.transcribe(
                        str(audio_file),
                        language='hi',
                        task="translate",
                        initial_prompt=initial_prompt,
                        condition_on_previous_text=True,
                        temperature=0.0,
                        best_of=3,  # More attempts for better quality
                        beam_size=5
                    )
                    text = result.get('text', text).strip()
                    # Re-apply post-processing
                    text = re.sub(r'\s+', ' ', text)
                    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
                    text = re.sub(r'([.,!?;:])\s*([A-Z])', r'\1 \2', text)
        
    except Exception as e:
        print(f"✗ Transcription failed: {e}")
        return None
    
    print(f"  Transcription length: {len(text)} characters")
    
    # Warn about model size for better quality
    if model_size in ['tiny', 'base'] and detected_language == 'hi':
        print(f"  ⚠ Tip: For better Hindi-English translation, consider using 'small' or larger model")
    
    # Ensure detected_language is set
    if 'detected_language' not in locals():
        detected_language = result.get('language', 'unknown')
    
    # Generate output filename
    audio_stem = audio_file.stem
    text_filename = f"{audio_stem}_transcribed.txt"
    text_path = os.path.join(output_dir, text_filename)
    
    # Save transcription
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Also save metadata (language, segments, etc.)
    metadata_filename = f"{audio_stem}_metadata.json"
    metadata_path = os.path.join(output_dir, metadata_filename)
    
    metadata = {
        'original_file': audio_file.name,
        'detected_language': detected_language,
        'text_length': len(text),
        'segments': result.get('segments', []),
        'language_probability': result.get('language_probs', {})
    }
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    # Move audio file to audio storage directory
    try:
        audio_dest = os.path.join(audio_storage_dir, audio_file.name)
        # If file already exists, add a number suffix
        counter = 1
        while os.path.exists(audio_dest):
            name_parts = audio_file.stem, counter, audio_file.suffix
            audio_dest = os.path.join(audio_storage_dir, f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}")
            counter += 1
        
        import shutil
        shutil.move(str(audio_file), audio_dest)
        print(f"  ✓ Audio moved to: {audio_dest}")
    except Exception as e:
        print(f"  ⚠ Warning: Could not move audio file: {e}")
    
    print(f"✓ Transcription saved to: {text_path}")
    return text_path


def transcribe_directory(
    audio_dir: str = 'downloads',
    output_dir: str = 'downloads/text_files',
    audio_storage_dir: str = 'downloads/audio',
    model_size: str = 'base',
    audio_extensions: tuple = ('.mp3', '.m4a', '.wav', '.ogg', '.flac', '.webm', '.opus')
) -> dict:
    """
    Transcribe all audio files in a directory.
    
    Args:
        audio_dir: Directory containing audio files
        output_dir: Directory to save text files
        audio_storage_dir: Directory to move audio files to
        model_size: Whisper model size
        audio_extensions: Tuple of audio file extensions to process
    
    Returns:
        Dictionary with transcription statistics
    """
    audio_dir_path = Path(audio_dir)
    if not audio_dir_path.exists():
        print(f"✗ Directory not found: {audio_dir}")
        return {'total': 0, 'processed': 0, 'failed': 0}
    
    # Find all audio files
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(audio_dir_path.glob(f"*{ext}"))
        audio_files.extend(audio_dir_path.glob(f"*{ext.upper()}"))
    
    if not audio_files:
        print(f"No audio files found in {audio_dir}")
        return {'total': 0, 'processed': 0, 'failed': 0}
    
    stats = {
        'total': len(audio_files),
        'processed': 0,
        'failed': 0,
        'files': []
    }
    
    print(f"Found {len(audio_files)} audio file(s) to transcribe\n")
    
    for audio_file in audio_files:
        print(f"[{stats['processed'] + stats['failed'] + 1}/{stats['total']}] Processing: {audio_file.name}")
        result = transcribe_audio(
            str(audio_file),
            output_dir=output_dir,
            audio_storage_dir=audio_storage_dir,
            model_size=model_size
        )
        
        if result:
            stats['processed'] += 1
            stats['files'].append({
                'audio': audio_file.name,
                'text_file': os.path.basename(result),
                'status': 'success'
            })
        else:
            stats['failed'] += 1
            stats['files'].append({
                'audio': audio_file.name,
                'status': 'failed'
            })
        print()
    
    return stats


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Transcribe audio files using Whisper')
    parser.add_argument(
        'audio_path',
        nargs='?',
        default=None,
        help='Path to audio file or directory (default: downloads/)'
    )
    parser.add_argument(
        '--model',
        default='base',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size (default: base)'
    )
    parser.add_argument(
        '--output-dir',
        default='downloads/text_files',
        help='Directory to save text files (default: downloads/text_files)'
    )
    parser.add_argument(
        '--audio-dir',
        default='downloads/audio',
        help='Directory to move audio files to (default: downloads/audio)'
    )
    
    args = parser.parse_args()
    
    # Check if whisper is installed
    if not check_whisper_installed():
        print("Whisper not installed. Installing...")
        if not install_whisper():
            print("Failed to install Whisper. Please install manually: pip install openai-whisper")
            sys.exit(1)
    
    # Determine input path
    if args.audio_path:
        input_path = args.audio_path
    else:
        input_path = 'downloads'
    
    input_path_obj = Path(input_path)
    
    # Process single file or directory
    if input_path_obj.is_file():
        print(f"Transcribing single file: {input_path}\n")
        result = transcribe_audio(
            str(input_path_obj),
            output_dir=args.output_dir,
            audio_storage_dir=args.audio_dir,
            model_size=args.model
        )
        if result:
            print(f"\n✓ Success! Transcription saved to: {result}")
        else:
            print("\n✗ Transcription failed")
            sys.exit(1)
    elif input_path_obj.is_dir():
        print(f"Transcribing all audio files in: {input_path}\n")
        stats = transcribe_directory(
            audio_dir=str(input_path_obj),
            output_dir=args.output_dir,
            audio_storage_dir=args.audio_dir,
            model_size=args.model
        )
        
        print("\n" + "="*50)
        print("Transcription Summary:")
        print(f"  Total files: {stats['total']}")
        print(f"  Successfully processed: {stats['processed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Output directory: {args.output_dir}")
        print("="*50)
    else:
        print(f"✗ Path not found: {input_path}")
        sys.exit(1)


if __name__ == '__main__':
    main()

