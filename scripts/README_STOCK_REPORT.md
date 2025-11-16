# Stock Analysis Report Generator

This script combines sentiment analysis results from multiple AI models into a concise, token-efficient report optimized for ChatGPT and other AI assistants.

## Purpose

After running sentiment analysis on transcribed market news/videos, this script:
1. Aggregates sentiment scores across all analyzers
2. Filters out false positives
3. Creates a concise report with key insights
4. Generates a ChatGPT-optimized prompt for stock recommendations
5. Includes web verification instructions for accuracy

## Files Generated

The script creates four files in `downloads/reports/`:

1. **`stock_analysis_report.txt`** - Human-readable summary report
2. **`cursor_prompt.txt`** - Token-optimized prompt for Cursor (Composer AI) - ~180 tokens
3. **`chatgpt_prompt.txt`** - Detailed prompt for ChatGPT with full context - ~6,000+ tokens
4. **`stock_analysis_summary.json`** - Structured JSON data for programmatic use

## How to Run

### Basic Usage

```bash
# From project root directory
python scripts/create_stock_report.py
```

This will:
- Read all `*_predictions.json` files from `downloads/analysis/`
- Read transcribed text from `downloads/text_files/`
- Generate reports in `downloads/reports/`

### Custom Paths

You can specify custom directories:

```bash
python scripts/create_stock_report.py [analysis_dir] [text_dir] [output_dir]
```

Example:
```bash
python scripts/create_stock_report.py downloads/analysis downloads/text_files downloads/reports
```

### Using Virtual Environment

```bash
# Activate virtual environment first
source venv/bin/activate

# Then run the script
python scripts/create_stock_report.py
```

## Step-by-Step Instructions

### Step 1: Ensure Analysis Files Exist

Make sure you have:
- Sentiment analysis JSON files in `downloads/analysis/` (e.g., `sentiment_finbert_predictions.json`, `sentiment_textblob_predictions.json`, etc.)
- At least one transcribed text file in `downloads/text_files/` (ending with `_transcribed.txt`)

### Step 2: Run the Report Generator

```bash
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate  # If using virtual environment
python scripts/create_stock_report.py
```

### Step 3: Get Stock Recommendations

#### Option A: For Cursor (Composer AI) - Quick Analysis

1. **Open the Cursor prompt:**
   ```bash
   open downloads/reports/cursor_prompt.txt
   ```

2. **Copy the entire contents** and paste into Cursor chat

3. **Get concise recommendations** (~500 words, token-optimized)

**Best for:** Quick insights, token-efficient analysis, rapid decision-making

#### Option B: For ChatGPT - Comprehensive Analysis

1. **Open the ChatGPT prompt:**
   ```bash
   open downloads/reports/chatgpt_prompt.txt
   ```

2. **Copy the entire contents** and paste into ChatGPT

3. **Get detailed analysis** including:
   - Full source transcription context
   - Detailed company-by-company analysis
   - Entry/exit strategies with price targets
   - Risk assessments and position sizing
   - Market outlook and sector analysis
   - Web verification instructions

**Best for:** Deep analysis, comprehensive research, detailed investment decisions

### Step 4: Review Results

The AI will provide:
- **Top 5 Buy Recommendations** (with reasoning)
- **Top 3 Avoid/Sell Recommendations**
- **Market Outlook Summary**
- **Risk Factors**
- **Verification Notes** (discrepancies between sentiment and news)

## What the Script Does

### 1. Data Aggregation
- Combines sentiment scores from all analyzers (FinBERT, TextBlob, VADER, etc.)
- Calculates consensus scores weighted by confidence
- Filters out companies flagged as false positives

### 2. Report Generation
- Creates a concise summary (top 15 companies by sentiment strength)
- Includes analyzer agreement percentages
- Adds key quotes/contexts from source material

### 3. Dual Prompt Generation

#### Cursor Prompt (Token-Optimized)
- Includes only essential data (summary + top 10 companies)
- Requests concise recommendations (~500 words)
- Optimized for quick analysis in Cursor
- ~180 tokens total

#### ChatGPT Prompt (Detailed)
- Includes full sentiment analysis report
- Detailed company-by-company breakdown with all metrics
- **Complete source transcription** (full text file content)
- Comprehensive instructions for web verification
- Requests detailed recommendations with price targets, risk assessments
- ~6,000+ tokens (no token limit concerns)

## Output Format

The generated report includes:

```
STOCK SENTIMENT ANALYSIS REPORT
================================================================================
Generated: 2025-11-16 21:33:33
Source: 7 sentiment analyzers
Companies Analyzed: 17

SUMMARY:
  • Positive Sentiment: X companies
  • Negative Sentiment: Y companies
  • Neutral Sentiment: Z companies

TOP COMPANIES BY SENTIMENT STRENGTH:
--------------------------------------------------------------------------------
1. COMPANY_NAME 📈
   Consensus Score: +0.901 (POSITIVE)
   Analyzer Agreement: 85.7% (6/7 analyzers)
   Total Mentions: 5
   Key Quote: "..."

[More companies...]

KEY INSIGHTS FROM SOURCE MATERIAL:
--------------------------------------------------------------------------------
[Summary of transcribed content]

ANALYSIS METHODS:
--------------------------------------------------------------------------------
  • FinBERT: BERT model fine-tuned on financial news...
  • TextBlob: Pattern analysis and word polarity...
  [etc.]
```

## Token Efficiency

The script generates two prompts with different token counts:

### Cursor Prompt (Token-Optimized)
- **Size**: ~180 tokens
- **Content**: Summary + top 10 companies only
- **Purpose**: Quick analysis in Cursor without token concerns
- **Best for**: Rapid insights, iterative refinement

### ChatGPT Prompt (Detailed)
- **Size**: ~6,000+ tokens
- **Content**: Full report + detailed company analysis + complete transcription
- **Purpose**: Comprehensive analysis with full context
- **Best for**: Deep research, detailed recommendations

### Report File
- **Size**: ~1,200 tokens
- **Content**: Human-readable summary
- **Purpose**: Quick reference, manual review

## Troubleshooting

### Error: "No analysis files found"
- Ensure you've run the sentiment analyzers first: `python scripts/run_all_analyzers.py`
- Check that JSON files exist in `downloads/analysis/`

### Error: "No transcription found"
- Make sure transcribed text files exist in `downloads/text_files/`
- Files should end with `_transcribed.txt`

### Empty Report
- Check that analysis files contain company data
- Verify companies aren't all flagged as false positives

## Integration with Analysis Pipeline

This script is designed to work after running the full analysis pipeline:

```bash
# 1. Download and transcribe video
python src/web/app.py  # Use web interface or API

# 2. Run sentiment analyzers
python scripts/run_all_analyzers.py --text-dir downloads/text_files --output-dir downloads/analysis

# 3. Generate combined report
python scripts/create_stock_report.py

# 4. Use report with ChatGPT
# Open downloads/reports/chatgpt_prompt.txt and paste into ChatGPT
```

## Customization

You can modify the script to:
- Change the number of top companies shown (currently 15)
- Adjust token limits
- Modify the prompt template
- Add additional analysis metrics

Edit `scripts/create_stock_report.py` to customize.

## Notes

- The script automatically filters out false positives (companies with `likely_false_positive: true`)
- Consensus scores are weighted by analyzer confidence
- Companies are sorted by absolute sentiment strength
- The prompt includes instructions for web verification to ensure accuracy

