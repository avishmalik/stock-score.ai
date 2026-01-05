# Stock Data & Trends Integration

## Overview

The ChatGPT prompt generation now includes:
1. **Real-time stock prices** from NSE India API
2. **Stock status** (UP/DOWN/FLAT) with price changes
3. **Company information** (market cap, industry, volume)
4. **Web search queries** for company trends and news

## What's New

### 1. Stock Data Fetcher Module (`src/core/stock_data_fetcher.py`)

**Features:**
- Maps company names to NSE symbols (e.g., "reliance" → "RELIANCE")
- Fetches real-time stock data from NSE India API
- Extracts price, volume, market cap, and company info
- Formats data for inclusion in prompts

**Key Functions:**
- `get_nse_symbol(company_name)` - Convert company name to NSE symbol
- `get_stock_data(company_name)` - Fetch stock data for a company
- `format_stock_info_for_prompt(stock_data)` - Format for ChatGPT prompt
- `get_company_trends_search_query(company_name, symbol)` - Generate web search query

### 2. Enhanced ChatGPT Prompt

**New Sections Added:**
- **CURRENT STOCK STATUS** for each company:
  - Stock Symbol (NSE)
  - Current Price (₹)
  - Change (₹ and %)
  - Day Range (High/Low)
  - Volume
  - Market Cap
  - Industry

- **WEB SEARCH QUERY FOR TRENDS**:
  - Pre-formatted search queries for each company
  - Example: "reliance (RELIANCE) stock news trends analysis India"

**Updated Instructions:**
- Emphasizes using provided stock data
- Instructs to verify stock prices via web search
- Guides to use search queries for trends and news

## Usage

### Automatic Integration

When you run:
```bash
python scripts/create_stock_report.py
```

The script will:
1. Load sentiment analysis results
2. **Fetch stock data** for each company mentioned
3. **Generate web search queries** for trends
4. Include all data in the ChatGPT prompt

### Example Output in ChatGPT Prompt

```
**RELIANCE**
- Consensus Sentiment Score: +0.750 (BULLISH)
- Analyzer Agreement: 85.7% (6/7 analyzers agree)
- Total Mentions: 12
- Analyzers Used: 7 different models
- Best Performing Model: FinBERT
- Sample Contexts:
  • "Reliance Industries reported strong quarterly earnings..."
  • "Reliance Jio's expansion plans are driving growth..."

**CURRENT STOCK STATUS:**
  📊 **Stock Symbol**: RELIANCE
  🏢 **Company**: Reliance Industries Ltd
  💰 **Current Price**: ₹2,450.50
  📈 **Change**: ₹+25.30 (+1.04%)
  🔓 **Open**: ₹2,425.20
  📊 **Day Range**: ₹2,420.00 - ₹2,455.00
  🔙 **Previous Close**: ₹2,425.20
  📦 **Volume**: 5.2M
  💎 **Market Cap**: ₹16.5T Cr
  🏭 **Industry**: Refineries

**WEB SEARCH QUERY FOR TRENDS**: "reliance (RELIANCE) stock news trends analysis India"
  (Use this query to search for recent news, earnings, analyst reports, and market trends)
```

## Company Symbol Mapping

The system includes mappings for **100+ major Indian companies**, including:

- **Major Companies**: Reliance, TCS, Infosys, HDFC Bank, ICICI Bank, SBI, Bharti Airtel, L&T, HCL, Wipro
- **Auto**: Maruti, Tata Motors, M&M, Bajaj Auto, Hero Motocorp
- **Banking**: HDFC Bank, ICICI Bank, SBI, Axis Bank, Kotak Bank
- **IT**: TCS, Infosys, Wipro, HCL, Tech Mahindra
- **Pharma**: Sun Pharma, Dr Reddy's, Cipla, Lupin
- **FMCG**: HUL, ITC, Nestle, Britannia, Dabur
- **And many more...**

## Error Handling

- **If stock data fetch fails**: Shows symbol but indicates data unavailable
- **If symbol not found**: Skips stock data but still includes sentiment analysis
- **Rate limiting**: Includes delays between API calls to avoid blocking

## Web Search Integration

For each company, ChatGPT is instructed to:
1. Use the provided search query to find:
   - Recent news and earnings reports
   - Analyst ratings and price targets
   - Market trends and sector performance
   - Breaking news and events

2. Cross-reference:
   - Sentiment analysis with actual stock performance
   - News with current price movements
   - Analyst opinions with sentiment scores

## Benefits

1. **Comprehensive Analysis**: Combines sentiment + stock data + trends
2. **Real-time Data**: Current stock prices and market status
3. **Actionable Insights**: Price targets can reference actual current prices
4. **Verification**: Stock data helps validate sentiment analysis
5. **Trend Awareness**: Search queries guide comprehensive research

## Testing

Test the stock data fetcher:
```bash
python src/core/stock_data_fetcher.py
```

Test with specific companies:
```bash
python -c "
from src.core.stock_data_fetcher import get_stock_data, format_stock_info_for_prompt
data = get_stock_data('reliance')
if data:
    print(format_stock_info_for_prompt(data))
"
```

## Notes

- **API Rate Limiting**: NSE API may have rate limits. The script includes delays between requests.
- **Symbol Mapping**: If a company isn't in the mapping, stock data won't be fetched but sentiment analysis still works.
- **Data Accuracy**: Stock prices are fetched in real-time but should be verified via web search for critical decisions.
- **Network Required**: Requires internet connection to fetch stock data.

## Future Enhancements

Potential improvements:
- Cache stock data to reduce API calls
- Add more company symbol mappings
- Integrate with additional data sources (BSE, financial APIs)
- Add historical price data
- Include technical indicators

