# Quick Start Guide

## Step-by-Step Instructions

### Step 1: Setup Virtual Environment (if not already done)

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Note: TextBlob will automatically download NLTK data on first use
```

### Step 3: Run Stock Sentiment Analyzer

**Option A: Command Line (Easiest)**

```bash
python stock_sentiment_analyzer.py
```

This will:
- Analyze all `*_transcribed.txt` files in `downloads/text_files/`
- Generate `stock_predictions.json` in `downloads/analysis/`
- Create `stock_performance_chart.png` chart

**Option B: Python Script**

```python
from stock_sentiment_analyzer import analyze_transcriptions

results = analyze_transcriptions(
    text_files_dir='downloads/text_files',
    output_dir='downloads/analysis',
    create_chart=True
)
```

**Option C: Custom Directories**

```bash
python stock_sentiment_analyzer.py --text-dir downloads/text_files --output-dir downloads/analysis
```

### Step 4: View Results

1. **JSON File**: Open `downloads/analysis/stock_predictions.json`
   - Contains company predictions with sentiment scores
   - Includes confidence levels and sample contexts

2. **Chart**: Open `downloads/analysis/stock_performance_chart.png`
   - Visual representation of predicted performance
   - Green bars = Positive, Red bars = Negative

## Complete Workflow

1. **Download & Transcribe**:
   ```bash
   python youtube_audio_downloader.py
   ```

2. **Analyze Sentiment**:
   ```bash
   python stock_sentiment_analyzer.py
   ```

3. **View Results**:
   - Check `downloads/analysis/stock_predictions.json`
   - View `downloads/analysis/stock_performance_chart.png`

## Troubleshooting

- **No sentiment library**: Install TextBlob: `pip install textblob`
- **No transcribed files**: Run transcription first: `python audio_transcriber.py downloads/audio/`
- **Chart not generated**: Install matplotlib: `pip install matplotlib`

