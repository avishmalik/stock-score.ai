# How to Run Stock Sentiment Analysis

## 🚀 Method 1: Web Interface (Easiest - Recommended)

### Step 1: Start the Web Server

```bash
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate
python src/web/app.py
```

### Step 2: Open Browser

Open: **http://localhost:5001**

### Step 3: Run Analysis

1. **Paste YouTube URL** in the text area
   - Example: `https://www.youtube.com/watch?v=VJqFJ6KaZEM`
   
2. **(Optional) Enter Duration** in minutes
   - Leave empty for full video
   
3. **Set Past Hours** (for live streams)
   - Default: 1 hour
   
4. **Select Transcription Model**
   - Base (recommended) or larger for better accuracy
   
5. **Click "🚀 Analyze"**

### Step 4: View Results

- **Progress bar** shows analysis status
- **Analysis files** listed when complete
- **Generated prompts** appear automatically:
  - ChatGPT Prompt (with Copy & Open buttons)
  - Cursor Prompt (with Copy button)

---

## 📋 Method 2: Command Line Scripts

### Option A: Run All Analyzers

```bash
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate

# Run all sentiment analyzers on existing transcriptions
python scripts/run_all_analyzers.py

# With custom directories
python scripts/run_all_analyzers.py --text-dir downloads/text_files --output-dir downloads/analysis

# Skip specific analyzers (e.g., skip Hindi)
python scripts/run_all_analyzers.py --skip hindi
```

### Option B: Generate Reports & Prompts

```bash
# After running analyzers, generate combined reports
python scripts/create_stock_report.py

# This creates:
# - downloads/reports/stock_analysis_report.txt
# - downloads/reports/cursor_prompt.txt
# - downloads/reports/chatgpt_prompt.txt
# - downloads/reports/stock_analysis_summary.json
```

### Option C: Comprehensive Analysis

```bash
# Run all analyzers + generate AI insights
python scripts/run_comprehensive_analysis.py
```

---

## 🔄 Complete Workflow Example

### Full Pipeline (Download → Transcribe → Analyze → Report)

```bash
# 1. Activate virtual environment
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate

# 2. Start web interface
python src/web/app.py

# 3. In browser (http://localhost:5001):
#    - Paste YouTube URL
#    - Click "Analyze"
#    - Wait for completion
#    - View prompts and copy to ChatGPT/Cursor

# OR use command line:

# 2a. Download and transcribe (if you have URLs)
python -c "
from src.core.youtube_downloader import download_from_list
download_from_list(
    video_urls=['https://www.youtube.com/watch?v=VIDEO_ID'],
    past_hours=1,
    output_dir='downloads',
    auto_transcribe=True,
    transcription_model='base',
    run_all_sentiment=False
)
"

# 3. Run all analyzers
python scripts/run_all_analyzers.py

# 4. Generate reports and prompts
python scripts/create_stock_report.py

# 5. Use the prompts
# - Copy cursor_prompt.txt for Cursor
# - Copy chatgpt_prompt.txt for ChatGPT
```

---

## 📊 What Each Method Does

### Web Interface (`python src/web/app.py`)
- ✅ Downloads audio from YouTube
- ✅ Transcribes audio automatically
- ✅ Runs all 7 sentiment analyzers
- ✅ Generates reports and prompts automatically
- ✅ Shows results in browser
- ✅ Provides copy buttons for prompts

### Run All Analyzers (`scripts/run_all_analyzers.py`)
- ✅ Runs all sentiment analyzers
- ✅ Requires existing transcriptions
- ✅ Generates JSON predictions + charts
- ❌ Doesn't download/transcribe
- ❌ Doesn't generate reports

### Create Stock Report (`scripts/create_stock_report.py`)
- ✅ Combines all analyzer results
- ✅ Generates ChatGPT prompt (detailed)
- ✅ Generates Cursor prompt (report format)
- ✅ Creates summary JSON
- ❌ Requires analysis files to exist first

---

## 🎯 Quick Start (3 Steps)

```bash
# Step 1: Start web server
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate
python src/web/app.py

# Step 2: Open browser
# Go to: http://localhost:5001

# Step 3: Analyze
# - Paste YouTube URL
# - Click "Analyze"
# - Wait for completion
# - Copy prompts to ChatGPT/Cursor
```

---

## 📁 Output Files Location

After running analysis, check:

```
downloads/
├── audio/                    # Downloaded audio files
├── text_files/              # Transcribed text files
│   ├── *_transcribed.txt
│   └── *_metadata.json
├── analysis/                # Sentiment analysis results
│   ├── sentiment_*_predictions.json  (7 files)
│   ├── sentiment_*_chart.png         (7 files)
│   └── stock_predictions.json
└── reports/                 # Combined reports & prompts
    ├── stock_analysis_report.txt
    ├── cursor_prompt.txt
    ├── chatgpt_prompt.txt
    └── stock_analysis_summary.json
```

---

## 🔧 Troubleshooting

### Error: "No transcribed files found"
**Solution:** Make sure audio was downloaded and transcribed first.

### Error: "Analysis already running"
**Solution:** Wait for current analysis to complete, or restart the server.

### Error: "Port already in use"
**Solution:** Use a different port:
```bash
python src/web/app.py 8080
```

### Analyzers failing with TypeError
**Solution:** Already fixed! The analyzers now handle dict/string contexts correctly.

---

## 💡 Tips

1. **For quick analysis**: Use web interface
2. **For batch processing**: Use command line scripts
3. **For testing**: Use `scripts/test_nse_api.py` to test NSE API
4. **For Hindi content**: Use `scripts/run_hindi_analysis.py`
5. **For detailed analysis**: Use ChatGPT prompt (includes full transcription)
6. **For quick insights**: Use Cursor prompt (report format)

---

## 🎓 Example Commands

```bash
# Test NSE API
python scripts/test_nse_api.py RELIANCE TCS INFY

# Run analysis on existing transcriptions
python scripts/run_all_analyzers.py

# Generate reports
python scripts/create_stock_report.py

# Run comprehensive analysis
python scripts/run_comprehensive_analysis.py

# Start web interface
python src/web/app.py
```

---

## ✅ Verification

To verify everything works:

```bash
# 1. Check if web app starts
python src/web/app.py
# Should show: "Starting Flask server on port 5001"

# 2. Check if analyzers can run
python scripts/run_all_analyzers.py --help

# 3. Check if report generator works
python scripts/create_stock_report.py
# Should create files in downloads/reports/
```



