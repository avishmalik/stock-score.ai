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


def download_live_stream_audio(url: str, past_hours: int, output_dir: str = 'downloads') -> bool:
    """
    Download audio from a live stream for the past N hours.
    Downloads available stream and trims to keep only the last N hours.
    
    Args:
        url: YouTube live stream URL
        past_hours: Number of hours to keep from the past
        output_dir: Directory to save audio files
    
    Returns:
        True if successful, False otherwise
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Use a temporary file for initial download
    temp_dir = tempfile.mkdtemp()
    temp_output = os.path.join(temp_dir, 'temp_%(title)s - %(id)s.%(ext)s')
    
    try:
        print(f"Downloading live stream audio (will keep past {past_hours} hour(s)) from: {url}")
        
        # Download the live stream (yt-dlp handles live streams)
        # Add options to bypass 403 errors - try different player clients
        player_clients = ['web', 'android', 'ios', 'tv_embedded']
        download_success = False
        
        for client in player_clients:
            try:
                cmd_download = [
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
                result = subprocess.run(cmd_download, check=True, capture_output=True, text=True, timeout=300)
                download_success = True
                break
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
        
        if not download_success:
            # Fallback: try without extractor args
            cmd_download = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0',
                '--no-playlist',
                '--no-warnings',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--referer', 'https://www.youtube.com/',
                '--retries', '3',
                '--fragment-retries', '3',
                '--output', temp_output,
                url
            ]
            result = subprocess.run(cmd_download, check=True, capture_output=True, text=True)
        
        # Find the downloaded file
        downloaded_files = glob.glob(os.path.join(temp_dir, '*.mp3'))
        if not downloaded_files:
            print(f"✗ No audio file found after download\n")
            return False
        
        temp_file = downloaded_files[0]
        
        # Get file duration using ffprobe
        cmd_probe = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            temp_file
        ]
        
        probe_result = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
        duration_seconds = float(probe_result.stdout.strip())
        target_seconds = past_hours * 3600
        
        # Final output filename
        base_name = os.path.basename(temp_file)
        final_output = os.path.join(output_dir, base_name)
        
        # If duration is longer than target, trim to keep only the last N hours
        if duration_seconds > target_seconds:
            start_time = duration_seconds - target_seconds
            print(f"  Trimming: keeping last {past_hours} hour(s) (from {start_time:.0f}s to end)")
            
            cmd_trim = [
                'ffmpeg',
                '-i', temp_file,
                '-ss', str(start_time),
                '-c', 'copy',
                '-y',  # Overwrite output file
                final_output
            ]
            
            subprocess.run(cmd_trim, check=True, capture_output=True)
        else:
            # Duration is shorter than target, just copy the file
            print(f"  Stream duration ({duration_seconds/3600:.2f}h) is shorter than requested ({past_hours}h), keeping full stream")
            shutil.copy2(temp_file, final_output)
        
        # Clean up temp file
        os.remove(temp_file)
        os.rmdir(temp_dir)
        
        print(f"✓ Successfully downloaded live stream audio (past {past_hours} hour(s)) from: {url}\n")
        return True
        
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
        # Clean up temp files
        try:
            for f in glob.glob(os.path.join(temp_dir, '*')):
                os.remove(f)
            os.rmdir(temp_dir)
        except:
            pass
        return False
    except Exception as e:
        print(f"✗ Error processing live stream {url}: {str(e)}\n")
        return False


def download_stored_video(url: str, output_dir: str = 'downloads') -> bool:
    """
    Download the full video (audio) from a stored live stream video.
    
    Args:
        url: YouTube video URL (that was a live stream)
        output_dir: Directory to save audio files
    
    Returns:
        True if successful, False otherwise
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
            return True
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
        return False


def download_from_list(
    video_urls: List[str], 
    past_hours: int = 1,
    output_dir: str = 'downloads'
) -> dict:
    """
    Download audio from a list of YouTube live streams or stored live videos.
    
    - For live streams: Downloads audio for the past N hours
    - For stored videos (that were live): Downloads the full video audio
    
    Args:
        video_urls: List of YouTube video URLs (live streams or stored live videos)
        past_hours: For live streams, download audio from past N hours
        output_dir: Directory to save audio files
    
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
    print(f"For live streams: Downloading past {past_hours} hour(s) of audio\n")
    
    for url in video_urls:
        # Get video info
        video_info = get_video_info(url)
        if not video_info:
            stats['failed'] += 1
            continue
        
        video_title = video_info.get('title', 'Unknown')
        live_status = video_info.get('live_status', 'not_live')
        
        print(f"Checking: {video_title}")
        print(f"  Live status: {live_status}")
        
        # Check if it's a live stream
        if is_live_stream(video_info):
            print(f"  📡 Live stream detected - downloading past {past_hours} hour(s) of audio")
            stats['live_streams'] += 1
            if download_live_stream_audio(url, past_hours, output_dir):
                stats['downloaded'] += 1
            else:
                stats['failed'] += 1
        
        # Check if it was a live stream (now stored)
        elif was_live_stream(video_info):
            print(f"  💾 Stored live video detected - downloading full video audio")
            stats['stored_videos'] += 1
            if download_stored_video(url, output_dir):
                stats['downloaded'] += 1
            else:
                stats['failed'] += 1
        
        # Not a live stream or stored live video
        else:
            print(f"  ⏭ Skipped (not a live stream or stored live video)\n")
            stats['skipped'] += 1
    
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
    
    # Check dependencies
    check_dependencies()
    
    if not video_urls:
        print("No video URLs provided!")
        print("\nUsage:")
        print("1. Edit this script and add URLs to the 'video_urls' list")
        print("2. Or import this module and call download_from_list()")
        print("\nExample:")
        print("  from youtube_audio_downloader import download_from_list")
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
        output_dir=OUTPUT_DIR
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

