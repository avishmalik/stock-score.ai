# Project Structure

## Overview

This project follows a standard Python package structure for better organization and maintainability.

## Directory Structure

```
stock-score-ai/
├── src/                          # Source code
│   ├── __init__.py
│   ├── analyzers/                # Sentiment analysis algorithms
│   │   ├── __init__.py
│   │   ├── base.py              # Base analyzer (TextBlob/VADER)
│   │   ├── sentiment_analyzer_textblob.py
│   │   ├── sentiment_analyzer_vader.py
│   │   ├── sentiment_analyzer_keyword.py
│   │   ├── sentiment_analyzer_ngram.py
│   │   ├── sentiment_analyzer_rulebased.py
│   │   ├── sentiment_analyzer_finbert.py
│   │   └── hindi.py             # Hindi/XLM-RoBERTa analyzer
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── company_registry.py  # Centralized company list
│   │   ├── audio_transcriber.py # Audio transcription
│   │   └── youtube_downloader.py # YouTube audio downloader
│   ├── analysis/                 # Analysis modules
│   │   ├── __init__.py
│   │   ├── comprehensive_analyzer.py # Runs all analyzers
│   │   └── ai_insights.py       # AI insights generator
│   └── web/                      # Web interface
│       ├── __init__.py
│       └── app.py               # Flask application
├── scripts/                      # Executable scripts
│   ├── run_all_analyzers.py     # Run all sentiment analyzers
│   ├── run_comprehensive_analysis.py # Comprehensive analysis
│   └── run_hindi_analysis.py    # Hindi-specific analysis
├── tests/                        # Test files
│   └── test_1minute_download.py
├── config/                       # Configuration files
│   └── companies.json           # Company list (JSON format)
├── templates/                    # HTML templates
│   └── index.html
├── docs/                         # Documentation
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── COMPANY_REGISTRY_GUIDE.md
│   └── ...
├── downloads/                    # Generated files (gitignored)
│   ├── audio/
│   ├── text_files/
│   └── analysis/
├── venv/                         # Virtual environment (gitignored)
├── requirements.txt
├── .gitignore
└── PROJECT_STRUCTURE.md          # This file
```

## Import Guidelines

### From Project Root

```python
# Core modules
from src.core.company_registry import COMMON_COMPANIES
from src.core.youtube_downloader import download_from_list
from src.core.audio_transcriber import transcribe_audio

# Analyzers
from src.analyzers.base import analyze_transcriptions
from src.analyzers.finbert import analyze_transcriptions

# Analysis
from src.analysis.comprehensive_analyzer import run_all_analyzers
from src.analysis.ai_insights import generate_ai_insights
```

### From Within src/

```python
# Relative imports
from .core.company_registry import COMMON_COMPANIES
from ..analyzers.base import analyze_transcriptions
```

## Adding New Files

1. **New Analyzer**: Add to `src/analyzers/` and update `src/analyzers/__init__.py`
2. **New Core Module**: Add to `src/core/` and update `src/core/__init__.py`
3. **New Script**: Add to `scripts/` directory
4. **New Test**: Add to `tests/` directory
5. **New Config**: Add to `config/` directory

## Running Scripts

All scripts should be run from the project root:

```bash
# From project root
python scripts/run_all_analyzers.py
python scripts/run_comprehensive_analysis.py
python src/web/app.py
```

## Benefits

1. **Clear Separation**: Each module has a clear purpose
2. **Easy Navigation**: Find files quickly
3. **Scalable**: Easy to add new features
4. **Standard**: Follows Python best practices
5. **Maintainable**: Changes are localized

