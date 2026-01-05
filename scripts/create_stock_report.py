#!/usr/bin/env python3
"""
Stock Analysis Report Generator
Combines sentiment analysis results into a concise report optimized for ChatGPT.
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.stock_data_fetcher import (
    get_stock_data,
    format_stock_info_for_prompt,
    get_company_trends_search_query,
    get_nse_symbol
)


def load_analysis_files(analysis_dir: Path) -> List[Dict[str, Any]]:
    """Load all JSON prediction files from analysis directory."""
    analysis_files = []
    for json_file in analysis_dir.glob("*_predictions.json"):
        if json_file.name == "stock_predictions.json":
            continue  # Skip aggregated file, we'll recreate it
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['source_file'] = json_file.name
                analysis_files.append(data)
        except Exception as e:
            print(f"⚠️  Warning: Could not load {json_file.name}: {e}")
    
    return analysis_files


def load_transcription(text_dir: Path) -> str:
    """Load the transcribed text file."""
    text_files = list(text_dir.glob("*_transcribed.txt"))
    if not text_files:
        return ""
    
    # Use the most recent transcription file
    text_file = max(text_files, key=lambda p: p.stat().st_mtime)
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  Warning: Could not load transcription: {e}")
        return ""


def aggregate_sentiment_scores(analysis_files: List[Dict]) -> Dict[str, Dict]:
    """
    Aggregate sentiment scores across all analyzers for each company.
    Returns a dict mapping company name to aggregated data.
    """
    company_data = defaultdict(lambda: {
        'sentiment_scores': [],
        'predictions': {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0},
        'confidences': [],
        'total_mentions': 0,
        'contexts': [],
        'algorithms': [],
        'likely_false_positive': False,
        'match_confidence': 1.0,
        'best_algorithm': None,
        'best_score': 0.0
    })
    
    for analysis in analysis_files:
        algorithm = analysis.get('algorithm', analysis.get('source_file', 'Unknown'))
        
        for company_info in analysis.get('companies', []):
            company = company_info['company']
            
            # Skip if flagged as likely false positive
            if company_info.get('likely_false_positive', False):
                company_data[company]['likely_false_positive'] = True
                company_data[company]['match_confidence'] = min(
                    company_data[company]['match_confidence'],
                    company_info.get('match_confidence', 1.0)
                )
                continue
            
            # Aggregate data
            sentiment = company_info.get('sentiment_score', 0)
            company_data[company]['sentiment_scores'].append(sentiment)
            company_data[company]['predictions'][company_info.get('prediction', 'NEUTRAL')] += 1
            company_data[company]['confidences'].append(company_info.get('confidence', 0))
            company_data[company]['total_mentions'] += company_info.get('total_mentions', 0)
            company_data[company]['algorithms'].append(algorithm)
            
            # Collect unique contexts (limit to 2 per company)
            contexts = company_info.get('sample_contexts', [])
            for ctx in contexts[:2]:
                if ctx not in company_data[company]['contexts']:
                    company_data[company]['contexts'].append(ctx)
                    if len(company_data[company]['contexts']) >= 2:
                        break
            
            # Track best algorithm/score
            if abs(sentiment) > abs(company_data[company]['best_score']):
                company_data[company]['best_score'] = sentiment
                company_data[company]['best_algorithm'] = algorithm
    
    return dict(company_data)


def calculate_consensus_score(company_info: Dict) -> float:
    """Calculate a consensus sentiment score from multiple analyzers."""
    if not company_info['sentiment_scores']:
        return 0.0
    
    # Weighted average by confidence
    total_weight = 0
    weighted_sum = 0
    
    for i, score in enumerate(company_info['sentiment_scores']):
        confidence = company_info['confidences'][i] if i < len(company_info['confidences']) else 0.5
        weighted_sum += score * confidence
        total_weight += confidence
    
    return weighted_sum / total_weight if total_weight > 0 else sum(company_info['sentiment_scores']) / len(company_info['sentiment_scores'])


def create_concise_report(
    company_data: Dict[str, Dict],
    transcription: str,
    analysis_files: List[Dict]
) -> str:
    """Create a concise, token-efficient report for ChatGPT."""
    
    # Filter out false positives and sort by consensus score
    valid_companies = {
        name: data for name, data in company_data.items()
        if not data['likely_false_positive'] and data['sentiment_scores']
    }
    
    # Calculate consensus scores
    for company, data in valid_companies.items():
        data['consensus_score'] = calculate_consensus_score(data)
        data['consensus_prediction'] = max(data['predictions'].items(), key=lambda x: x[1])[0]
        data['agreement'] = max(data['predictions'].values()) / sum(data['predictions'].values()) if sum(data['predictions'].values()) > 0 else 0
    
    # Sort by absolute consensus score (strongest sentiment first)
    sorted_companies = sorted(
        valid_companies.items(),
        key=lambda x: abs(x[1]['consensus_score']),
        reverse=True
    )
    
    # Build report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("STOCK SENTIMENT ANALYSIS REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Source: {len(analysis_files)} sentiment analyzers")
    report_lines.append(f"Companies Analyzed: {len(sorted_companies)}")
    report_lines.append("")
    
    # Summary statistics
    positive_count = sum(1 for _, d in sorted_companies if d['consensus_prediction'] == 'POSITIVE')
    negative_count = sum(1 for _, d in sorted_companies if d['consensus_prediction'] == 'NEGATIVE')
    neutral_count = sum(1 for _, d in sorted_companies if d['consensus_prediction'] == 'NEUTRAL')
    
    report_lines.append("SUMMARY:")
    report_lines.append(f"  • Positive Sentiment: {positive_count} companies")
    report_lines.append(f"  • Negative Sentiment: {negative_count} companies")
    report_lines.append(f"  • Neutral Sentiment: {neutral_count} companies")
    report_lines.append("")
    
    # Top companies by sentiment strength
    report_lines.append("TOP COMPANIES BY SENTIMENT STRENGTH:")
    report_lines.append("-" * 80)
    
    for i, (company, data) in enumerate(sorted_companies[:15], 1):  # Top 15 to save tokens
        consensus = data['consensus_score']
        prediction = data['consensus_prediction']
        agreement = data['agreement']
        mentions = data['total_mentions']
        
        # Create sentiment indicator
        if prediction == 'POSITIVE':
            indicator = "📈"
        elif prediction == 'NEGATIVE':
            indicator = "📉"
        else:
            indicator = "➡️"
        
        report_lines.append(f"{i}. {company.upper()} {indicator}")
        report_lines.append(f"   Consensus Score: {consensus:+.3f} ({prediction})")
        report_lines.append(f"   Analyzer Agreement: {agreement:.1%} ({max(data['predictions'].values())}/{sum(data['predictions'].values())} analyzers)")
        report_lines.append(f"   Total Mentions: {mentions}")
        
        # Add best context (most relevant quote)
        if data['contexts']:
            context = data['contexts'][0]
            # Truncate long contexts
            if len(context) > 150:
                context = context[:147] + "..."
            report_lines.append(f"   Key Quote: \"{context}\"")
        
        report_lines.append("")
    
    # Key insights (extract from transcription if available)
    if transcription:
        report_lines.append("KEY INSIGHTS FROM SOURCE MATERIAL:")
        report_lines.append("-" * 80)
        # Extract first 500 chars as summary
        summary = transcription[:500].replace('\n', ' ').strip()
        if len(transcription) > 500:
            summary += "..."
        report_lines.append(summary)
        report_lines.append("")
    
    # Analyzer methods used
    report_lines.append("ANALYSIS METHODS:")
    report_lines.append("-" * 80)
    unique_algorithms = set()
    for analysis in analysis_files:
        algo = analysis.get('algorithm', 'Unknown')
        desc = analysis.get('algorithm_description', '')
        if algo not in unique_algorithms:
            unique_algorithms.add(algo)
            report_lines.append(f"  • {algo}: {desc[:100] if desc else 'N/A'}")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)


def create_cursor_prompt(report: str) -> str:
    """Create cursor prompt - uses the stock analysis report directly."""
    # Simply return the report as the cursor prompt
    return report


def create_chatgpt_prompt(report: str, transcription: str, company_data: Dict[str, Dict]) -> str:
    """Create a detailed prompt for ChatGPT with full context."""
    
    # Build detailed company analysis section with stock data
    detailed_companies = []
    sorted_companies = sorted(
        [(name, data) for name, data in company_data.items() if not data.get('likely_false_positive', False) and data.get('sentiment_scores')],
        key=lambda x: abs(x[1].get('consensus_score', 0)),
        reverse=True
    )
    
    print("\n📊 Fetching stock data for companies...")
    stock_data_cache = {}
    
    for company, data in sorted_companies:
        consensus = data.get('consensus_score', 0)
        prediction = data.get('consensus_prediction', 'NEUTRAL')
        agreement = data.get('agreement', 0)
        mentions = data.get('total_mentions', 0)
        algorithms = len(set(data.get('algorithms', [])))
        best_algo = data.get('best_algorithm', 'N/A')
        
        # Fetch stock data
        stock_info = None
        nse_symbol = None
        if company not in stock_data_cache:
            try:
                stock_info = get_stock_data(company)
                if stock_info:
                    stock_data_cache[company] = stock_info
                    nse_symbol = stock_info.get('symbol')
                    print(f"  ✓ Fetched data for {company} ({nse_symbol})")
                else:
                    nse_symbol = get_nse_symbol(company)
                    stock_data_cache[company] = None
                    if nse_symbol:
                        print(f"  ⚠️  Could not fetch data for {company} (symbol: {nse_symbol})")
            except Exception as e:
                print(f"  ⚠️  Error fetching stock data for {company}: {e}")
                stock_data_cache[company] = None
        else:
            stock_info = stock_data_cache[company]
            if stock_info:
                nse_symbol = stock_info.get('symbol')
        
        # Build company section
        company_section = f"""
**{company.upper()}**
- Consensus Sentiment Score: {consensus:+.3f} ({prediction})
- Analyzer Agreement: {agreement:.1%} ({max(data['predictions'].values())}/{sum(data['predictions'].values())} analyzers agree)
- Total Mentions: {mentions}
- Analyzers Used: {algorithms} different models
- Best Performing Model: {best_algo}
- Sample Contexts:
{chr(10).join(f'  • "{ctx[:200]}..."' if len(ctx) > 200 else f'  • "{ctx}"' for ctx in data.get('contexts', [])[:2])}
"""
        
        # Add stock data if available
        if stock_info:
            company_section += "\n**CURRENT STOCK STATUS:**\n"
            company_section += format_stock_info_for_prompt(stock_info)
            company_section += "\n"
        elif nse_symbol:
            company_section += f"\n**STOCK SYMBOL**: {nse_symbol} (data fetch failed - please verify via web search)\n"
        
        # Add web search query for trends
        search_query = get_company_trends_search_query(company, nse_symbol)
        company_section += f"\n**WEB SEARCH QUERY FOR TRENDS**: \"{search_query}\"\n"
        company_section += "  (Use this query to search for recent news, earnings, analyst reports, and market trends)\n"
        
        detailed_companies.append(company_section)
    
    companies_section = "\n".join(detailed_companies)
    
    # Include full or large portion of transcription
    transcription_summary = transcription
    if len(transcription) > 10000:
        # If very long, include first 5000 and last 5000 chars
        transcription_summary = (
            transcription[:5000] + 
            "\n\n[... MIDDLE PORTION TRUNCATED FOR BREVITY ...]\n\n" + 
            transcription[-5000:]
        )
    
    prompt = f"""You are a senior financial analyst specializing in Indian stock market analysis with deep expertise in sentiment analysis, technical analysis, and fundamental research. You have access to web search capabilities to verify information and cross-reference data.

**CONTEXT:**
Below is a comprehensive sentiment analysis report generated from 7 different AI models analyzing recent Indian stock market news, discussions, and market commentary. The analysis includes multiple sentiment detection algorithms (FinBERT, TextBlob, VADER, Keyword-based, N-gram, Rule-based, and XLM-RoBERTa) to ensure robust and reliable insights.

**IMPORTANT INSTRUCTIONS:**
1. **Deep Analysis Required**: Analyze the sentiment data thoroughly, considering:
   - Consensus scores across multiple analyzers (higher agreement = more reliable)
   - Individual analyzer performance and confidence levels
   - Frequency of mentions (more mentions may indicate stronger market focus)
   - Context and quotes from source material

2. **Web Verification & Stock Data**: For each significant company recommendation:
   - **Stock Price & Status**: Current stock prices, price changes, and market data are provided below for each company. Verify these are current and accurate.
   - **Company Trends**: Use the provided web search queries to find recent news, earnings reports, analyst ratings, and market trends
   - **Cross-Reference**: Compare sentiment analysis with actual stock performance and market data
   - **Breaking News**: Check for any recent events, earnings announcements, or regulatory changes that might affect recommendations
   - **Analyst Coverage**: Verify analyst ratings, price targets, and recommendations from financial institutions
   - **Market Context**: Consider sector performance, market trends, and macroeconomic factors

3. **Comprehensive Recommendations**: Provide detailed, actionable recommendations including:
   - Entry prices and stop-loss levels
   - Target prices with time horizons (short-term: 1-3 months, medium-term: 3-12 months)
   - Risk-reward ratios
   - Position sizing suggestions
   - Market conditions that would invalidate the recommendation

4. **Risk Assessment**: For each recommendation, clearly identify:
   - Company-specific risks
   - Sector risks
   - Market-wide risks
   - Liquidity concerns
   - Volatility expectations

5. **Market Context**: Consider:
   - Overall market sentiment and trends
   - Sector rotation patterns
   - Macroeconomic factors affecting Indian markets
   - Global market influences
   - Policy and regulatory changes

**SENTIMENT ANALYSIS REPORT:**

{report}

**DETAILED COMPANY ANALYSIS:**

{companies_section}

**FULL SOURCE TRANSCRIPTION:**

Below is the complete transcription of the market news/discussion that was analyzed:

---
{transcription_summary}
---

**YOUR COMPREHENSIVE TASK:**

Based on the sentiment analysis, detailed company data, and full source material above, provide a comprehensive stock market analysis:

1. **EXECUTIVE SUMMARY** (2-3 paragraphs)
   - Overall market sentiment assessment
   - Key themes and trends identified
   - Market outlook (bullish/bearish/neutral with reasoning)

2. **TOP 5 BUY RECOMMENDATIONS** (Detailed for each)
   - Company name and ticker symbol (NSE symbol provided in stock data)
   - **Current Stock Status**: Use the provided stock price, change %, and market data. Compare with current market prices via web search to ensure accuracy.
   - **Company Trends**: Use the provided web search query to find recent news, earnings, analyst reports, and market trends. Summarize key findings.
   - Entry strategy (price levels, timing) - reference current price from stock data
   - Target prices (short-term and medium-term) - calculate based on current price
   - Stop-loss levels - calculate based on current price and volatility
   - Risk-reward ratio
   - Position sizing recommendation
   - Key catalysts and reasoning (from web search results)
   - Risk factors specific to this stock
   - Time horizon for the trade/investment

3. **TOP 3 AVOID/SELL RECOMMENDATIONS** (Detailed for each)
   - Company name and reasoning
   - Current concerns and red flags
   - If holding, exit strategy
   - If shorting, entry strategy and targets
   - Risk factors

4. **SECTOR ANALYSIS**
   - Best performing sectors (based on sentiment)
   - Sectors to avoid
   - Sector rotation opportunities

5. **MARKET OUTLOOK & STRATEGY**
   - Overall market direction (Nifty/Sensex outlook)
   - Key support and resistance levels (if identifiable)
   - Market conditions that would change your view
   - Portfolio allocation suggestions

6. **RISK FACTORS & WARNINGS**
   - Market-wide risks
   - Sector-specific risks
   - Geopolitical/economic risks
   - Volatility expectations

7. **VERIFICATION NOTES**
   - Discrepancies found between sentiment analysis and actual news/data
   - Companies where sentiment may be misleading
   - Additional research needed for specific stocks
   - Data quality concerns (if any)

8. **FOLLOW-UP RESEARCH SUGGESTIONS**
   - Companies that need deeper fundamental analysis
   - Earnings reports to watch
   - Events and announcements to monitor

**FORMATTING REQUIREMENTS:**
- Use clear sections with headers
- Use bullet points for easy scanning
- Include emojis/spacing for visual clarity (📈 for buys, 📉 for sells, ⚠️ for risks)
- Provide specific numbers and percentages where possible
- Include confidence levels for each recommendation (High/Medium/Low)

**IMPORTANT DISCLAIMERS TO INCLUDE:**
- This analysis is based on sentiment analysis and should be combined with fundamental and technical analysis
- Past performance does not guarantee future results
- Always do your own research and consult with financial advisors
- Sentiment analysis is one tool among many - use it as part of a comprehensive investment strategy
- Market conditions can change rapidly - monitor positions regularly

Please provide a comprehensive, detailed analysis that an investor can use to make informed decisions."""
    
    return prompt


def save_report_files(
    report: str,
    cursor_prompt: str,
    chatgpt_prompt: str,
    output_dir: Path,
    company_data: Dict[str, Dict]
):
    """Save the report and prompts to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save concise report
    report_file = output_dir / "stock_analysis_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")
    
    # Save Cursor prompt (token-optimized)
    cursor_file = output_dir / "cursor_prompt.txt"
    with open(cursor_file, 'w', encoding='utf-8') as f:
        f.write(cursor_prompt)
    print(f"✓ Cursor prompt saved to: {cursor_file}")
    
    # Save ChatGPT prompt (detailed)
    chatgpt_file = output_dir / "chatgpt_prompt.txt"
    with open(chatgpt_file, 'w', encoding='utf-8') as f:
        f.write(chatgpt_prompt)
    print(f"✓ ChatGPT prompt saved to: {chatgpt_file}")
    
    # Save structured JSON for programmatic use
    json_data = {
        'generated_at': datetime.now().isoformat(),
        'total_companies': len(company_data),
        'companies': []
    }
    
    for company, data in sorted(
        company_data.items(),
        key=lambda x: abs(x[1].get('consensus_score', 0)),
        reverse=True
    ):
        if not data.get('likely_false_positive', False):
            json_data['companies'].append({
                'company': company,
                'consensus_score': round(data.get('consensus_score', 0), 3),
                'consensus_prediction': data.get('consensus_prediction', 'NEUTRAL'),
                'agreement': round(data.get('agreement', 0), 3),
                'total_mentions': data['total_mentions'],
                'algorithms_used': len(set(data['algorithms'])),
                'best_algorithm': data.get('best_algorithm'),
                'sample_contexts': data['contexts'][:2]
            })
    
    json_file = output_dir / "stock_analysis_summary.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"✓ JSON summary saved to: {json_file}")
    
    # Print token estimates
    report_tokens = len(report.split()) * 1.3
    cursor_tokens = len(cursor_prompt.split()) * 1.3
    chatgpt_tokens = len(chatgpt_prompt.split()) * 1.3
    print(f"\n📊 Token Estimates:")
    print(f"   Report: ~{int(report_tokens)} tokens")
    print(f"   Cursor Prompt: ~{int(cursor_tokens)} tokens (optimized)")
    print(f"   ChatGPT Prompt: ~{int(chatgpt_tokens)} tokens (detailed)")


def create_stock_report(
    analysis_dir: str = "downloads/analysis",
    text_dir: str = "downloads/text_files",
    output_dir: str = "downloads/reports"
):
    """
    Main function to create a combined stock analysis report.
    
    Args:
        analysis_dir: Directory containing JSON prediction files
        text_dir: Directory containing transcribed text files
        output_dir: Directory to save the generated report
    """
    print("🔍 Loading analysis files...")
    analysis_path = Path(analysis_dir)
    text_path = Path(text_dir)
    output_path = Path(output_dir)
    
    if not analysis_path.exists():
        print(f"❌ Error: Analysis directory not found: {analysis_dir}")
        return
    
    # Load data
    analysis_files = load_analysis_files(analysis_path)
    if not analysis_files:
        print("❌ Error: No analysis files found!")
        return
    
    transcription = load_transcription(text_path)
    
    print(f"✓ Loaded {len(analysis_files)} analysis files")
    if transcription:
        print(f"✓ Loaded transcription ({len(transcription)} chars)")
    
    # Aggregate sentiment scores
    print("\n📊 Aggregating sentiment scores...")
    company_data = aggregate_sentiment_scores(analysis_files)
    print(f"✓ Found {len(company_data)} companies")
    
    # Create report
    print("\n📝 Generating report...")
    report = create_concise_report(company_data, transcription, analysis_files)
    
    # Create both prompts
    print("📝 Creating prompts...")
    cursor_prompt = create_cursor_prompt(report)
    chatgpt_prompt = create_chatgpt_prompt(report, transcription, company_data)
    
    # Save files
    print("\n💾 Saving files...")
    save_report_files(report, cursor_prompt, chatgpt_prompt, output_path, company_data)
    
    print("\n✅ Report generation complete!")
    print(f"\n📋 Next Steps:")
    print(f"\n   For Cursor (Composer AI) - Token Optimized:")
    print(f"   1. Open: {output_path / 'cursor_prompt.txt'}")
    print(f"   2. Copy and paste into Cursor chat")
    print(f"   3. Get concise, actionable recommendations")
    print(f"\n   For ChatGPT - Detailed Analysis:")
    print(f"   1. Open: {output_path / 'chatgpt_prompt.txt'}")
    print(f"   2. Copy the entire prompt")
    print(f"   3. Paste it into ChatGPT")
    print(f"   4. Get comprehensive analysis with full context")
    print(f"\n💡 Tip: Use Cursor prompt for quick insights, ChatGPT prompt for deep analysis")


if __name__ == "__main__":
    import sys
    
    # Allow custom paths via command line
    analysis_dir = sys.argv[1] if len(sys.argv) > 1 else "downloads/analysis"
    text_dir = sys.argv[2] if len(sys.argv) > 2 else "downloads/text_files"
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "downloads/reports"
    
    create_stock_report(analysis_dir, text_dir, output_dir)

