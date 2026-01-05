# Complete Step-by-Step Run Guide

## 🚀 Method 1: Web Interface (Easiest - Recommended)

### Step 1: Activate Virtual Environment
```bash
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate
```

### Step 2: Start Web Server
```bash
python src/web/app.py
```

You'll see:
```
============================================================
Stock Sentiment Analysis Web Interface
============================================================

Starting Flask server on port 5001...
Open your browser and navigate to: http://localhost:5001
```

### Step 3: Open Browser
- Go to: **http://localhost:5001**
- You'll see the web interface

### Step 4: Run Analysis
1. **Paste YouTube URL(s)** in the text area
   - Example: `https://www.youtube.com/watch?v=VIDEO_ID`
   - You can paste multiple URLs (one per line)
2. **Optional**: Enter duration in minutes (e.g., `5` for 5 minutes)
3. **Click "Analyze"** button
4. **Wait for completion** - Progress will show:
   - Downloading audio...
   - Transcribing...
   - Running analyzers...
   - Generating prompts...
5. **View Results**:
   - Sentiment analysis results
   - Generated prompts (Cursor & ChatGPT)
   - Copy buttons for prompts
   - "Open ChatGPT" button

### Step 5: Use Generated Prompts
- **Cursor Prompt**: Copy and paste into Cursor chat
- **ChatGPT Prompt**: Click "Open ChatGPT" button (auto-copies and opens)

---

## 📋 Method 2: Command Line Scripts (Step-by-Step)

### Complete Workflow

#### Step 1: Activate Virtual Environment
```bash
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate
```

#### Step 2: Download YouTube Video & Transcribe
```bash
# Option A: Download specific video
python -c "
from src.core.youtube_downloader import download_from_list
download_from_list(
    video_urls=['https://www.youtube.com/watch?v=VIDEO_ID'],
    duration=5,  # minutes
    auto_transcribe=True
)
"

# Option B: Download from list (last hour)
python -c "
from src.core.youtube_downloader import download_from_list
download_from_list(
    video_urls=['https://www.youtube.com/watch?v=VIDEO_ID'],
    past_hours=1,
    auto_transcribe=True
)
"
```

**Output Location**: `downloads/text_files/*_transcribed.txt`

#### Step 3: Run All Sentiment Analyzers
```bash
python scripts/run_all_analyzers.py
```

**What it does**:
- Finds all transcribed files in `downloads/text_files/`
- Runs 7 sentiment analyzers:
  - Base (TextBlob/VADER)
  - TextBlob
  - VADER
  - Keyword-Based
  - N-gram Based
  - Rule-Based
  - FinBERT
- Saves results to `downloads/analysis/`

**Output Files**:
- `downloads/analysis/sentiment_*_predictions.json` (7 files)
- `downloads/analysis/sentiment_*_chart.png` (7 files)

#### Step 4: Generate Prompts
```bash
python scripts/create_stock_report.py
```

**What it does**:
- Aggregates all sentiment scores
- Calculates consensus scores
- Generates two prompts:
  - `cursor_prompt.txt` (optimized for Cursor)
  - `chatgpt_prompt.txt` (detailed for ChatGPT)
- Saves to `downloads/reports/`

**Output Files**:
- `downloads/reports/cursor_prompt.txt`
- `downloads/reports/chatgpt_prompt.txt`
- `downloads/reports/stock_analysis_report.txt`
- `downloads/reports/stock_analysis_summary.json`

#### Step 5: Use the Prompts
```bash
# View Cursor prompt
cat downloads/reports/cursor_prompt.txt

# View ChatGPT prompt
cat downloads/reports/chatgpt_prompt.txt

# Or open in editor
open downloads/reports/chatgpt_prompt.txt
```

---

## 🎯 Quick Reference: All Commands

```bash
# 1. Activate virtual environment
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate

# 2. Run web interface (EASIEST)
python src/web/app.py
# Then open: http://localhost:5001

# OR use command line:

# 2a. Download & transcribe
python -c "
from src.core.youtube_downloader import download_from_list
download_from_list(['YOUTUBE_URL'], duration=5, auto_transcribe=True)
"

# 2b. Run analyzers
python scripts/run_all_analyzers.py

# 2c. Generate prompts
python scripts/create_stock_report.py

# 3. View results
ls downloads/analysis/
ls downloads/reports/
```

---

## 📊 What Happens in Each Step

### Web Interface Flow:
```
1. User pastes YouTube URL → 
2. Server downloads audio → 
3. Server transcribes audio → 
4. Server runs all analyzers → 
5. Server generates prompts → 
6. Results displayed in browser
```

### Command Line Flow:
```
1. Download audio → downloads/audio/
2. Transcribe → downloads/text_files/
3. Run analyzers → downloads/analysis/
4. Generate prompts → downloads/reports/
```

---

## 🔍 Verify Everything Works

### Test 1: Check Imports
```bash
python -c "from src.web.app import app; print('✓ Web app OK')"
python -c "from scripts.run_all_analyzers import SENTIMENT_ANALYZERS; print('✓ Analyzers OK')"
python -c "from scripts.create_stock_report import create_stock_report; print('✓ Report generator OK')"
```

### Test 2: Check Files Exist
```bash
# Check transcribed files
ls downloads/text_files/*_transcribed.txt

# Check analysis files
ls downloads/analysis/*_predictions.json

# Check report files
ls downloads/reports/*.txt
```

### Test 3: Run Quick Test
```bash
# Test 1-minute download
python tests/test_1minute_download.py
```

---

## 🐛 Troubleshooting

### Problem: "No module named 'src'"
**Solution**: Make sure you're in project root:
```bash
cd /Users/avishmalik/Desktop/stock-score-ai
pwd  # Should show: /Users/avishmalik/Desktop/stock-score-ai
```

### Problem: "Port 5001 already in use"
**Solution**: Use different port:
```bash
python src/web/app.py 8080
# Then open: http://localhost:8080
```

### Problem: "No analysis files found"
**Solution**: Run analyzers first:
```bash
python scripts/run_all_analyzers.py
```

### Problem: "No transcription found"
**Solution**: Download and transcribe first:
```bash
python -c "
from src.core.youtube_downloader import download_from_list
download_from_list(['YOUTUBE_URL'], duration=5, auto_transcribe=True)
"
```

### Problem: Virtual environment not activated
**Solution**: Activate it:
```bash
source venv/bin/activate
# You should see (venv) in your prompt
```

---

## 📁 File Structure After Running

```
downloads/
├── audio/                          # Downloaded audio files
│   └── VIDEO_TITLE.mp3
├── text_files/                     # Transcribed text
│   ├── VIDEO_TITLE_transcribed.txt
│   └── VIDEO_TITLE_metadata.json
├── analysis/                       # Sentiment analysis results
│   ├── sentiment_textblob_predictions.json
│   ├── sentiment_vader_predictions.json
│   ├── sentiment_finbert_predictions.json
│   ├── sentiment_keyword_predictions.json
│   ├── sentiment_ngram_predictions.json
│   ├── sentiment_rulebased_predictions.json
│   └── sentiment_*_chart.png (7 charts)
└── reports/                        # Generated prompts
    ├── cursor_prompt.txt           # For Cursor
    ├── chatgpt_prompt.txt          # For ChatGPT
    ├── stock_analysis_report.txt   # Human-readable
    └── stock_analysis_summary.json # JSON data
```

---

## ✅ Complete Example Run

```bash
# 1. Navigate to project
cd /Users/avishmalik/Desktop/stock-score-ai

# 2. Activate venv
source venv/bin/activate

# 3. Start web interface
python src/web/app.py

# 4. In browser (http://localhost:5001):
#    - Paste: https://www.youtube.com/watch?v=VIDEO_ID
#    - Duration: 5
#    - Click "Analyze"
#    - Wait for completion
#    - Copy prompts and use them!

# OR use command line:

# 3a. Download & transcribe
python -c "
from src.core.youtube_downloader import download_from_list
download_from_list(
    ['https://www.youtube.com/watch?v=VIDEO_ID'],
    duration=5,
    auto_transcribe=True
)
"

# 3b. Run analyzers
python scripts/run_all_analyzers.py

# 3c. Generate prompts
python scripts/create_stock_report.py

# 3d. View results
cat downloads/reports/cursor_prompt.txt
cat downloads/reports/chatgpt_prompt.txt
```

---

## 🎓 Next Steps

1. **Run analysis**: Use web interface or command line
2. **Review results**: Check `downloads/analysis/` for sentiment scores
3. **Use prompts**: Copy to Cursor or ChatGPT for stock predictions
4. **Iterate**: Try different videos, adjust duration, compare results

---

## 📚 Additional Resources

- `HOW_TO_RUN.md` - Detailed run instructions
- `QUICK_START.md` - Quick reference
- `GENERATE_PROMPTS.md` - Prompt generation guide
- `docs/README.md` - Full documentation

---

## 💡 Pro Tips

1. **Use Web Interface**: Easiest way to run everything
2. **Check Progress**: Web interface shows real-time progress
3. **Multiple Videos**: Paste multiple URLs (one per line)
4. **Duration Control**: Use duration parameter to limit analysis time
5. **Prompt Optimization**: Cursor prompt is token-optimized, ChatGPT prompt is detailed

