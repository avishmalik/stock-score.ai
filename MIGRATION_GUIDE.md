# Migration Guide - Project Restructure

## What Changed

The project has been restructured from a flat file structure to a standard Python package structure.

### Before
```
stock-score-ai/
├── stock_sentiment_analyzer.py
├── sentiment_analyzer_*.py
├── company_registry.py
├── youtube_audio_downloader.py
├── app.py
└── ...
```

### After
```
stock-score-ai/
├── src/
│   ├── analyzers/        # All sentiment analyzers
│   ├── core/             # Core modules (registry, downloader, transcriber)
│   ├── analysis/         # Analysis modules
│   └── web/              # Web interface
├── scripts/              # Executable scripts
├── config/               # Configuration files
└── tests/                # Test files
```

## Updated Imports

### Old Imports
```python
from stock_sentiment_analyzer import analyze_transcriptions
from company_registry import COMMON_COMPANIES
from youtube_audio_downloader import download_from_list
```

### New Imports
```python
from src.analyzers.base import analyze_transcriptions
from src.core.company_registry import COMMON_COMPANIES
from src.core.youtube_downloader import download_from_list
```

## Running Scripts

### Old Way
```bash
python run_all_sentiment_analyzers.py
python app.py
```

### New Way
```bash
python scripts/run_all_analyzers.py
python src/web/app.py
```

## Key Changes

1. **All analyzers** moved to `src/analyzers/`
2. **Core modules** moved to `src/core/`
3. **Scripts** moved to `scripts/`
4. **Config files** moved to `config/`
5. **Documentation** moved to `docs/`

## Benefits

- ✅ Better organization
- ✅ Standard Python structure
- ✅ Easier to maintain
- ✅ Clear separation of concerns
- ✅ Scalable for future growth

## Notes

- All imports have been updated in core files
- Scripts include path setup for imports
- Backward compatibility maintained where possible
- `.gitignore` updated for new structure

