#!/usr/bin/env python3
"""
Flask Web Application for YouTube Stock Sentiment Analysis
Allows users to paste multiple YouTube links and run complete analysis pipeline.
"""

import os
import json
import threading
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Import existing modules
import sys
import os

# Add project root to Python path
current_file = os.path.abspath(__file__)
src_dir = os.path.dirname(current_file)  # src/web/
src_parent = os.path.dirname(src_dir)    # src/
project_root = os.path.dirname(src_parent)  # project root
sys.path.insert(0, project_root)

from src.core.youtube_downloader import download_from_list
from scripts.run_all_analyzers import SENTIMENT_ANALYZERS, run_analyzer

# Set template folder relative to project root
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'templates')
app = Flask(__name__, template_folder=template_dir)

# Global status tracking
analysis_status = {
    'running': False,
    'current_step': '',
    'progress': 0,
    'total_steps': 0,
    'completed_steps': 0,
    'errors': [],
    'results': {}
}


def extract_youtube_urls(text: str) -> list:
    """Extract YouTube URLs from text input."""
    import re
    urls = []
    seen = set()
    
    # Match full YouTube URLs (youtube.com/watch?v=... or youtu.be/...)
    patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'https?://youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for video_id in matches:
            url = f'https://www.youtube.com/watch?v={video_id}'
            if url not in seen:
                seen.add(url)
                urls.append(url)
    
    # Remove duplicates while preserving order
    return urls


def run_analysis_pipeline(urls: list, past_hours: int = 1, transcription_model: str = 'base'):
    """Run the complete analysis pipeline."""
    global analysis_status
    
    try:
        analysis_status['running'] = True
        analysis_status['errors'] = []
        analysis_status['results'] = {}
        analysis_status['completed_steps'] = 0
        
        # Step 1: Check dependencies
        analysis_status['current_step'] = 'Checking dependencies...'
        analysis_status['progress'] = 5
        try:
            # Check dependencies manually to avoid sys.exit
            missing = []
            try:
                subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                missing.append('yt-dlp')
            
            try:
                subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                missing.append('ffmpeg')
            
            if missing:
                analysis_status['errors'].append(f'Missing dependencies: {", ".join(missing)}')
                analysis_status['running'] = False
                return
        except Exception as e:
            analysis_status['errors'].append(f'Error checking dependencies: {str(e)}')
            analysis_status['running'] = False
            return
        
        # Step 2: Download audio and transcribe
        analysis_status['current_step'] = f'Downloading audio from {len(urls)} video(s)...'
        analysis_status['progress'] = 10
        analysis_status['total_steps'] = len(urls) + len(SENTIMENT_ANALYZERS) + 2
        
        download_stats = download_from_list(
            video_urls=urls,
            past_hours=past_hours,
            output_dir='downloads',
            auto_transcribe=True,
            transcription_model=transcription_model,
            auto_hindi_transcribe=False,  # Skip Hindi transcription (garbled)
            auto_hindi_sentiment=False,  # We'll run all analyzers together
            run_all_sentiment=False  # We'll run manually to track progress
        )
        
        analysis_status['completed_steps'] += len(urls)
        analysis_status['results']['download_stats'] = download_stats
        
        # Step 3: Check if transcription files exist
        text_dir = Path('downloads/text_files')
        audio_dir = Path('downloads/audio')
        downloads_dir = Path('downloads')
        
        # First check if audio files were downloaded
        audio_files = []
        audio_extensions = ['.mp3', '.m4a', '.wav', '.ogg', '.flac', '.webm', '.opus']
        for ext in audio_extensions:
            audio_files.extend(list(downloads_dir.glob(f"*{ext}")))
            audio_files.extend(list(downloads_dir.glob(f"*{ext.upper()}")))
            if audio_dir.exists():
                audio_files.extend(list(audio_dir.glob(f"*{ext}")))
                audio_files.extend(list(audio_dir.glob(f"*{ext.upper()}")))
        
        text_files = list(text_dir.glob('*_transcribed.txt')) if text_dir.exists() else []
        # Exclude Hindi transcribed files
        text_files = [f for f in text_files if '_hindi_transcribed.txt' not in str(f)]
        
        if not text_files:
            error_msg = 'No transcribed files found.'
            if audio_files:
                error_msg += f' Found {len(audio_files)} audio file(s) but transcription may have failed. Please check transcription logs.'
            elif download_stats.get('downloaded', 0) > 0:
                error_msg += f' Audio download reported success but no audio files found. Please check downloads directory.'
            else:
                error_msg += ' No audio files were downloaded. Please check if the video URLs are valid and accessible.'
            
            analysis_status['errors'].append(error_msg)
            analysis_status['results']['diagnostics'] = {
                'audio_files_found': len(audio_files),
                'audio_file_paths': [str(f) for f in audio_files[:5]],  # Show first 5
                'text_dir_exists': text_dir.exists(),
                'download_stats': download_stats
            }
            analysis_status['running'] = False
            return
        
        analysis_status['current_step'] = f'Found {len(text_files)} transcribed file(s). Running sentiment analyzers...'
        analysis_status['progress'] = 50
        
        # Step 4: Run all sentiment analyzers
        output_dir = 'downloads/analysis'
        os.makedirs(output_dir, exist_ok=True)
        
        success_count = 0
        failed_count = 0
        
        for idx, (analyzer_name, description) in enumerate(SENTIMENT_ANALYZERS):
            analysis_status['current_step'] = f'Running {description}...'
            analysis_status['progress'] = 50 + int((idx + 1) / len(SENTIMENT_ANALYZERS) * 45)
            
            if run_analyzer(analyzer_name, str(text_dir), output_dir, no_chart=False):
                success_count += 1
            else:
                failed_count += 1
                analysis_status['errors'].append(f'Failed to run {analyzer_name}')
            
            analysis_status['completed_steps'] += 1
        
        # Step 5: Collect results
        analysis_status['current_step'] = 'Collecting results...'
        analysis_status['progress'] = 95
        
        output_path = Path(output_dir)
        json_files = list(output_path.glob('*_predictions.json'))
        
        analysis_status['results']['analyzer_results'] = {
            'successful': success_count,
            'failed': failed_count,
            'total': len(SENTIMENT_ANALYZERS),
            'output_files': [f.name for f in sorted(json_files)]
        }
        
        # List all generated files
        chart_files = list(output_path.glob('*.png'))
        analysis_status['results']['chart_files'] = [f.name for f in sorted(chart_files)]
        
        analysis_status['current_step'] = 'Analysis complete!'
        analysis_status['progress'] = 100
        analysis_status['completed_steps'] = analysis_status['total_steps']
        
    except Exception as e:
        analysis_status['errors'].append(f'Error: {str(e)}')
        import traceback
        analysis_status['errors'].append(traceback.format_exc())
    finally:
        analysis_status['running'] = False


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Start analysis pipeline."""
    global analysis_status
    
    if analysis_status['running']:
        return jsonify({
            'success': False,
            'message': 'Analysis already running. Please wait for it to complete.'
        }), 400
    
    data = request.get_json()
    urls_text = data.get('urls', '')
    past_hours = int(data.get('past_hours', 1))
    transcription_model = data.get('transcription_model', 'base')
    
    if not urls_text:
        return jsonify({
            'success': False,
            'message': 'No URLs provided'
        }), 400
    
    # Extract YouTube URLs
    urls = extract_youtube_urls(urls_text)
    
    if not urls:
        return jsonify({
            'success': False,
            'message': 'No valid YouTube URLs found. Please check your input.'
        }), 400
    
    # Reset status
    analysis_status = {
        'running': True,
        'current_step': 'Starting analysis...',
        'progress': 0,
        'total_steps': len(urls) + len(SENTIMENT_ANALYZERS) + 2,
        'completed_steps': 0,
        'errors': [],
        'results': {}
    }
    
    # Start analysis in background thread
    thread = threading.Thread(
        target=run_analysis_pipeline,
        args=(urls, past_hours, transcription_model)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Analysis started for {len(urls)} video(s)',
        'urls_found': len(urls),
        'urls': urls
    })


@app.route('/api/status', methods=['GET'])
def status():
    """Get current analysis status."""
    return jsonify(analysis_status)


@app.route('/api/results', methods=['GET'])
def results():
    """Get analysis results."""
    output_dir = Path('downloads/analysis')
    
    if not output_dir.exists():
        return jsonify({
            'success': False,
            'message': 'No results found'
        }), 404
    
    json_files = list(output_dir.glob('*_predictions.json'))
    chart_files = list(output_dir.glob('*.png'))
    
    results_data = {
        'success': True,
        'json_files': [f.name for f in sorted(json_files)],
        'chart_files': [f.name for f in sorted(chart_files)],
        'output_directory': str(output_dir.absolute())
    }
    
    return jsonify(results_data)


@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Manually trigger transcription for existing audio files."""
    from src.core.audio_transcriber import transcribe_directory
    
    data = request.get_json() or {}
    transcription_model = data.get('transcription_model', 'base')
    
    downloads_dir = Path('downloads')
    audio_dir = Path('downloads/audio')
    text_dir = Path('downloads/text_files')
    
    # Find audio files in downloads and audio directories
    audio_files = []
    audio_extensions = ['.mp3', '.m4a', '.wav', '.ogg', '.flac', '.webm', '.opus']
    for ext in audio_extensions:
        audio_files.extend(list(downloads_dir.glob(f"*{ext}")))
        audio_files.extend(list(downloads_dir.glob(f"*{ext.upper()}")))
        if audio_dir.exists():
            audio_files.extend(list(audio_dir.glob(f"*{ext}")))
            audio_files.extend(list(audio_dir.glob(f"*{ext.upper()}")))
    
    if not audio_files:
        return jsonify({
            'success': False,
            'message': 'No audio files found. Please download audio files first.'
        }), 404
    
    # Transcribe all audio files
    try:
        stats = transcribe_directory(
            audio_dir=str(downloads_dir),
            output_dir=str(text_dir),
            audio_storage_dir=str(audio_dir),
            model_size=transcription_model
        )
        
        return jsonify({
            'success': True,
            'message': f'Transcription completed. Processed {stats["processed"]} file(s), {stats["failed"]} failed.',
            'stats': stats
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Transcription failed: {str(e)}',
            'error_details': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    import sys
    
    # Try to use port from environment variable or command line, default to 5001
    port = 5001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}. Using default port 5001.")
    else:
        port = int(os.environ.get('FLASK_PORT', 5001))
    
    print("="*60)
    print("Stock Sentiment Analysis Web Interface")
    print("="*60)
    print(f"\nStarting Flask server on port {port}...")
    print(f"Open your browser and navigate to: http://localhost:{port}")
    print("\nNote: If port is in use, specify a different port:")
    print("  python app.py 8080")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\n✗ Port {port} is already in use!")
            print(f"Try running with a different port: python app.py {port + 1}")
            print("\nOn macOS, port 5000 is often used by AirPlay Receiver.")
            print("You can disable it in System Preferences -> General -> AirDrop & Handoff")
        else:
            raise

