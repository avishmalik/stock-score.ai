# How to Run the Application

## 🚀 Quick Start

### 1. Activate Virtual Environment

```bash
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate
```

### 2. Run Web Interface

```bash
python src/web/app.py
```

Then open: **http://localhost:5001**

---

## 📋 Detailed Steps

### Option A: Web Interface (Recommended)

**Step 1:** Start the server
```bash
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate
python src/web/app.py
```

**Step 2:** Open browser
- Go to: http://localhost:5001
- Paste YouTube URLs
- Click "Analyze"

**Step 3:** Wait for analysis
- The page will show progress
- Results appear when complete

---

### Option B: Command Line Scripts

#### Run All Sentiment Analyzers

```bash
python scripts/run_all_analyzers.py
```

This runs all 8 sentiment analyzers on transcribed files in `downloads/text_files/`

#### Run Comprehensive Analysis (with AI Insights)

```bash
python scripts/run_comprehensive_analysis.py
```

This runs all analyzers AND generates AI insights with predictions.

#### Run Hindi Analysis

```bash
python scripts/run_hindi_analysis.py
```

For Hindi/Hinglish content analysis.

---

### Option C: Python API

```python
from src.core.youtube_downloader import download_from_list

# Download and analyze
urls = ['https://www.youtube.com/watch?v=VIDEO_ID']
download_from_list(
    video_urls=urls,
    past_hours=1,
    auto_transcribe=True,
    run_all_sentiment=True
)
```

---

## 📁 File Locations

| Purpose | Location |
|---------|----------|
| **Web Interface** | `src/web/app.py` |
| **Scripts** | `scripts/` |
| **Config** | `config/companies.json` |
| **Output Files** | `downloads/` |
| - Audio | `downloads/audio/` |
| - Transcripts | `downloads/text_files/` |
| - Analysis | `downloads/analysis/` |

---

## 🔧 Common Commands

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run web interface
python src/web/app.py

# 3. Run all analyzers
python scripts/run_all_analyzers.py

# 4. Run comprehensive analysis
python scripts/run_comprehensive_analysis.py

# 5. Test download (1 minute)
python tests/test_1minute_download.py
```

---

## ⚙️ Configuration

### Change Port (if 5001 is busy)

```bash
python src/web/app.py 8080
```

### Update Company List

Edit: `config/companies.json`

---

## 🐛 Troubleshooting

### Error: "No module named 'src'"

**Solution:** Make sure you're in the project root:
```bash
cd /Users/avishmalik/Desktop/stock-score-ai
pwd  # Should show: /Users/avishmalik/Desktop/stock-score-ai
```

### Error: "Can't open file 'app.py'"

**Solution:** Use the new path:
```bash
python src/web/app.py  # ✅ Correct
python app.py          # ❌ Wrong (old path)
```

### Error: "Template not found"

**Solution:** Templates are in `templates/` folder. The app should find them automatically. If not, check that `templates/index.html` exists.

### Port Already in Use

**Solution:** Use a different port:
```bash
python src/web/app.py 8080
```

---

## 📊 What Happens When You Run

1. **Web Interface** (`python src/web/app.py`):
   - Starts Flask server on port 5001
   - Serves web UI at http://localhost:5001
   - Handles YouTube URL input
   - Runs download → transcription → analysis pipeline

2. **Run All Analyzers** (`python scripts/run_all_analyzers.py`):
   - Finds all transcribed files in `downloads/text_files/`
   - Runs all 8 sentiment analyzers
   - Saves results to `downloads/analysis/`

3. **Comprehensive Analysis** (`python scripts/run_comprehensive_analysis.py`):
   - Runs all analyzers
   - Extracts comprehensive data
   - Generates AI insights and predictions
   - Saves to `downloads/analysis/ai_insights.json`

---

## ✅ Verification

To verify everything works:

```bash
# 1. Check imports
python -c "from src.web.app import app; print('✓ Imports OK')"

# 2. Check scripts
python scripts/run_all_analyzers.py --help

# 3. Start web interface
python src/web/app.py
# Then visit http://localhost:5001
```

---

## 🎯 Next Steps

1. **Start the web interface**: `python src/web/app.py`
2. **Open browser**: http://localhost:5001
3. **Paste YouTube URLs** and analyze!
4. **Check results** in `downloads/analysis/`

For more details, see:
- `QUICK_START.md` - Quick reference
- `PROJECT_STRUCTURE.md` - Project organization
- `MIGRATION_GUIDE.md` - What changed

