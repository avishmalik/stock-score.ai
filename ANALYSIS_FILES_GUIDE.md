# Analysis Files Guide

## Overview

After transcription and sentiment analysis, the system generates multiple JSON prediction files and PNG chart files in the `downloads/analysis/` directory.

## Generated Files

### JSON Prediction Files (8 files)

Each analyzer produces a JSON file with sentiment predictions:

1. **`stock_predictions.json`** - Base analyzer (TextBlob/VADER combination)
2. **`sentiment_textblob_predictions.json`** - TextBlob algorithm
3. **`sentiment_vader_predictions.json`** - VADER sentiment analyzer
4. **`sentiment_keyword_predictions.json`** - Keyword-based algorithm
5. **`sentiment_ngram_predictions.json`** - N-gram based algorithm
6. **`sentiment_rulebased_predictions.json`** - Rule-based algorithm
7. **`sentiment_finbert_predictions.json`** - FinBERT (financial domain-specific)
8. **`sentiment_xlmroberta_hindi_predictions.json`** - XLM-RoBERTa (multilingual)

### PNG Chart Files (8 files)

Each analyzer also generates a visualization chart:
- `stock_performance_chart.png`
- `sentiment_textblob_chart.png`
- `sentiment_vader_chart.png`
- `sentiment_keyword_chart.png`
- `sentiment_ngram_chart.png`
- `sentiment_rulebased_chart.png`
- `sentiment_finbert_chart.png`
- `sentiment_xlmroberta_hindi_chart.png`

## JSON File Structure

Each prediction JSON file follows this structure:

```json
{
  "analysis_date": "2025-11-16T01:01:25.294330",
  "source_files": [
    "Stock Market Updates - VJqFJ6KaZEM_transcribed.txt"
  ],
  "total_companies_analyzed": 8,
  "companies": [
    {
      "company": "TCS",
      "sentiment_score": 0.273,
      "total_mentions": 1,
      "prediction": "POSITIVE",
      "confidence": 0.3,
      "sample_contexts": [
        "IT stocks right on top with HCL Tech TCS also clocking in for 5% kind of games"
      ]
    }
  ]
}
```

### Field Descriptions

- **`analysis_date`**: ISO timestamp when analysis was performed
- **`source_files`**: List of transcribed text files analyzed
- **`total_companies_analyzed`**: Number of companies found and analyzed
- **`companies`**: Array of company analysis objects, each containing:
  - **`company`**: Company name/ticker
  - **`sentiment_score`**: Numeric sentiment score (-1 to 1, where positive = bullish, negative = bearish)
  - **`prediction`**: Categorical prediction ("POSITIVE", "NEGATIVE", "NEUTRAL")
  - **`confidence`**: Confidence level (0 to 1)
  - **`total_mentions`**: Number of times company was mentioned
  - **`sample_contexts`**: Array of text snippets showing how company was mentioned

## How to Use These Files

### 1. For Further Analysis

You can feed any of these JSON files to AI models or analysis tools:

```python
import json

# Load a prediction file
with open('downloads/analysis/sentiment_finbert_predictions.json', 'r') as f:
    predictions = json.load(f)

# Access company predictions
for company in predictions['companies']:
    print(f"{company['company']}: {company['prediction']} (score: {company['sentiment_score']})")
```

### 2. Comparing Different Models

Since you have 8 different analyzers, you can:
- Compare predictions across models
- Identify consensus predictions
- Use ensemble methods combining multiple models
- Identify companies with high confidence across multiple models

### 3. Recommended Files for Analysis

- **`sentiment_finbert_predictions.json`** - Best for financial content (fine-tuned on financial news)
- **`sentiment_xlmroberta_hindi_predictions.json`** - Best for multilingual/mixed content
- **`stock_predictions.json`** - General purpose, combines multiple approaches

## Running Analysis Manually

If transcription completed but analysis didn't run automatically, use:

```bash
python run_analysis_on_transcribed.py
```

Or use the web interface - it should automatically run analysis after transcription completes.

## File Locations

- **Transcribed text files**: `downloads/text_files/*_transcribed.txt`
- **Analysis JSON files**: `downloads/analysis/*_predictions.json`
- **Analysis charts**: `downloads/analysis/*.png`
- **Audio files**: `downloads/audio/*.mp3`

## Next Steps

1. Review the JSON files to see sentiment predictions
2. Check the PNG charts for visualizations
3. Compare results across different analyzers
4. Use the data for further analysis or trading decisions

