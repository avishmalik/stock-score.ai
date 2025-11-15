#!/usr/bin/env python3
"""
Stock Sentiment Analyzer
Analyzes transcribed text files to extract company mentions, analyze sentiment,
and predict stock performance. Uses lightweight local libraries.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for MacBook Air
import matplotlib.pyplot as plt
from datetime import datetime

# Try to import sentiment analysis libraries (lightweight)
HAS_TEXTBLOB = False
HAS_VADER = False

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        HAS_VADER = True
    except ImportError:
        pass


# Import centralized company registry
try:
    from src.core.company_registry import COMMON_COMPANIES
except ImportError:
    try:
        from core.company_registry import COMMON_COMPANIES
    except ImportError:
        # Fallback to basic list if registry not available
        COMMON_COMPANIES = {
            'reliance', 'tcs', 'infosys', 'hdfc', 'icici', 'sbi', 'bharti', 'lt', 'hcl', 'wipro',
            'maruti', 'tata', 'adani', 'jsw', 'vedanta', 'hindalco', 'tata motors', 'm&m', 'mm', 'mahindra',
            'dlf', 'grasim', 'ultratech', 'ambuja', 'shree cement', 'dabur', 'hul', 'itc',
            'asian paints', 'berger paints', 'nippon', 'indigo', 'spicejet', 'airtel', 'jio',
            'lic', 'sbi bank', 'hdfc bank', 'icici bank', 'axis bank', 'kotak', 'pnb', 'rbl bank',
            'nifty', 'sensex', 'bank nifty', 'nifty 50', 'nifty bank',
            'tata steel', 'jsw steel', 'sail', 'coal india', 'ongc', 'ioc', 'bpcl', 'hpcl',
            'zomato', 'nykaa', 'paytm', 'policybazaar', 'delhivery',
            'lupin', 'dr reddy', 'sun pharma', 'cipla', 'torrent', 'mankind', 'glenmark', 'mankind pharma',
            'nhpc', 'power grid', 'ntpc', 'suzlon', 'adani green', 'tata power',
            'upl', 'coromandel', 'rallis', 'pi industries',
            'mcx', 'nse', 'bse', 'ncdx'
        }

# Financial keywords that indicate positive/negative sentiment
POSITIVE_KEYWORDS = [
    'buy', 'bullish', 'positive', 'growth', 'profit', 'gain', 'rise', 'up', 'strong',
    'good', 'excellent', 'outperform', 'target', 'recommend', 'upgrade', 'beat',
    'surprise', 'better', 'increase', 'higher', 'rally', 'momentum', 'breakout'
]

NEGATIVE_KEYWORDS = [
    'sell', 'bearish', 'negative', 'loss', 'fall', 'down', 'weak', 'bad', 'poor',
    'underperform', 'downgrade', 'miss', 'decline', 'lower', 'drop', 'crash',
    'correction', 'concern', 'risk', 'worry', 'trouble', 'problem'
]


def get_sentiment_analyzer():
    """Get available sentiment analyzer."""
    if HAS_TEXTBLOB:
        return 'textblob'
    elif HAS_VADER:
        return SentimentIntensityAnalyzer()
    else:
        return None


def analyze_sentiment_textblob(text: str) -> float:
    """Analyze sentiment using TextBlob (returns -1 to 1)."""
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except LookupError:
        # NLTK data not downloaded - download it automatically
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('brown', quiet=True)
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            # Fallback to simple analysis if download fails
            return analyze_sentiment_simple(text)


def analyze_sentiment_vader(text: str, analyzer) -> float:
    """Analyze sentiment using VADER (returns -1 to 1)."""
    scores = analyzer.polarity_scores(text)
    # Compound score ranges from -1 to 1
    return scores['compound']


def analyze_sentiment_simple(text: str) -> float:
    """Simple keyword-based sentiment analysis (fallback)."""
    text_lower = text.lower()
    positive_count = sum(1 for word in POSITIVE_KEYWORDS if word in text_lower)
    negative_count = sum(1 for word in NEGATIVE_KEYWORDS if word in text_lower)
    
    total = positive_count + negative_count
    if total == 0:
        return 0.0
    
    # Normalize to -1 to 1 range
    sentiment = (positive_count - negative_count) / total
    return sentiment


def extract_company_mentions(text: str) -> Dict[str, List[str]]:
    """
    Extract company mentions and surrounding context.
    Returns dict mapping company names to list of context sentences.
    """
    text_lower = text.lower()
    company_mentions = defaultdict(list)
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        # Check for each company
        for company in COMMON_COMPANIES:
            # Look for company name in sentence (word boundary matching)
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, sentence_lower):
                # Clean up sentence
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 10:  # Only keep meaningful sentences
                    company_mentions[company].append(clean_sentence)
    
    return company_mentions


def analyze_company_sentiment(
    company: str,
    contexts: List[str],
    analyzer
) -> Dict:
    """Analyze sentiment for a specific company."""
    if not contexts:
        return {
            'company': company,
            'sentiment_score': 0.0,
            'mentions': 0,
            'prediction': 'NEUTRAL',
            'confidence': 0.0
        }
    
    # Combine all contexts for this company
    combined_text = ' '.join(contexts)
    
    # Get sentiment score
    if analyzer == 'textblob':
        sentiment_score = analyze_sentiment_textblob(combined_text)
    elif HAS_VADER and hasattr(analyzer, 'polarity_scores'):
        # VADER analyzer object
        sentiment_score = analyze_sentiment_vader(combined_text, analyzer)
    else:
        # Fallback to simple keyword-based
        sentiment_score = analyze_sentiment_simple(combined_text)
    
    # Count mentions
    mention_count = len(contexts)
    
    # Determine prediction
    if sentiment_score > 0.2:
        prediction = 'POSITIVE'
    elif sentiment_score < -0.2:
        prediction = 'NEGATIVE'
    else:
        prediction = 'NEUTRAL'
    
    # Calculate confidence (based on sentiment strength and mention count)
    confidence = min(abs(sentiment_score) * (1 + min(mention_count / 10, 0.5)), 1.0)
    
    return {
        'company': company.title(),
        'sentiment_score': round(sentiment_score, 3),
        'mentions': mention_count,
        'prediction': prediction,
        'confidence': round(confidence, 3),
        'contexts': contexts[:3]  # Store first 3 contexts as examples
    }


def analyze_text_file(text_file_path: str) -> Dict:
    """Analyze a single transcribed text file."""
    try:
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"✗ Error reading {text_file_path}: {e}")
        return None
    
    if not text or len(text.strip()) < 50:
        print(f"⚠ Skipping {text_file_path}: Text too short or empty")
        return None
    
    print(f"Analyzing: {Path(text_file_path).name}")
    
    # Get sentiment analyzer
    analyzer = get_sentiment_analyzer()
    if analyzer is None:
        print("⚠ No sentiment library found. Using simple keyword-based analysis.")
        print("  Install: pip install textblob (recommended) or pip install vaderSentiment")
    
    # Extract company mentions
    company_mentions = extract_company_mentions(text)
    
    if not company_mentions:
        print("  No company mentions found")
        return None
    
    print(f"  Found {len(company_mentions)} companies mentioned")
    
    # Analyze sentiment for each company
    results = []
    for company, contexts in company_mentions.items():
        analysis = analyze_company_sentiment(company, contexts, analyzer)
        results.append(analysis)
    
    # Sort by confidence (most confident predictions first)
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        'source_file': Path(text_file_path).name,
        'analysis_date': datetime.now().isoformat(),
        'total_companies': len(results),
        'companies': results
    }


def create_performance_chart(results: Dict, output_path: str):
    """Create a chart showing predicted performance."""
    companies = results.get('companies', [])
    if not companies:
        print("No data to plot")
        return
    
    # Get top 15 companies by confidence
    top_companies = companies[:15]
    
    company_names = [c['company'] for c in top_companies]
    sentiment_scores = [c['sentiment_score'] for c in top_companies]
    colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' for s in sentiment_scores]
    
    # Create figure
    plt.figure(figsize=(12, 8))
    bars = plt.barh(company_names, sentiment_scores, color=colors, alpha=0.7)
    
    plt.xlabel('Sentiment Score', fontsize=12)
    plt.ylabel('Company', fontsize=12)
    plt.title('Stock Performance Prediction (Based on Sentiment Analysis)', fontsize=14, fontweight='bold')
    plt.axvline(x=0, color='black', linestyle='--', linewidth=0.5)
    plt.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, score) in enumerate(zip(bars, sentiment_scores)):
        width = bar.get_width()
        label_x = width + (0.05 if width >= 0 else -0.05)
        plt.text(label_x, bar.get_y() + bar.get_height()/2, 
                f'{score:.2f}', ha='left' if width >= 0 else 'right', 
                va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Chart saved to: {output_path}")


def analyze_transcriptions(
    text_files_dir: str = 'downloads/text_files',
    output_dir: str = 'downloads/analysis',
    create_chart: bool = True
) -> Dict:
    """
    Analyze all transcribed text files and generate predictions.
    
    Args:
        text_files_dir: Directory containing transcribed text files
        output_dir: Directory to save analysis results
        create_chart: Whether to create visualization charts
    
    Returns:
        Combined analysis results
    """
    text_dir = Path(text_files_dir)
    if not text_dir.exists():
        print(f"✗ Directory not found: {text_files_dir}")
        return None
    
    # Find all text files
    text_files = list(text_dir.glob('*_transcribed.txt'))
    
    if not text_files:
        print(f"No transcribed text files found in {text_files_dir}")
        return None
    
    print(f"Found {len(text_files)} transcribed file(s)\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Analyze each file
    all_results = []
    for text_file in text_files:
        result = analyze_text_file(str(text_file))
        if result:
            all_results.append(result)
        print()
    
    if not all_results:
        print("No analysis results generated")
        return None
    
    # Combine results from all files
    combined_companies = defaultdict(lambda: {
        'sentiment_scores': [],
        'mentions': 0,
        'contexts': []
    })
    
    for result in all_results:
        for company_data in result.get('companies', []):
            company = company_data['company']
            combined_companies[company]['sentiment_scores'].append(company_data['sentiment_score'])
            combined_companies[company]['mentions'] += company_data['mentions']
            combined_companies[company]['contexts'].extend(company_data.get('contexts', []))
    
    # Calculate aggregated scores
    final_results = []
    for company, data in combined_companies.items():
        avg_sentiment = sum(data['sentiment_scores']) / len(data['sentiment_scores'])
        
        if avg_sentiment > 0.2:
            prediction = 'POSITIVE'
        elif avg_sentiment < -0.2:
            prediction = 'NEGATIVE'
        else:
            prediction = 'NEUTRAL'
        
        confidence = min(abs(avg_sentiment) * (1 + min(data['mentions'] / 10, 0.5)), 1.0)
        
        final_results.append({
            'company': company,
            'sentiment_score': round(avg_sentiment, 3),
            'total_mentions': data['mentions'],
            'prediction': prediction,
            'confidence': round(confidence, 3),
            'sample_contexts': data['contexts'][:2]  # Store 2 sample contexts
        })
    
    # Sort by confidence
    final_results.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Create final output
    output = {
        'analysis_date': datetime.now().isoformat(),
        'source_files': [r['source_file'] for r in all_results],
        'total_companies_analyzed': len(final_results),
        'companies': final_results,
        'summary': {
            'positive': sum(1 for c in final_results if c['prediction'] == 'POSITIVE'),
            'negative': sum(1 for c in final_results if c['prediction'] == 'NEGATIVE'),
            'neutral': sum(1 for c in final_results if c['prediction'] == 'NEUTRAL')
        }
    }
    
    # Save JSON output
    json_path = os.path.join(output_dir, 'stock_predictions.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Analysis saved to: {json_path}")
    
    # Create chart
    if create_chart:
        chart_path = os.path.join(output_dir, 'stock_performance_chart.png')
        create_performance_chart(output, chart_path)
    
    # Print summary
    print("\n" + "="*60)
    print("Analysis Summary:")
    print(f"  Total companies analyzed: {output['total_companies_analyzed']}")
    print(f"  Positive predictions: {output['summary']['positive']}")
    print(f"  Negative predictions: {output['summary']['negative']}")
    print(f"  Neutral predictions: {output['summary']['neutral']}")
    print("\nTop 5 Predictions:")
    for i, company in enumerate(final_results[:5], 1):
        print(f"  {i}. {company['company']}: {company['prediction']} "
              f"(Score: {company['sentiment_score']}, Confidence: {company['confidence']})")
    print("="*60)
    
    return output


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze stock sentiment from transcribed text files')
    parser.add_argument(
        '--text-dir',
        default='downloads/text_files',
        help='Directory containing transcribed text files (default: downloads/text_files)'
    )
    parser.add_argument(
        '--output-dir',
        default='downloads/analysis',
        help='Directory to save analysis results (default: downloads/analysis)'
    )
    parser.add_argument(
        '--no-chart',
        action='store_true',
        help='Skip creating performance chart'
    )
    
    args = parser.parse_args()
    
    # Check for sentiment libraries
    if not HAS_TEXTBLOB and not HAS_VADER:
        print("⚠ Warning: No sentiment analysis library found!")
        print("  Install one for better accuracy:")
        print("    pip install textblob (recommended)")
        print("    or")
        print("    pip install vaderSentiment")
        print("  Continuing with simple keyword-based analysis...\n")
    
    # Run analysis
    results = analyze_transcriptions(
        text_files_dir=args.text_dir,
        output_dir=args.output_dir,
        create_chart=not args.no_chart
    )
    
    if results:
        print(f"\n✓ Analysis complete! Results saved to: {args.output_dir}")


if __name__ == '__main__':
    main()

