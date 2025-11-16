# Stock Score AI - Project Summary

## 🎯 Project Overview

**Stock Score AI** is a comprehensive sentiment analysis system for Indian stock market news. It downloads YouTube videos (market news, discussions), transcribes them, and analyzes sentiment across multiple companies using 7+ different AI models to generate actionable stock recommendations.

---

## 🏗️ Architecture & Components

### 1. **Core Infrastructure**

#### YouTube Downloader (`src/core/youtube_downloader.py`)
- Downloads audio from YouTube videos (regular videos, live streams, stored live videos)
- Supports downloading last N hours from live streams
- Handles various YouTube URL formats
- Uses `yt-dlp` for reliable downloads

#### Audio Transcriber (`src/core/audio_transcriber.py`)
- Transcribes audio using OpenAI Whisper (offline, no API keys)
- Supports English, Hindi, and mixed content
- Automatic translation to English
- Can transcribe existing audio files or directories
- Saves transcriptions with metadata

#### Company Registry (`src/core/company_registry.py`)
- **Centralized company database**: 358 Indian companies from NSE
- **Smart company matching**:
  - Handles abbreviations (e.g., "HCL Tech" → "hcl")
  - Partial matches and multi-word names
  - False positive detection (e.g., "acc" in "according")
  - Confidence scoring and validation
- **Metadata tracking**: Match confidence, false positive flags
- Loads from `config/india_companies_registry.json`

---

### 2. **Sentiment Analysis Engines** (7 Models)

All analyzers extract company mentions and analyze sentiment:

1. **FinBERT** (`sentiment_analyzer_finbert.py`)
   - BERT model fine-tuned on financial news
   - Best for finance-specific terminology
   - Output: `sentiment_finbert_predictions.json`

2. **TextBlob** (`sentiment_analyzer_textblob.py`)
   - Pattern analysis and word polarity
   - General-purpose sentiment analysis
   - Output: `sentiment_textblob_predictions.json`

3. **VADER** (`sentiment_analyzer_vader.py`)
   - Optimized for social media text
   - Handles negations and slang well
   - Output: `sentiment_vader_predictions.json`

4. **Keyword-Based** (`sentiment_analyzer_keyword.py`)
   - Simple keyword counting with weighted financial terms
   - No external dependencies
   - Output: `sentiment_keyword_predictions.json`

5. **N-gram Based** (`sentiment_analyzer_ngram.py`)
   - Bigram and trigram analysis for phrase-level sentiment
   - Captures context and multi-word expressions
   - Output: `sentiment_ngram_predictions.json`

6. **Rule-Based** (`sentiment_analyzer_rulebased.py`)
   - Financial domain-specific rules
   - Negation handling and intensity modifiers
   - Output: `sentiment_rulebased_predictions.json`

7. **XLM-RoBERTa (Hindi)** (`hindi.py`)
   - Multilingual sentiment analysis
   - Analyzes Hindi/Hinglish content directly
   - Output: `sentiment_xlmroberta_hindi_predictions.json`

**Common Features Across All Analyzers:**
- Extract company mentions from text
- Calculate sentiment scores (-1 to +1)
- Generate predictions (POSITIVE/NEGATIVE/NEUTRAL)
- Confidence scoring
- Sample context quotes
- **False positive flags** (`likely_false_positive`)
- **Match confidence** scores

---

### 3. **Analysis & Reporting**

#### Report Generator (`scripts/create_stock_report.py`)
- **Aggregates** sentiment scores from all 7 analyzers
- **Calculates consensus** scores weighted by confidence
- **Filters** false positives automatically
- **Generates two prompts**:
  - `cursor_prompt.txt`: Stock analysis report (same as `stock_analysis_report.txt`)
  - `chatgpt_prompt.txt`: Detailed prompt with full transcription (~6,000 tokens)
- **Outputs**:
  - `stock_analysis_report.txt`: Human-readable summary
  - `stock_analysis_summary.json`: Structured JSON data
  - Token estimates for each file

#### Comprehensive Analyzer (`src/analysis/comprehensive_analyzer.py`)
- Runs all analyzers and combines results
- Generates AI insights
- Creates aggregated predictions

---

### 4. **Web Interface** (`src/web/app.py`)

Flask web application with:
- **YouTube URL input**: Paste video URLs for analysis
- **Batch processing**: Multiple URLs at once
- **Background jobs**: Non-blocking analysis
- **API endpoints**:
  - `/api/analyze`: Run full analysis pipeline
  - `/api/transcribe`: Manual transcription trigger
  - `/api/status`: Check job status
- **Automatic workflow**: Download → Transcribe → Analyze → Generate reports

---

### 5. **Scripts & Utilities**

#### Main Scripts:
- `scripts/run_all_analyzers.py`: Run all sentiment analyzers
- `scripts/create_stock_report.py`: Generate combined reports and prompts
- `scripts/run_comprehensive_analysis.py`: Comprehensive analysis with AI insights
- `scripts/run_hindi_analysis.py`: Hindi-specific analysis

#### Helper Scripts:
- `fetch_indian_companies.py`: Fetch top 300 Indian companies from NSE
- `run_analysis_on_transcribed.py`: Analyze existing transcriptions

---

## 📊 Data Flow

```
YouTube Video URL
    ↓
[YouTube Downloader]
    ↓
Audio File (.mp3)
    ↓
[Whisper Transcriber]
    ↓
Transcribed Text (.txt)
    ↓
[7 Sentiment Analyzers] (Parallel)
    ↓
7 JSON Prediction Files
    ↓
[Report Generator]
    ↓
Combined Report + Prompts
    ↓
ChatGPT/Cursor Analysis
    ↓
Stock Recommendations
```

---

## 📁 File Structure

```
stock-score-ai/
├── src/
│   ├── core/
│   │   ├── youtube_downloader.py    # YouTube audio download
│   │   ├── audio_transcriber.py      # Whisper transcription
│   │   └── company_registry.py      # 358 companies + smart matching
│   ├── analyzers/                    # 7 sentiment models
│   │   ├── sentiment_analyzer_finbert.py
│   │   ├── sentiment_analyzer_textblob.py
│   │   ├── sentiment_analyzer_vader.py
│   │   ├── sentiment_analyzer_keyword.py
│   │   ├── sentiment_analyzer_ngram.py
│   │   ├── sentiment_analyzer_rulebased.py
│   │   └── hindi.py
│   ├── analysis/
│   │   ├── comprehensive_analyzer.py
│   │   └── ai_insights.py
│   └── web/
│       └── app.py                    # Flask web interface
├── scripts/
│   ├── run_all_analyzers.py
│   ├── create_stock_report.py       # Report generator
│   └── run_comprehensive_analysis.py
├── config/
│   └── india_companies_registry.json # 358 companies
├── downloads/
│   ├── audio/                        # Downloaded audio files
│   ├── text_files/                   # Transcriptions
│   ├── analysis/                     # JSON predictions + charts
│   └── reports/                      # Combined reports + prompts
└── docs/                             # Comprehensive documentation
```

---

## 🚀 Key Features

### 1. **Multi-Model Consensus**
- 7 different sentiment analysis algorithms
- Consensus scoring across models
- Analyzer agreement percentages
- Confidence-weighted aggregation

### 2. **Smart Company Detection**
- 358 Indian companies in registry
- Handles abbreviations, partial matches
- False positive filtering
- Match confidence scoring

### 3. **Comprehensive Output**
- Individual model predictions (JSON + charts)
- Aggregated consensus scores
- Human-readable reports
- ChatGPT-optimized prompts (with full transcription)
- Cursor-optimized prompts (report format)

### 4. **Production Ready**
- Web interface for easy use
- Background job processing
- Error handling and diagnostics
- Comprehensive logging
- Token estimates

### 5. **Offline Capable**
- No API keys required
- All models run locally
- Uses open-source tools only

---

## 📈 Output Files

### Analysis Files (`downloads/analysis/`)
- `sentiment_*_predictions.json`: Individual model predictions
- `sentiment_*_chart.png`: Visual charts for each model
- `stock_predictions.json`: Aggregated predictions

### Report Files (`downloads/reports/`)
- `stock_analysis_report.txt`: Human-readable summary
- `cursor_prompt.txt`: Report format for Cursor
- `chatgpt_prompt.txt`: Detailed prompt with full transcription
- `stock_analysis_summary.json`: Structured JSON data

### Transcription Files (`downloads/text_files/`)
- `*_transcribed.txt`: Transcribed text
- `*_metadata.json`: Transcription metadata

---

## 🎯 Use Cases

1. **Market News Analysis**: Analyze CNBC, ET Now, etc. market discussions
2. **Earnings Calls**: Transcribe and analyze company earnings calls
3. **Expert Interviews**: Analyze interviews with market experts
4. **Daily Market Updates**: Process daily market closing bell shows
5. **Stock Recommendations**: Generate actionable buy/sell recommendations

---

## 🔧 Technology Stack

- **Python 3.9+**
- **Flask**: Web framework
- **Whisper**: Audio transcription (OpenAI)
- **yt-dlp**: YouTube downloading
- **Transformers**: FinBERT, XLM-RoBERTa models
- **TextBlob/VADER**: Sentiment analysis
- **Matplotlib**: Chart generation
- **NLTK**: Natural language processing

---

## 📝 Key Improvements Made

1. **Company Registry System**
   - Centralized 358 companies
   - Smart matching with false positive detection
   - Confidence scoring

2. **Multi-Model Analysis**
   - 7 different algorithms for robust predictions
   - Consensus scoring
   - Analyzer agreement tracking

3. **Report Generation**
   - Token-optimized Cursor prompts
   - Detailed ChatGPT prompts with full context
   - Human-readable summaries

4. **Error Handling**
   - Comprehensive error diagnostics
   - Graceful failure handling
   - Detailed logging

5. **Web Interface**
   - Easy-to-use Flask app
   - Background job processing
   - API endpoints for automation

---

## 🎓 How to Use

### Quick Start:
```bash
# 1. Setup
source venv/bin/activate

# 2. Run analysis on YouTube video
python src/web/app.py
# Open http://localhost:5000
# Paste YouTube URL

# 3. Generate reports
python scripts/create_stock_report.py

# 4. Use prompts
# - Copy cursor_prompt.txt for Cursor
# - Copy chatgpt_prompt.txt for ChatGPT
```

### Command Line:
```bash
# Run all analyzers
python scripts/run_all_analyzers.py

# Generate reports
python scripts/create_stock_report.py
```

---

## 📊 Current Status

✅ **Completed:**
- YouTube downloader (regular + live streams)
- Audio transcription (Whisper)
- 7 sentiment analysis models
- Company registry (358 companies)
- Smart company matching
- False positive detection
- Report generation
- Web interface
- Comprehensive documentation

✅ **Working:**
- Full pipeline: Download → Transcribe → Analyze → Report
- Multi-model consensus
- Token-optimized prompts
- Error handling

---

## 🎯 Next Steps (Potential Enhancements)

- [ ] Real-time streaming analysis
- [ ] Database storage for historical data
- [ ] Price correlation analysis
- [ ] Backtesting predictions
- [ ] Email/SMS alerts
- [ ] Portfolio tracking
- [ ] API for external integrations

---

## 📚 Documentation

Comprehensive guides available in `docs/`:
- `QUICKSTART.md`: Getting started guide
- `SENTIMENT_ALGORITHMS.md`: Algorithm details
- `WEB_INTERFACE.md`: Web app usage
- `HINDI_SENTIMENT_GUIDE.md`: Hindi analysis
- `COMPREHENSIVE_ANALYSIS_GUIDE.md`: Advanced analysis
- `scripts/README_STOCK_REPORT.md`: Report generation guide

---

## 🏆 Summary

**Stock Score AI** is a production-ready sentiment analysis system that:
- Downloads and transcribes YouTube market news
- Analyzes sentiment using 7 different AI models
- Detects 358+ Indian companies with smart matching
- Generates actionable stock recommendations
- Provides optimized prompts for ChatGPT/Cursor
- Works completely offline with no API keys

The system is designed for both quick insights (Cursor) and deep analysis (ChatGPT), making it versatile for different use cases.

