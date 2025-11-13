#!/usr/bin/env python3
"""
Sentiment Analyzer - Algorithm 2: VADER
Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) for sentiment analysis.
VADER is specifically attuned to social media text and handles negations well.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    HAS_VADER = True
except ImportError:
    HAS_VADER = False
    print("⚠ VADER not found. Install with: pip install vaderSentiment")

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
    'mcx', 'nse', 'bse', 'ncdx',
    'chola', 'cummins', 'abb', 'abb india', 'zyder', 'life sciences', 'goedrich', 'goedrich properties',
    'amber', 'crompton', 'ncc', 'apollo', 'apollo hospital', 'jsw', 'fortis', 'ge', 'varunova',
    'seaman', 'tata elxsi', 'container corporation', 'jeffries', 'grasim payal',
    'man-kind pharma', 'upn', 'chohada', 'vyada', 'bazaar'
}


def analyze_sentiment_vader(text: str, analyzer) -> float:
    """Analyze sentiment using VADER (returns -1 to 1)."""
    if not HAS_VADER:
        return 0.0
    
    scores = analyzer.polarity_scores(text)
    return scores['compound']  # Compound score ranges from -1 to 1


def extract_company_mentions(text: str) -> Dict[str, List[str]]:
    """Extract company mentions and surrounding context."""
    text_lower = text.lower()
    company_mentions = defaultdict(list)
    
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for company in COMMON_COMPANIES:
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, sentence_lower):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 10:
                    company_mentions[company].append(clean_sentence)
    
    return company_mentions


def analyze_company_sentiment(company: str, contexts: List[str], analyzer) -> Dict:
    """Analyze sentiment for a specific company using VADER."""
    if not contexts:
        return {
            'company': company,
            'sentiment_score': 0.0,
            'mentions': 0,
            'prediction': 'NEUTRAL',
            'confidence': 0.0
        }
    
    combined_text = ' '.join(contexts)
    sentiment_score = analyze_sentiment_vader(combined_text, analyzer)
    
    mention_count = len(contexts)
    
    if sentiment_score > 0.2:
        prediction = 'POSITIVE'
    elif sentiment_score < -0.2:
        prediction = 'NEGATIVE'
    else:
        prediction = 'NEUTRAL'
    
    confidence = min(abs(sentiment_score) * (1 + min(mention_count / 10, 0.5)), 1.0)
    
    return {
        'company': company.title(),
        'sentiment_score': round(sentiment_score, 3),
        'mentions': mention_count,
        'prediction': prediction,
        'confidence': round(confidence, 3),
        'contexts': contexts[:3]
    }


def create_performance_chart(results: Dict, output_path: str):
    """Create a chart showing predicted performance."""
    companies = results.get('companies', [])
    if not companies:
        return
    
    top_companies = companies[:15]
    company_names = [c['company'] for c in top_companies]
    sentiment_scores = [c['sentiment_score'] for c in top_companies]
    colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' for s in sentiment_scores]
    
    plt.figure(figsize=(12, 8))
    bars = plt.barh(company_names, sentiment_scores, color=colors, alpha=0.7)
    
    plt.xlabel('Sentiment Score', fontsize=12)
    plt.ylabel('Company', fontsize=12)
    plt.title('Stock Performance Prediction - VADER Algorithm', fontsize=14, fontweight='bold')
    plt.axvline(x=0, color='black', linestyle='--', linewidth=0.5)
    plt.grid(axis='x', alpha=0.3)
    
    for i, (bar, score) in enumerate(zip(bars, sentiment_scores)):
        width = bar.get_width()
        label_x = width + (0.05 if width >= 0 else -0.05)
        plt.text(label_x, bar.get_y() + bar.get_height()/2, 
                f'{score:.2f}', ha='left' if width >= 0 else 'right', 
                va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def analyze_transcriptions(
    text_files_dir: str = 'downloads/text_files',
    output_dir: str = 'downloads/analysis',
    create_chart: bool = True
) -> Dict:
    """Analyze all transcribed text files using VADER."""
    if not HAS_VADER:
        print("✗ VADER not installed. Install with: pip install vaderSentiment")
        return None
    
    analyzer = SentimentIntensityAnalyzer()
    
    text_dir = Path(text_files_dir)
    if not text_dir.exists():
        print(f"✗ Directory not found: {text_files_dir}")
        return None
    
    text_files = list(text_dir.glob('*_transcribed.txt'))
    if not text_files:
        print(f"No transcribed text files found")
        return None
    
    print(f"Found {len(text_files)} transcribed file(s)\n")
    os.makedirs(output_dir, exist_ok=True)
    
    all_results = []
    for text_file in text_files:
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"✗ Error reading {text_file}: {e}")
            continue
        
        if not text or len(text.strip()) < 50:
            continue
        
        print(f"Analyzing (VADER): {Path(text_file).name}")
        company_mentions = extract_company_mentions(text)
        
        if not company_mentions:
            continue
        
        print(f"  Found {len(company_mentions)} companies mentioned")
        
        results = []
        for company, contexts in company_mentions.items():
            analysis = analyze_company_sentiment(company, contexts, analyzer)
            results.append(analysis)
        
        results.sort(key=lambda x: x['confidence'], reverse=True)
        all_results.append({
            'source_file': Path(text_file).name,
            'companies': results
        })
        print()
    
    if not all_results:
        return None
    
    # Combine results
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
            'sample_contexts': data['contexts'][:2]
        })
    
    final_results.sort(key=lambda x: x['confidence'], reverse=True)
    
    output = {
        'analysis_date': datetime.now().isoformat(),
        'algorithm': 'VADER',
        'algorithm_description': 'Valence Aware Dictionary and sEntiment Reasoner - optimized for social media text',
        'source_files': [r['source_file'] for r in all_results],
        'total_companies_analyzed': len(final_results),
        'companies': final_results,
        'summary': {
            'positive': sum(1 for c in final_results if c['prediction'] == 'POSITIVE'),
            'negative': sum(1 for c in final_results if c['prediction'] == 'NEGATIVE'),
            'neutral': sum(1 for c in final_results if c['prediction'] == 'NEUTRAL')
        }
    }
    
    json_path = os.path.join(output_dir, 'sentiment_vader_predictions.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ VADER predictions saved to: {json_path}")
    
    if create_chart:
        chart_path = os.path.join(output_dir, 'sentiment_vader_chart.png')
        create_performance_chart(output, chart_path)
        print(f"✓ Chart saved to: {chart_path}")
    
    return output


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sentiment Analyzer - VADER Algorithm')
    parser.add_argument('--text-dir', default='downloads/text_files')
    parser.add_argument('--output-dir', default='downloads/analysis')
    parser.add_argument('--no-chart', action='store_true')
    args = parser.parse_args()
    
    results = analyze_transcriptions(args.text_dir, args.output_dir, create_chart=not args.no_chart)
    if results:
        print(f"\n✓ Analysis complete! {results['total_companies_analyzed']} companies analyzed")

