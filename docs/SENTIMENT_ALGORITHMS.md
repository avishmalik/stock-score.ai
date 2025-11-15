# Sentiment Analysis Algorithms Guide

This project includes **6 different sentiment analysis algorithms** that you can run individually to compare their results.

## Available Algorithms

### 1. TextBlob (`sentiment_analyzer_textblob.py`)
- **Algorithm**: Pattern analysis and word polarity using TextBlob library
- **Dependencies**: `textblob` (pip install textblob)
- **Output**: `sentiment_textblob_predictions.json`
- **Best for**: General-purpose sentiment analysis with good accuracy

### 2. VADER (`sentiment_analyzer_vader.py`)
- **Algorithm**: Valence Aware Dictionary and sEntiment Reasoner
- **Dependencies**: `vaderSentiment` (pip install vaderSentiment)
- **Output**: `sentiment_vader_predictions.json`
- **Best for**: Social media text, handles negations and slang well

### 3. Keyword-Based (`sentiment_analyzer_keyword.py`)
- **Algorithm**: Simple keyword counting with weighted financial terms
- **Dependencies**: None (pure Python)
- **Output**: `sentiment_keyword_predictions.json`
- **Best for**: Fast analysis, no external dependencies

### 4. N-gram Based (`sentiment_analyzer_ngram.py`)
- **Algorithm**: Bigram and trigram analysis for phrase-level sentiment
- **Dependencies**: None (pure Python)
- **Output**: `sentiment_ngram_predictions.json`
- **Best for**: Understanding context and multi-word expressions

### 5. Rule-Based (`sentiment_analyzer_rulebased.py`)
- **Algorithm**: Financial domain-specific rules with negation handling
- **Dependencies**: None (pure Python)
- **Output**: `sentiment_rulebased_predictions.json`
- **Best for**: Financial terminology and domain-specific patterns

### 6. FinBERT (`sentiment_analyzer_finbert.py`)
- **Algorithm**: BERT model fine-tuned on financial news sentiment (ProsusAI)
- **Dependencies**: `transformers`, `torch` (pip install transformers torch)
- **Output**: `sentiment_finbert_predictions.json`
- **Best for**: Finance-specific wording like "margin contraction", "beat estimates", etc. Most accurate for stock price correlation tasks
- **Note**: First run downloads ~500MB model. Requires internet connection.

## Installation

### Required Dependencies (for all algorithms)
```bash
pip install matplotlib  # For chart generation
```

### Optional Dependencies (for specific algorithms)
```bash
# For TextBlob algorithm
pip install textblob

# For VADER algorithm
pip install vaderSentiment

# For FinBERT algorithm (recommended for financial text)
pip install transformers torch
```

**Note**: Algorithms 3, 4, and 5 (Keyword, N-gram, Rule-Based) work without any external sentiment libraries.

## Usage

### Run Individual Algorithms

```bash
# Algorithm 1: TextBlob
python sentiment_analyzer_textblob.py

# Algorithm 2: VADER
python sentiment_analyzer_vader.py

# Algorithm 3: Keyword-Based
python sentiment_analyzer_keyword.py

# Algorithm 4: N-gram Based
python sentiment_analyzer_ngram.py

# Algorithm 5: Rule-Based
python sentiment_analyzer_rulebased.py

# Algorithm 6: FinBERT (recommended for financial text)
python sentiment_analyzer_finbert.py
```

### Custom Directories

```bash
python sentiment_analyzer_textblob.py --text-dir downloads/text_files --output-dir downloads/analysis
```

### Skip Chart Generation

```bash
python sentiment_analyzer_textblob.py --no-chart
```

## Output Files

All algorithms save their results to `downloads/analysis/`:

- `sentiment_textblob_predictions.json` - TextBlob results
- `sentiment_vader_predictions.json` - VADER results
- `sentiment_keyword_predictions.json` - Keyword-based results
- `sentiment_ngram_predictions.json` - N-gram results
- `sentiment_rulebased_predictions.json` - Rule-based results
- `sentiment_finbert_predictions.json` - FinBERT results (most accurate for financial text)

Each JSON file contains:
- `algorithm`: Algorithm name
- `algorithm_description`: How the algorithm works
- `analysis_date`: When analysis was performed
- `total_companies_analyzed`: Number of companies found
- `companies`: Array of company predictions with:
  - `company`: Company name
  - `sentiment_score`: Score from -1 to 1
  - `prediction`: POSITIVE, NEGATIVE, or NEUTRAL
  - `confidence`: Confidence level (0 to 1)
  - `total_mentions`: Number of times company was mentioned
  - `sample_contexts`: Example sentences mentioning the company
- `summary`: Count of positive/negative/neutral predictions

## Comparing Results

After running all 5 algorithms, you can compare the JSON files to see:

1. **Which algorithm gives different predictions** for the same companies
2. **Sentiment score differences** between algorithms
3. **Confidence level variations**
4. **Which algorithm aligns best** with your expectations

### Example Comparison

```python
import json

# Load results from different algorithms
with open('downloads/analysis/sentiment_textblob_predictions.json') as f:
    textblob = json.load(f)

with open('downloads/analysis/sentiment_vader_predictions.json') as f:
    vader = json.load(f)

# Compare predictions for a specific company
company = "Reliance"
for algo_name, results in [("TextBlob", textblob), ("VADER", vader)]:
    for comp in results['companies']:
        if comp['company'] == company:
            print(f"{algo_name}: {comp['prediction']} (score: {comp['sentiment_score']}, confidence: {comp['confidence']})")
```

## Algorithm Characteristics

| Algorithm | Speed | Accuracy | Dependencies | Best Use Case |
|-----------|-------|----------|--------------|---------------|
| TextBlob | Medium | High | textblob | General sentiment |
| VADER | Fast | High | vaderSentiment | Social media text |
| Keyword | Very Fast | Medium | None | Quick analysis |
| N-gram | Medium | Medium-High | None | Context understanding |
| Rule-Based | Medium | Medium-High | None | Financial domain |
| FinBERT | Slow | Very High | transformers, torch | Financial news (best accuracy) |

## Tips for Comparison

1. **Run all 6 algorithms** on the same transcribed text files
2. **Compare sentiment scores** - do they agree or disagree?
3. **Check confidence levels** - which algorithm is more confident?
4. **Review sample contexts** - do the predictions make sense?
5. **Look for consensus** - when multiple algorithms agree, prediction is more reliable

## Notes

- All algorithms use the same company extraction logic
- All algorithms use the same prediction thresholds (>0.2 = POSITIVE, <-0.2 = NEGATIVE)
- Charts are optional (use `--no-chart` to skip)
- All algorithms are lightweight and suitable for MacBook Air M4

