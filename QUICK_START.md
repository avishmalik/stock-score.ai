# Quick Start Guide

## Prerequisites

1. **Python 3.9+** installed
2. **Virtual environment** activated
3. **Dependencies** installed (`pip install -r requirements.txt`)

## Step 1: Activate Virtual Environment

```bash
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

## Step 2: Run the Web Interface

```bash
# From project root
python src/web/app.py

# OR specify a port
python src/web/app.py 8080
```

Then open your browser: **http://localhost:5001** (or the port you specified)

## Step 3: Run Analysis Scripts

### Run All Sentiment Analyzers

```bash
python scripts/run_all_analyzers.py
```

### Run Comprehensive Analysis (with AI Insights)

```bash
python scripts/run_comprehensive_analysis.py
```

### Run Hindi Analysis

```bash
python scripts/run_hindi_analysis.py
```

## Step 4: Download and Analyze YouTube Videos

### Using Python Script

```python
from src.core.youtube_downloader import download_from_list

urls = ['https://www.youtube.com/watch?v=VIDEO_ID']
download_from_list(
    video_urls=urls,
    past_hours=1,
    auto_transcribe=True,
    run_all_sentiment=True
)
```

### Using Web Interface

1. Start the web server: `python src/web/app.py`
2. Open http://localhost:5001
3. Paste YouTube URLs
4. Click "Analyze"

## Common Commands

```bash
# Activate venv
source venv/bin/activate

# Run web interface
python src/web/app.py

# Run all analyzers
python scripts/run_all_analyzers.py

# Run comprehensive analysis
python scripts/run_comprehensive_analysis.py

# Test download (1 minute)
python tests/test_1minute_download.py
```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the project root:

```bash
cd /Users/avishmalik/Desktop/stock-score-ai
python src/web/app.py
```

### Module Not Found

If modules aren't found, check that you're in the project root and venv is activated:

```bash
pwd  # Should show: /Users/avishmalik/Desktop/stock-score-ai
which python  # Should show: .../venv/bin/python
```

### Port Already in Use

If port 5001 is busy, use a different port:

```bash
python src/web/app.py 8080
```

## File Locations

- **Web Interface**: `src/web/app.py`
- **Scripts**: `scripts/`
- **Config**: `config/companies.json`
- **Output**: `downloads/` (audio, text_files, analysis)

