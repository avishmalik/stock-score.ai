#!/usr/bin/env python3
"""
YouTube Audio Downloader
Downloads audio from YouTube live streams (past X hours) or full videos from stored live streams.
Uses yt-dlp (free, open-source) for downloading and ffmpeg for audio processing.
"""

import subprocess
import sys
import os
import tempfile
import glob
import shutil
from datetime import datetime, timedelta
from typing import List, Optional
import json


def check_dependencies():
    """Check if yt-dlp and ffmpeg are installed."""
    missing = []
    
    try:
        subprocess.run(['yt-dlp', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('yt-dlp')
    
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('ffmpeg')
    
    if missing:
        print(f"Error: Missing dependencies: {', '.join(missing)}")
        print("\nInstallation instructions:")
        if 'yt-dlp' in missing:
            print("  yt-dlp: pip install yt-dlp")
        if 'ffmpeg' in missing:
            print("  ffmpeg: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
        sys.exit(1)


def get_video_info(url: str) -> Optional[dict]:
    """Get video information including upload time."""
    # Add options to bypass 403 errors
    # Try different YouTube player clients if one fails
    player_clients = ['web', 'android', 'ios', 'tv_embedded']
    
    for client in player_clients:
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--referer', 'https://www.youtube.com/',
                '--retries', '2',
                '--extractor-args', f'youtube:player_client={client}',
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    
    # If all clients failed, try without extractor args as fallback
    cmd = [
        'yt-dlp',
        '--dump-json',
        '--no-playlist',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '--referer', 'https://www.youtube.com/',
        '--retries', '3',
        url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error getting info for {url}: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print(f"Error parsing JSON for {url}")
        return None


def is_live_stream(video_info: dict) -> bool:
    """Check if video is currently live streaming."""
    live_status = video_info.get('live_status', 'not_live')
    return live_status == 'is_live'


def was_live_stream(video_info: dict) -> bool:
    """Check if video was a live stream (now stored)."""
    live_status = video_info.get('live_status', 'not_live')
    return live_status in ('was_live', 'post_live')


def download_live_stream_audio(url: str, past_hours: int, output_dir: str = 'downloads') -> Optional[str]:
    """
    Download audio from a live stream for the past N hours using stream URL + ffmpeg.
    Uses yt-dlp to get the direct stream URL, then ffmpeg to download only the last N hours.
    
    Args:
        url: YouTube live stream URL
        past_hours: Number of hours to download (from "now" going forward)
        output_dir: Directory to save audio files
    
    Returns:
        Path to downloaded file if successful, False otherwise
    
    Note: For live streams, this downloads the NEXT N hours from "now", not the past.
    For past hour, DVR must be enabled on the stream.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print(f"Downloading live stream audio (next {past_hours} hour(s)) from: {url}")
        
        # Get video info for title
        video_info = get_video_info(url)
        video_title = video_info.get('title', 'Unknown') if video_info else 'Unknown'
        
        # Get stream URL using yt-dlp -g
        player_clients = ['web', 'android', 'ios', 'tv_embedded']
        stream_url = None
        
        for client in player_clients:
            try:
                cmd_get_url = [
                    'yt-dlp',
                    '-f', 'best[ext=mp4]/best',
                    '-g',
                    '--extractor-args', f'youtube:player_client={client}',
                    url
                ]
                result = subprocess.run(cmd_get_url, check=True, capture_output=True, text=True, timeout=30)
                stream_url = result.stdout.strip().split('\n')[0]
                if stream_url and stream_url.startswith('http'):
                    print(f"  Got stream URL (using {client} client)")
                    break
            except:
                continue
        
        if not stream_url:
            print(f"✗ Could not get stream URL for live stream\n")
            return False
        
        # Use ffmpeg to download and extract audio (limit to past_hours)
        target_seconds = past_hours * 3600
        video_id = video_info.get('id', 'live') if video_info else 'live'
        final_output = os.path.join(output_dir, f'{video_title} - {video_id}.mp3')
        
        # For live streams, use -t to limit duration (downloads next N hours from "now")
        cmd_ffmpeg = [
            'ffmpeg',
            '-i', stream_url,
            '-t', str(target_seconds),  # Limit to N hours
            '-vn',  # No video
            '-acodec', 'libmp3lame',
            '-ab', '192k',
            '-y',
            final_output
        ]
        
        print(f"  Downloading audio using ffmpeg (will download next {past_hours} hour(s))...")
        subprocess.run(cmd_ffmpeg, check=True, capture_output=True)
        
        if os.path.exists(final_output):
            print(f"✓ Successfully downloaded live stream audio (next {past_hours} hour(s)) from: {url}\n")
            return final_output
        else:
            print(f"✗ ffmpeg download failed - output file not found\n")
            return False
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else (e.stdout if e.stdout else 'Unknown error')
        print(f"✗ Failed to download live stream {url}")
        if error_msg:
            # Show last few lines of error for debugging
            error_lines = error_msg.strip().split('\n')
            if len(error_lines) > 3:
                print(f"  Error: ...{chr(10).join(error_lines[-3:])}")
            else:
                print(f"  Error: {error_msg}")
        print()
        return False
    except Exception as e:
        print(f"✗ Error processing live stream {url}: {str(e)}\n")
        return False


def download_stored_video_past_hour(url: str, past_hours: int, output_dir: str = 'downloads') -> Optional[str]:
    """
    Download the past N hours of audio from a stored live stream video using stream URL + ffmpeg.
    Uses yt-dlp to get the stream URL, then ffmpeg to download only the last N hours.
    
    Args:
        url: YouTube video URL (that was a live stream)
        past_hours: Number of hours to download from the end
        output_dir: Directory to save audio files
    
    Returns:
        Path to downloaded file if successful, False otherwise
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Get video info to calculate duration
        video_info = get_video_info(url)
        if not video_info:
            print(f"✗ Failed to get video info for {url}\n")
            return False
        
        duration = video_info.get('duration')
        if not duration:
            print(f"✗ Could not determine video duration for {url}\n")
            return False
        
        video_title = video_info.get('title', 'Unknown')
        print(f"  Video duration: {duration/3600:.2f} hours")
        
        # Calculate start time (from end)
        target_seconds = past_hours * 3600
        if duration <= target_seconds:
            print(f"  Video duration ({duration/3600:.2f}h) is shorter than requested ({past_hours}h), downloading full video")
            start_time = 0
        else:
            start_time = duration - target_seconds
            print(f"  Will download only last {past_hours} hour(s) (from {start_time:.0f}s to end)")
        
        # Try method 1: Use --download-sections (works for stored videos)
        try:
            temp_dir = tempfile.mkdtemp()
            temp_output = os.path.join(temp_dir, 'temp_%(title)s - %(id)s.%(ext)s')
            
            # Format time for --download-sections: "START-END" where times are in HH:MM:SS or seconds
            if start_time > 0:
                # Convert seconds to HH:MM:SS format for better compatibility
                start_hours = int(start_time // 3600)
                start_mins = int((start_time % 3600) // 60)
                start_secs = int(start_time % 60)
                end_hours = int(duration // 3600)
                end_mins = int((duration % 3600) // 60)
                end_secs = int(duration % 60)
                section_spec = f"{start_hours:02d}:{start_mins:02d}:{start_secs:02d}-{end_hours:02d}:{end_mins:02d}:{end_secs:02d}"
            else:
                # Download full video
                section_spec = None
            
            player_clients = ['web', 'android', 'ios', 'tv_embedded']
            download_success = False
            last_error = None
            
            for client in player_clients:
                try:
                    cmd = [
                        'yt-dlp',
                        '--extract-audio',
                        '--audio-format', 'mp3',
                        '--audio-quality', '0',
                        '--no-playlist',
                        '--no-warnings',
                        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        '--referer', 'https://www.youtube.com/',
                        '--retries', '2',
                        '--fragment-retries', '2',
                        '--extractor-args', f'youtube:player_client={client}',
                        '--output', temp_output,
                    ]
                    
                    if section_spec:
                        cmd.extend(['--download-sections', section_spec])
                    
                    cmd.append(url)
                    
                    print(f"  Downloading using --download-sections (trying {client} client)...")
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
                    download_success = True
                    break
                except subprocess.CalledProcessError as e:
                    last_error = e.stderr if e.stderr else e.stdout
                    continue
                except subprocess.TimeoutExpired:
                    last_error = "Timeout"
                    continue
            
            if download_success:
                # Find the downloaded file - check for mp3, m4a, webm, opus, etc.
                downloaded_files = []
                for ext in ['*.mp3', '*.m4a', '*.webm', '*.opus', '*.ogg', '*.*']:
                    files = glob.glob(os.path.join(temp_dir, ext))
                    downloaded_files.extend(files)
                    if downloaded_files:
                        break
                
                # Also check all files in temp_dir
                if not downloaded_files:
                    all_files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
                    downloaded_files = [os.path.join(temp_dir, f) for f in all_files if not f.startswith('.')]
                
                if downloaded_files:
                    temp_file = downloaded_files[0]
                    # If it's not mp3, we might need to convert it
                    if not temp_file.endswith('.mp3'):
                        # Convert to mp3 using ffmpeg
                        base_name = os.path.basename(temp_file)
                        mp3_name = os.path.splitext(base_name)[0] + '.mp3'
                        mp3_temp = os.path.join(temp_dir, mp3_name)
                        cmd_convert = [
                            'ffmpeg',
                            '-i', temp_file,
                            '-vn',
                            '-acodec', 'libmp3lame',
                            '-ab', '192k',
                            '-y',
                            mp3_temp
                        ]
                        try:
                            subprocess.run(cmd_convert, check=True, capture_output=True)
                            os.remove(temp_file)
                            temp_file = mp3_temp
                        except:
                            pass
                    
                    base_name = os.path.basename(temp_file)
                    final_output = os.path.join(output_dir, base_name)
                    shutil.copy2(temp_file, final_output)
                    os.remove(temp_file)
                    os.rmdir(temp_dir)
                    print(f"✓ Successfully downloaded past {past_hours} hour(s) from stored video: {url}\n")
                    return final_output
                else:
                    # Debug: list what's actually in the temp directory
                    try:
                        files_in_dir = os.listdir(temp_dir)
                        print(f"  ⚠ --download-sections completed but no file found. Files in temp dir: {files_in_dir}")
                    except:
                        print(f"  ⚠ --download-sections completed but no file found")
            else:
                if last_error:
                    error_lines = last_error.strip().split('\n')
                    if len(error_lines) > 2:
                        print(f"  ⚠ --download-sections failed: ...{error_lines[-1]}")
                    else:
                        print(f"  ⚠ --download-sections failed")
            
            # Clean up temp files
            try:
                for f in glob.glob(os.path.join(temp_dir, '*')):
                    os.remove(f)
                os.rmdir(temp_dir)
            except:
                pass
        except Exception as e:
            print(f"  ⚠ --download-sections method failed: {e}")
        
        # Method 2: Fallback - Download full video then trim with ffmpeg (most reliable for stored videos)
        print(f"  Trying download-then-trim method (downloads full video, then trims to last {past_hours} hour(s))...")
        try:
            temp_dir = tempfile.mkdtemp()
            temp_output = os.path.join(temp_dir, 'temp_%(title)s - %(id)s.%(ext)s')
            
            player_clients = ['web', 'android', 'ios', 'tv_embedded']
            download_success = False
            
            for client in player_clients:
                try:
                    cmd = [
                        'yt-dlp',
                        '--extract-audio',
                        '--audio-format', 'mp3',
                        '--audio-quality', '0',
                        '--no-playlist',
                        '--no-warnings',
                        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        '--referer', 'https://www.youtube.com/',
                        '--retries', '2',
                        '--fragment-retries', '2',
                        '--extractor-args', f'youtube:player_client={client}',
                        '--output', temp_output,
                        url
                    ]
                    
                    print(f"  Downloading full video (will trim to last {past_hours} hour(s) afterwards)...")
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
                    download_success = True
                    break
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    continue
            
            if download_success:
                # Find the downloaded file
                downloaded_files = glob.glob(os.path.join(temp_dir, '*.mp3'))
                if downloaded_files:
                    temp_file = downloaded_files[0]
                    
                    # Get file duration using ffprobe
                    cmd_probe = [
                        'ffprobe',
                        '-v', 'error',
                        '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        temp_file
                    ]
                    
                    try:
                        probe_result = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
                        file_duration = float(probe_result.stdout.strip())
                        
                        # Calculate trim start time
                        if file_duration > target_seconds:
                            trim_start = file_duration - target_seconds
                            
                            base_name = os.path.basename(temp_file)
                            final_output = os.path.join(output_dir, base_name)
                            
                            # Trim the file
                            cmd_trim = [
                                'ffmpeg',
                                '-i', temp_file,
                                '-ss', str(trim_start),
                                '-c', 'copy',
                                '-y',
                                final_output
                            ]
                            
                            print(f"  Trimming: keeping last {past_hours} hour(s) (from {trim_start:.0f}s to end)")
                            subprocess.run(cmd_trim, check=True, capture_output=True)
                            
                            # Clean up temp file
                            os.remove(temp_file)
                            os.rmdir(temp_dir)
                            
                            if os.path.exists(final_output):
                                print(f"✓ Successfully downloaded past {past_hours} hour(s) from stored video: {url}\n")
                                return final_output
                        else:
                            # File is shorter than requested, just copy it
                            base_name = os.path.basename(temp_file)
                            final_output = os.path.join(output_dir, base_name)
                            shutil.copy2(temp_file, final_output)
                            os.remove(temp_file)
                            os.rmdir(temp_dir)
                            print(f"✓ Video duration ({file_duration/3600:.2f}h) is shorter than requested ({past_hours}h), downloaded full video\n")
                            return final_output
                    except Exception as e:
                        print(f"  ⚠ Error trimming file: {e}")
                        # Fallback: just copy the file
                        base_name = os.path.basename(temp_file)
                        final_output = os.path.join(output_dir, base_name)
                        shutil.copy2(temp_file, final_output)
                        os.remove(temp_file)
                        os.rmdir(temp_dir)
                        return final_output
            
            # Clean up temp files
            try:
                for f in glob.glob(os.path.join(temp_dir, '*')):
                    os.remove(f)
                os.rmdir(temp_dir)
            except:
                pass
                
        except Exception as e:
            print(f"  ✗ Download-then-trim method failed: {str(e)}\n")
            return False
            
    except Exception as e:
        print(f"✗ Error downloading past hour from {url}: {str(e)}\n")
        return False


def download_stored_video(url: str, output_dir: str = 'downloads') -> Optional[str]:
    """
    Download the full video (audio) from a stored live stream video.
    
    Args:
        url: YouTube video URL (that was a live stream)
        output_dir: Directory to save audio files
    
    Returns:
        Path to downloaded file if successful, False otherwise
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Output template: {title} - {id}.{ext}
    output_template = os.path.join(output_dir, '%(title)s - %(id)s.%(ext)s')
    
    # Add options to bypass 403 errors - try different player clients
    player_clients = ['web', 'android', 'ios', 'tv_embedded']
    download_success = False
    
    for client in player_clients:
        try:
            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',  # Convert to MP3
                '--audio-quality', '0',   # Best quality
                '--no-playlist',
                '--no-warnings',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--referer', 'https://www.youtube.com/',
                '--retries', '2',
                '--fragment-retries', '2',
                '--extractor-args', f'youtube:player_client={client}',
                '--output', output_template,
                url
            ]
            print(f"Downloading full video audio from: {url} (trying {client} client)")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
            print(f"✓ Successfully downloaded full video audio from: {url}\n")
            # Find and return the downloaded file path
            import glob
            downloaded_files = glob.glob(os.path.join(output_dir, '*.mp3'))
            if downloaded_files:
                return max(downloaded_files, key=os.path.getmtime)
            return None
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    
    # Fallback: try without extractor args
    try:
        cmd = [
            'yt-dlp',
            '--extract-audio',
            '--audio-format', 'mp3',  # Convert to MP3
            '--audio-quality', '0',   # Best quality
            '--no-playlist',
            '--no-warnings',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--referer', 'https://www.youtube.com/',
            '--retries', '3',
            '--fragment-retries', '3',
            '--output', output_template,
            url
        ]
        print(f"Downloading full video audio from: {url} (fallback method)")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Successfully downloaded full video audio from: {url}\n")
        
        # Return the downloaded file path for transcription
        # Find the downloaded file
        import glob
        downloaded_files = glob.glob(os.path.join(output_dir, '*.mp3'))
        if downloaded_files:
            # Return the most recently modified file
            return max(downloaded_files, key=os.path.getmtime)
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else (e.stdout if e.stdout else 'Unknown error')
        print(f"✗ Failed to download {url}")
        if error_msg:
            # Show last few lines of error for debugging
            error_lines = error_msg.strip().split('\n')
            if len(error_lines) > 3:
                print(f"  Error: ...{chr(10).join(error_lines[-3:])}")
            else:
                print(f"  Error: {error_msg}")
        print()
        return None


def download_from_list(
    video_urls: List[str], 
    past_hours: int = 1,
    output_dir: str = 'downloads',
    auto_transcribe: bool = True,
    transcription_model: str = 'base',
    auto_hindi_transcribe: bool = False,
    auto_hindi_sentiment: bool = True,
    run_all_sentiment: bool = True
) -> dict:
    """
    Download audio from a list of YouTube live streams or stored live videos.
    
    - For live streams: Downloads audio for the next N hours (from "now")
    - For stored videos (that were live): Downloads the past N hours from the end of the video
    - Optionally transcribes audio to text (English, Hindi, or mixed) - with translation
    - Optionally runs all sentiment analyzers automatically (including XLM-RoBERTa)
    
    Args:
        video_urls: List of YouTube video URLs (live streams or stored live videos)
        past_hours: Number of hours to download (for live: next N hours, for stored: past N hours)
        output_dir: Directory to save audio files
        auto_transcribe: If True, automatically transcribe downloaded audio (with translation to English)
        transcription_model: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        auto_hindi_transcribe: If True, transcribe Hindi/Hinglish WITHOUT translation (usually produces garbled text)
        auto_hindi_sentiment: If True, analyze sentiment using XLM-RoBERTa (uses English translation)
        run_all_sentiment: If True, run all sentiment analyzers automatically after transcription
    
    Returns:
        Dictionary with download statistics
    """
    stats = {
        'total': len(video_urls),
        'live_streams': 0,
        'stored_videos': 0,
        'downloaded': 0,
        'failed': 0,
        'skipped': 0
    }
    
    print(f"Processing {len(video_urls)} video(s)...")
    print(f"For live streams: Downloading next {past_hours} hour(s) of audio")
    print(f"For stored live videos: Downloading past {past_hours} hour(s) from the end\n")
    
    for url in video_urls:
        # Get video info
        print(f"Fetching video info for: {url}")
        video_info = get_video_info(url)
        if not video_info:
            print(f"✗ Failed to get video info for {url}")
            print(f"  Possible reasons:")
            print(f"    - Video is private or unavailable")
            print(f"    - Invalid URL")
            print(f"    - Network error")
            print(f"    - YouTube API/access restrictions\n")
            stats['failed'] += 1
            continue
        
        video_title = video_info.get('title', 'Unknown')
        live_status = video_info.get('live_status', 'not_live')
        
        print(f"Checking: {video_title}")
        print(f"  Live status: {live_status}")
        
        # Check if it's a live stream
        if is_live_stream(video_info):
            print(f"  📡 Live stream detected - downloading next {past_hours} hour(s) of audio")
            stats['live_streams'] += 1
            result = download_live_stream_audio(url, past_hours, output_dir)
            if result:
                stats['downloaded'] += 1
                # Auto-transcribe if enabled
                if auto_transcribe and isinstance(result, str) and os.path.exists(result):
                    print(f"  🎤 Starting transcription (with translation)...")
                    try:
                        from src.core.audio_transcriber import transcribe_audio
                        transcribe_audio(
                            result,
                            output_dir=os.path.join(output_dir, 'text_files'),
                            audio_storage_dir=os.path.join(output_dir, 'audio'),
                            model_size=transcription_model
                        )
                    except Exception as e:
                        print(f"  ⚠ Transcription failed: {e}")
                
                # Hindi transcription (WITHOUT translation) for XLM-RoBERTa
                # This keeps original Hindi/Hinglish text - no translation step
                if auto_hindi_transcribe:
                    # Find audio file - it might have been moved to audio/ directory
                    audio_file = result if isinstance(result, str) and os.path.exists(result) else None
                    if not audio_file:
                        # Check if file was moved to audio directory
                        import glob
                        audio_dir = os.path.join(output_dir, 'audio')
                        if os.path.exists(audio_dir):
                            # Find the most recently modified audio file
                            audio_files = glob.glob(os.path.join(audio_dir, '*.mp3'))
                            if audio_files:
                                audio_file = max(audio_files, key=os.path.getmtime)
                    
                    if audio_file and os.path.exists(audio_file):
                        print(f"  🎤 Starting Hindi transcription (keeping original language, no translation)...")
                        try:
                            from src.analyzers.hindi import transcribe_audio_no_translation
                            hindi_text_file = transcribe_audio_no_translation(
                                audio_file,
                                output_dir=os.path.join(output_dir, 'text_files'),
                                model_size=transcription_model
                            )
                            
                            # Run XLM-RoBERTa sentiment analysis
                            # Note: Uses English translated text (better quality) since Hindi transcription is garbled
                            if auto_hindi_sentiment:
                                print(f"  📊 Analyzing sentiment with XLM-RoBERTa...")
                                try:
                                    from src.analyzers.hindi import analyze_hindi_transcriptions
                                    analyze_hindi_transcriptions(
                                        text_files_dir=os.path.join(output_dir, 'text_files'),
                                        output_dir=os.path.join(output_dir, 'analysis'),
                                        create_chart=True,
                                        use_translated_text=True  # Use English translation (better quality)
                                    )
                                except Exception as e:
                                    print(f"  ⚠ XLM-RoBERTa sentiment analysis failed: {e}")
                        except Exception as e:
                            print(f"  ⚠ Hindi transcription failed: {e}")
                    else:
                        print(f"  ⚠ Could not find audio file for Hindi transcription")
            else:
                stats['failed'] += 1
        
        # Check if it was a live stream (now stored)
        elif was_live_stream(video_info):
            print(f"  💾 Stored live video detected - downloading past {past_hours} hour(s) of audio")
            stats['stored_videos'] += 1
            # Try to download only past N hours
            result = download_stored_video_past_hour(url, past_hours, output_dir)
            # If that fails, fall back to full video download
            if not result:
                print(f"  ⚠ Past hour download failed, falling back to full video download...")
                result = download_stored_video(url, output_dir)
            if result:
                stats['downloaded'] += 1
                # Auto-transcribe if enabled
                if auto_transcribe:
                    audio_file = result if isinstance(result, str) else None
                    if not audio_file:
                        # Find the most recently downloaded file
                        import glob
                        downloaded_files = glob.glob(os.path.join(output_dir, '*.mp3'))
                        if downloaded_files:
                            audio_file = max(downloaded_files, key=os.path.getmtime)
                    
                    if audio_file and os.path.exists(audio_file):
                        print(f"  🎤 Starting transcription (with translation)...")
                        try:
                            from src.core.audio_transcriber import transcribe_audio
                            transcribe_audio(
                                audio_file,
                                output_dir=os.path.join(output_dir, 'text_files'),
                                audio_storage_dir=os.path.join(output_dir, 'audio'),
                                model_size=transcription_model
                            )
                        except Exception as e:
                            print(f"  ⚠ Transcription failed: {e}")
                
                # Hindi transcription (WITHOUT translation) for XLM-RoBERTa
                # This keeps original Hindi/Hinglish text - no translation step
                if auto_hindi_transcribe:
                    audio_file = result if isinstance(result, str) else None
                    if not audio_file:
                        # Find the most recently downloaded file
                        import glob
                        downloaded_files = glob.glob(os.path.join(output_dir, '*.mp3'))
                        if downloaded_files:
                            audio_file = max(downloaded_files, key=os.path.getmtime)
                    
                    if audio_file and os.path.exists(audio_file):
                        print(f"  🎤 Starting Hindi transcription (keeping original language, no translation)...")
                        try:
                            from src.analyzers.hindi import transcribe_audio_no_translation
                            hindi_text_file = transcribe_audio_no_translation(
                                audio_file,
                                output_dir=os.path.join(output_dir, 'text_files'),
                                model_size=transcription_model
                            )
                            
                            # Run XLM-RoBERTa sentiment analysis
                            # Note: Uses English translated text (better quality) since Hindi transcription is garbled
                            if auto_hindi_sentiment:
                                print(f"  📊 Analyzing sentiment with XLM-RoBERTa...")
                                try:
                                    from src.analyzers.hindi import analyze_hindi_transcriptions
                                    analyze_hindi_transcriptions(
                                        text_files_dir=os.path.join(output_dir, 'text_files'),
                                        output_dir=os.path.join(output_dir, 'analysis'),
                                        create_chart=True,
                                        use_translated_text=True  # Use English translation (better quality)
                                    )
                                except Exception as e:
                                    print(f"  ⚠ XLM-RoBERTa sentiment analysis failed: {e}")
                        except Exception as e:
                            print(f"  ⚠ Hindi transcription failed: {e}")
            else:
                stats['failed'] += 1
        
        # Not a live stream or stored live video - treat as regular video
        else:
            print(f"  📹 Regular video detected - downloading full video audio")
            stats['stored_videos'] += 1  # Count as stored video for stats
            result = download_stored_video(url, output_dir)
            if result:
                stats['downloaded'] += 1
                # Auto-transcribe if enabled
                if auto_transcribe:
                    audio_file = result if isinstance(result, str) else None
                    if not audio_file:
                        # Find the most recently downloaded file
                        import glob
                        downloaded_files = glob.glob(os.path.join(output_dir, '*.mp3'))
                        if downloaded_files:
                            audio_file = max(downloaded_files, key=os.path.getmtime)
                    
                    if audio_file and os.path.exists(audio_file):
                        print(f"  🎤 Starting transcription (with translation)...")
                        try:
                            from src.core.audio_transcriber import transcribe_audio
                            transcribe_audio(
                                audio_file,
                                output_dir=os.path.join(output_dir, 'text_files'),
                                audio_storage_dir=os.path.join(output_dir, 'audio'),
                                model_size=transcription_model
                            )
                        except Exception as e:
                            print(f"  ⚠ Transcription failed: {e}")
            else:
                stats['failed'] += 1
                print(f"  ✗ Failed to download video\n")
    
    return stats


def main():
    """Main function with example usage."""
    # Example: List of YouTube video URLs (live streams or stored live videos)
    video_urls = [
        # Add your YouTube URLs here
        'https://www.youtube.com/watch?v=O2ZU-tpRHZ8',
        # 'https://www.youtube.com/watch?v=STORED_LIVE_VIDEO_ID',
    ]
    
    # Configuration
    PAST_HOURS = 1  # For live streams: download audio from past 1 hour
    OUTPUT_DIR = 'downloads'  # Directory to save audio files
    AUTO_TRANSCRIBE = True  # Automatically transcribe downloaded audio (with translation to English)
    TRANSCRIPTION_MODEL = 'base'  # Whisper model: 'tiny', 'base', 'small', 'medium', 'large'
    AUTO_HINDI_TRANSCRIBE = False  # Skip Hindi transcription (produces garbled text) - use English translation instead
    AUTO_HINDI_SENTIMENT = True  # Analyze sentiment using XLM-RoBERTa on English translated text (better quality)
    
    # Check dependencies
    check_dependencies()
    
    if not video_urls:
        print("No video URLs provided!")
        print("\nUsage:")
        print("1. Edit this script and add URLs to the 'video_urls' list")
        print("2. Or import this module and call download_from_list()")
        print("\nExample:")
        print("  from src.core.youtube_downloader import download_from_list")
        print("  urls = ['https://www.youtube.com/watch?v=VIDEO_ID']")
        print("  download_from_list(urls, past_hours=1)")
        print("\nNote:")
        print("  - Live streams: Downloads audio from past N hours")
        print("  - Stored live videos: Downloads full video audio")
        return
    
    # Download audio
    stats = download_from_list(
        video_urls=video_urls,
        past_hours=PAST_HOURS,
        output_dir=OUTPUT_DIR,
        auto_transcribe=AUTO_TRANSCRIBE,
        transcription_model=TRANSCRIPTION_MODEL,
        auto_hindi_transcribe=AUTO_HINDI_TRANSCRIBE,
        auto_hindi_sentiment=AUTO_HINDI_SENTIMENT
    )
    
    # Print summary
    print("\n" + "="*50)
    print("Download Summary:")
    print(f"  Total videos: {stats['total']}")
    print(f"  Live streams: {stats['live_streams']}")
    print(f"  Stored live videos: {stats['stored_videos']}")
    print(f"  Successfully downloaded: {stats['downloaded']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("="*50)


if __name__ == '__main__':
    main()

