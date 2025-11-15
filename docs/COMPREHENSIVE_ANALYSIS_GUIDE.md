# Comprehensive Stock Analysis Guide (Option 2B)

## Overview

This guide explains how to use the **Comprehensive Stock Analysis** system, which combines multiple sentiment models with AI-powered insights for stock prediction and trend analysis.

## How It Works

### Step 1: Model Data Collection
All sentiment analyzers run and extract:
- **Sentiment scores** from 8 different algorithms
- **Company mentions** (including US stocks like Nvidia, Valero, CME)
- **Financial indicators** (keywords, percentages, price mentions)
- **Trend signals** (bullish/bearish indicators)
- **Risk factors**

### Step 2: AI Analysis
The AI analyzes all model outputs and generates:
- **Growth probability** for each stock
- **Loss probability** assessments
- **Trend detection** (Strong Bullish, Bullish, Neutral, Bearish, Strong Bearish)
- **Key factors** influencing each stock
- **Market-wide trends**
- **Risk assessments**
- **Actionable recommendations** (BUY/CAUTION)

## Usage Steps

### Method 1: Command Line (Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Run comprehensive analysis
python run_comprehensive_analysis.py

# With custom directories
python run_comprehensive_analysis.py --text-dir downloads/text_files --output-dir downloads/analysis

# Include charts
python run_comprehensive_analysis.py --charts
```

### Method 2: Python Script

```python
from run_comprehensive_analysis import run_comprehensive_analysis

# Run analysis
result = run_comprehensive_analysis(
    text_files_dir='downloads/text_files',
    output_dir='downloads/analysis',
    create_charts=False
)

# Access results
comprehensive_data = result['comprehensive_data']
ai_insights = result['ai_insights']
```

### Method 3: Step-by-Step (Advanced)

```python
# Step 1: Run all models and extract data
from comprehensive_stock_analyzer import run_all_analyzers

comprehensive_data = run_all_analyzers(
    text_files_dir='downloads/text_files',
    output_dir='downloads/analysis',
    create_chart=False
)

# Step 2: Generate AI insights
from ai_insights_generator import generate_ai_insights

ai_insights = generate_ai_insights(
    comprehensive_data_file='downloads/analysis/comprehensive_analysis_data.json',
    output_file='downloads/analysis/ai_insights.json'
)
```

## Output Files

### 1. `comprehensive_analysis_data.json`
Contains all model outputs and extracted data:
```json
{
  "analysis_date": "2025-11-15T23:50:00",
  "source_files": ["video_transcribed.txt"],
  "model_outputs": {
    "textblob": {...},
    "vader": {...},
    "finbert": {...},
    ...
  },
  "extracted_data": {
    "video_transcribed.txt": {
      "companies_mentioned": {...},
      "financial_indicators": {...}
    }
  },
  "aggregated_companies": [
    {
      "company": "Nvidia",
      "sentiment_score": 0.75,
      "prediction": "POSITIVE",
      "confidence": 0.88,
      "total_mentions": 15
    }
  ],
  "summary": {
    "total_companies": 10,
    "positive": 6,
    "negative": 2,
    "neutral": 2
  }
}
```

### 2. `ai_insights.json`
Contains AI-generated insights and recommendations:
```json
{
  "generation_date": "2025-11-15T23:50:05",
  "overall_analysis": {
    "market_sentiment": "BULLISH",
    "total_companies_analyzed": 10,
    "bullish_ratio": 0.6
  },
  "company_insights": [
    {
      "company": "Nvidia",
      "sentiment_score": 0.75,
      "prediction": "POSITIVE",
      "trend": "STRONG_BULLISH",
      "growth_probability": 0.85,
      "loss_probability": 0.15,
      "key_factors": [
        "Positive: Beat",
        "Positive: Growth"
      ]
    }
  ],
  "market_trends": {
    "bullish_stocks": ["Nvidia", "Apple", "Microsoft"],
    "bearish_stocks": ["CompanyX"],
    "high_confidence_picks": ["Nvidia", "Apple"]
  },
  "risk_assessment": {
    "high_risk_stocks": [],
    "overall_risk_level": "LOW"
  },
  "recommendations": [
    {
      "type": "BUY",
      "company": "Nvidia",
      "reason": "Strong positive sentiment (0.75) with high confidence (0.88)",
      "growth_probability": 0.85
    }
  ],
  "summary_text": "..."
}
```

## Understanding the Results

### Sentiment Scores
- **Range**: -1.0 (very negative) to +1.0 (very positive)
- **> 0.2**: Positive sentiment
- **< -0.2**: Negative sentiment
- **-0.2 to 0.2**: Neutral sentiment

### Growth/Loss Probability
- **Growth Probability**: Likelihood of stock price increase (0.0 to 1.0)
- **Loss Probability**: Likelihood of stock price decrease (0.0 to 1.0)
- **> 0.7**: High probability
- **0.4-0.7**: Moderate probability
- **< 0.4**: Low probability

### Trends
- **STRONG_BULLISH**: Very positive sentiment (>0.3)
- **BULLISH**: Positive sentiment (0.1-0.3)
- **NEUTRAL**: Mixed sentiment (-0.1 to 0.1)
- **BEARISH**: Negative sentiment (-0.3 to -0.1)
- **STRONG_BEARISH**: Very negative sentiment (<-0.3)

### Confidence Scores
- **Range**: 0.0 to 1.0
- **> 0.7**: High confidence (reliable prediction)
- **0.4-0.7**: Moderate confidence
- **< 0.4**: Low confidence (less reliable)

## Integration with Existing Workflow

The comprehensive analysis can be integrated into your existing pipeline:

### Option A: After Transcription
```python
from youtube_audio_downloader import download_from_list
from run_comprehensive_analysis import run_comprehensive_analysis

# Download and transcribe
download_from_list(
    video_urls=['https://youtube.com/watch?v=...'],
    past_hours=1,
    auto_transcribe=True
)

# Run comprehensive analysis
run_comprehensive_analysis()
```

### Option B: Standalone Analysis
```python
# If you already have transcribed files
from run_comprehensive_analysis import run_comprehensive_analysis

run_comprehensive_analysis(
    text_files_dir='downloads/text_files',
    output_dir='downloads/analysis'
)
```

## Supported Stocks

The system detects:
- **Indian stocks**: Reliance, TCS, Infosys, HDFC, ICICI, SBI, Nifty, Sensex, etc.
- **US stocks**: Nvidia, Apple, Microsoft, Google, Amazon, Tesla, Valero, CME, etc.
- **Indices**: S&P 500, NASDAQ, Dow Jones, etc.
- **ETFs**: SPY, QQQ, VOO, etc.

## Tips for Best Results

1. **Use longer transcripts**: More text = better analysis
2. **Multiple videos**: Analyze multiple sources for better accuracy
3. **Check confidence scores**: Higher confidence = more reliable
4. **Review key factors**: Understand why predictions were made
5. **Compare with market data**: Use insights as one input, not the only source

## Troubleshooting

### No companies found
- Check if stock names are mentioned in the transcript
- The system looks for exact matches (case-insensitive)
- Add custom company names to `ENHANCED_COMPANIES` in `comprehensive_stock_analyzer.py`

### Low confidence scores
- More mentions = higher confidence
- Stronger sentiment = higher confidence
- Consider analyzing longer transcripts

### Missing model outputs
- Ensure all sentiment analyzers are installed
- Check error messages in console output
- Some models require additional dependencies (transformers, torch)

## Next Steps

After running comprehensive analysis:

1. **Review AI insights**: Check `ai_insights.json` for recommendations
2. **Analyze trends**: Look at market_trends section
3. **Assess risks**: Review risk_assessment
4. **Make decisions**: Use insights as one factor in your investment decisions

Remember: This is a tool to assist analysis, not a replacement for professional financial advice.

