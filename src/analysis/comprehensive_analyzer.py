#!/usr/bin/env python3
"""
Comprehensive Stock Analyzer
Runs all sentiment models and extracts comprehensive data for AI analysis.
This module collects all necessary data from multiple models and prepares it
for AI insights generation.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime

# Import all sentiment analyzers
try:
    from src.analyzers.base import analyze_transcriptions as analyze_base
except ImportError:
    try:
        from analyzers.base import analyze_transcriptions as analyze_base
    except ImportError:
        analyze_base = None

try:
    from src.analyzers.sentiment_analyzer_textblob import analyze_transcriptions as analyze_textblob
except ImportError:
    try:
        from analyzers.sentiment_analyzer_textblob import analyze_transcriptions as analyze_textblob
    except ImportError:
        analyze_textblob = None

try:
    from src.analyzers.sentiment_analyzer_vader import analyze_transcriptions as analyze_vader
except ImportError:
    try:
        from analyzers.sentiment_analyzer_vader import analyze_transcriptions as analyze_vader
    except ImportError:
        analyze_vader = None

try:
    from src.analyzers.sentiment_analyzer_keyword import analyze_transcriptions as analyze_keyword
except ImportError:
    try:
        from analyzers.sentiment_analyzer_keyword import analyze_transcriptions as analyze_keyword
    except ImportError:
        analyze_keyword = None

try:
    from src.analyzers.sentiment_analyzer_ngram import analyze_transcriptions as analyze_ngram
except ImportError:
    try:
        from analyzers.sentiment_analyzer_ngram import analyze_transcriptions as analyze_ngram
    except ImportError:
        analyze_ngram = None

try:
    from src.analyzers.sentiment_analyzer_rulebased import analyze_transcriptions as analyze_rulebased
except ImportError:
    try:
        from analyzers.sentiment_analyzer_rulebased import analyze_transcriptions as analyze_rulebased
    except ImportError:
        analyze_rulebased = None

try:
    from src.analyzers.sentiment_analyzer_finbert import analyze_transcriptions as analyze_finbert
except ImportError:
    try:
        from analyzers.sentiment_analyzer_finbert import analyze_transcriptions as analyze_finbert
    except ImportError:
        analyze_finbert = None

try:
    from src.analyzers.hindi import analyze_hindi_transcriptions as analyze_hindi
except ImportError:
    try:
        from analyzers.hindi import analyze_hindi_transcriptions as analyze_hindi
    except ImportError:
        analyze_hindi = None

# Import centralized company registry
try:
    from src.core.company_registry import ALL_INDIAN_COMPANIES
    ENHANCED_COMPANIES = ALL_INDIAN_COMPANIES
except ImportError:
    try:
        from core.company_registry import ALL_INDIAN_COMPANIES
        ENHANCED_COMPANIES = ALL_INDIAN_COMPANIES
    except ImportError:
        # Fallback to basic list if registry not available
        ENHANCED_COMPANIES = {
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

# Financial keywords for trend detection
POSITIVE_KEYWORDS = [
    'buy', 'bullish', 'positive', 'growth', 'profit', 'gain', 'rise', 'up', 'strong',
    'good', 'excellent', 'outperform', 'target', 'recommend', 'upgrade', 'beat',
    'surprise', 'better', 'increase', 'higher', 'rally', 'momentum', 'breakout',
    'surge', 'soar', 'jump', 'climb', 'advance', 'boost', 'improve', 'expand',
    'earnings beat', 'revenue growth', 'margin expansion', 'guidance raise'
]

NEGATIVE_KEYWORDS = [
    'sell', 'bearish', 'negative', 'loss', 'fall', 'down', 'weak', 'bad', 'poor',
    'underperform', 'downgrade', 'miss', 'decline', 'lower', 'drop', 'crash',
    'correction', 'concern', 'risk', 'worry', 'trouble', 'problem', 'plunge',
    'tumble', 'slump', 'slide', 'dip', 'retreat', 'pullback', 'volatility',
    'earnings miss', 'revenue decline', 'margin contraction', 'guidance cut'
]

TREND_KEYWORDS = [
    'trend', 'momentum', 'support', 'resistance', 'breakout', 'breakdown',
    'oversold', 'overbought', 'rally', 'correction', 'consolidation', 'volatility',
    'bull market', 'bear market', 'sideways', 'range-bound', 'uptrend', 'downtrend'
]

RISK_KEYWORDS = [
    'risk', 'volatility', 'uncertainty', 'concern', 'warning', 'caution',
    'regulatory', 'litigation', 'competition', 'debt', 'liquidity', 'default',
    'recession', 'inflation', 'interest rate', 'geopolitical', 'trade war'
]


def extract_enhanced_company_mentions(text: str) -> Dict[str, List[str]]:
    """Extract company mentions with enhanced detection including US stocks."""
    text_lower = text.lower()
    company_mentions = defaultdict(list)
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        sentence_clean = sentence.strip()
        
        # Check for company mentions
        for company in ENHANCED_COMPANIES:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, sentence_lower):
                if len(sentence_clean) > 10:
                    company_mentions[company].append(sentence_clean)
    
    return company_mentions


def extract_financial_indicators(text: str) -> Dict:
    """Extract financial indicators and keywords from text."""
    text_lower = text.lower()
    
    indicators = {
        'positive_keywords': [],
        'negative_keywords': [],
        'trend_keywords': [],
        'risk_keywords': [],
        'numbers': [],
        'percentages': [],
        'price_mentions': []
    }
    
    # Extract keywords
    for keyword in POSITIVE_KEYWORDS:
        if keyword in text_lower:
            indicators['positive_keywords'].append(keyword)
    
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text_lower:
            indicators['negative_keywords'].append(keyword)
    
    for keyword in TREND_KEYWORDS:
        if keyword in text_lower:
            indicators['trend_keywords'].append(keyword)
    
    for keyword in RISK_KEYWORDS:
        if keyword in text_lower:
            indicators['risk_keywords'].append(keyword)
    
    # Extract percentages (e.g., "5%", "10 percent")
    percentage_pattern = r'(\d+\.?\d*)\s*%|(\d+\.?\d*)\s+percent'
    percentages = re.findall(percentage_pattern, text_lower)
    indicators['percentages'] = [p[0] if p[0] else p[1] for p in percentages]
    
    # Extract price mentions (e.g., "$100", "$50.25")
    price_pattern = r'\$(\d+\.?\d*)'
    prices = re.findall(price_pattern, text)
    indicators['price_mentions'] = prices
    
    return indicators


def run_all_analyzers(
    text_files_dir: str = 'downloads/text_files',
    output_dir: str = 'downloads/analysis',
    create_chart: bool = False
) -> Dict:
    """
    Run all sentiment analyzers and collect comprehensive data.
    
    Returns:
        Dictionary containing all model outputs and extracted data
    """
    text_dir = Path(text_files_dir)
    if not text_dir.exists():
        print(f"✗ Directory not found: {text_files_dir}")
        return None
    
    text_files = list(text_dir.glob('*_transcribed.txt'))
    if not text_files:
        print(f"No transcribed text files found")
        return None
    
    print(f"Found {len(text_files)} transcribed file(s)")
    os.makedirs(output_dir, exist_ok=True)
    
    # Collect all model outputs
    all_model_outputs = {}
    
    # Run each analyzer
    analyzers = [
        ('base', analyze_base),
        ('textblob', analyze_textblob),
        ('vader', analyze_vader),
        ('keyword', analyze_keyword),
        ('ngram', analyze_ngram),
        ('rulebased', analyze_rulebased),
        ('finbert', analyze_finbert),
        ('hindi', analyze_hindi)
    ]
    
    for name, analyzer_func in analyzers:
        if analyzer_func:
            try:
                print(f"  Running {name} analyzer...")
                result = analyzer_func(text_files_dir, output_dir, create_chart)
                if result:
                    all_model_outputs[name] = result
            except Exception as e:
                print(f"  ⚠ {name} analyzer failed: {e}")
        else:
            print(f"  ⚠ {name} analyzer not available")
    
    # Extract comprehensive data from text files
    comprehensive_data = {
        'analysis_date': datetime.now().isoformat(),
        'source_files': [f.name for f in text_files],
        'model_outputs': all_model_outputs,
        'extracted_data': {}
    }
    
    # Process each text file
    for text_file in text_files:
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            file_data = {
                'file_name': text_file.name,
                'text_length': len(text),
                'companies_mentioned': extract_enhanced_company_mentions(text),
                'financial_indicators': extract_financial_indicators(text),
                'raw_text': text[:5000]  # First 5000 chars for context
            }
            
            comprehensive_data['extracted_data'][text_file.name] = file_data
            
        except Exception as e:
            print(f"  ⚠ Error processing {text_file.name}: {e}")
    
    # Aggregate company data across all models
    all_companies = set()
    company_sentiment_scores = defaultdict(list)
    company_mentions_count = defaultdict(int)
    company_contexts = defaultdict(list)
    
    for model_name, model_output in all_model_outputs.items():
        if model_output and 'companies' in model_output:
            for company_data in model_output['companies']:
                company = company_data.get('company', '').lower()
                if company:
                    all_companies.add(company)
                    company_sentiment_scores[company].append(company_data.get('sentiment_score', 0))
                    company_mentions_count[company] += company_data.get('total_mentions', 0)
                    contexts = company_data.get('sample_contexts', [])
                    if contexts:
                        company_contexts[company].extend(contexts[:2])  # Limit contexts
    
    # Calculate aggregated scores
    aggregated_companies = []
    for company in all_companies:
        if company_sentiment_scores[company]:
            avg_sentiment = sum(company_sentiment_scores[company]) / len(company_sentiment_scores[company])
            total_mentions = company_mentions_count[company]
            
            # Determine prediction
            if avg_sentiment > 0.2:
                prediction = 'POSITIVE'
            elif avg_sentiment < -0.2:
                prediction = 'NEGATIVE'
            else:
                prediction = 'NEUTRAL'
            
            # Calculate confidence
            confidence = min(abs(avg_sentiment) * (1 + min(total_mentions / 10, 0.5)), 1.0)
            
            aggregated_companies.append({
                'company': company.title(),
                'sentiment_score': round(avg_sentiment, 3),
                'total_mentions': total_mentions,
                'prediction': prediction,
                'confidence': round(confidence, 3),
                'sample_contexts': company_contexts[company][:3]
            })
    
    # Sort by confidence
    aggregated_companies.sort(key=lambda x: x['confidence'], reverse=True)
    
    comprehensive_data['aggregated_companies'] = aggregated_companies
    comprehensive_data['summary'] = {
        'total_companies': len(aggregated_companies),
        'positive': sum(1 for c in aggregated_companies if c['prediction'] == 'POSITIVE'),
        'negative': sum(1 for c in aggregated_companies if c['prediction'] == 'NEGATIVE'),
        'neutral': sum(1 for c in aggregated_companies if c['prediction'] == 'NEUTRAL')
    }
    
    # Save comprehensive data
    output_file = os.path.join(output_dir, 'comprehensive_analysis_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Comprehensive analysis data saved to: {output_file}")
    print(f"  Found {len(aggregated_companies)} companies")
    print(f"  Summary: {comprehensive_data['summary']['positive']} positive, "
          f"{comprehensive_data['summary']['negative']} negative, "
          f"{comprehensive_data['summary']['neutral']} neutral")
    
    return comprehensive_data


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Stock Analyzer')
    parser.add_argument('--text-dir', default='downloads/text_files', help='Text files directory')
    parser.add_argument('--output-dir', default='downloads/analysis', help='Output directory')
    parser.add_argument('--no-chart', action='store_true', help='Skip chart generation')
    
    args = parser.parse_args()
    
    run_all_analyzers(
        text_files_dir=args.text_dir,
        output_dir=args.output_dir,
        create_chart=not args.no_chart
    )

