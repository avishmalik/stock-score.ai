#!/usr/bin/env python3
"""
Sentiment Analyzer - Algorithm 5: Rule-Based with Financial Domain Knowledge
Uses financial domain-specific rules and patterns to analyze sentiment.
Includes negation handling, intensity modifiers, and financial terminology.
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

# Financial sentiment indicators with base scores
POSITIVE_INDICATORS = {
    'buy': 2.0, 'strong buy': 3.0, 'bullish': 2.5, 'positive': 2.0,
    'upgrade': 2.5, 'outperform': 2.0, 'recommend': 2.0, 'target': 1.5,
    'growth': 1.5, 'profit': 2.0, 'gain': 1.5, 'rise': 1.5, 'rally': 2.0,
    'beat': 2.0, 'surprise': 1.5, 'momentum': 1.5, 'breakout': 2.5,
    'excellent': 2.0, 'strong': 1.5, 'good': 1.0, 'better': 1.0
}

NEGATIVE_INDICATORS = {
    'sell': 2.0, 'strong sell': 3.0, 'bearish': 2.5, 'negative': 2.0,
    'downgrade': 2.5, 'underperform': 2.0, 'avoid': 2.0, 'miss': 2.0,
    'loss': 2.0, 'decline': 1.5, 'fall': 1.5, 'drop': 1.5, 'crash': 3.0,
    'correction': 2.0, 'concern': 1.5, 'risk': 1.0, 'weak': 1.5,
    'poor': 1.5, 'bad': 1.0, 'trouble': 1.5, 'problem': 1.0
}

# Intensity modifiers
INTENSIFIERS = {
    'very': 1.5, 'extremely': 2.0, 'highly': 1.5, 'significantly': 1.5,
    'substantially': 1.5, 'dramatically': 2.0, 'massively': 2.0
}

DIMINISHERS = {
    'slightly': 0.5, 'somewhat': 0.7, 'moderately': 0.7, 'a bit': 0.6
}

# Negation words
NEGATIONS = {'not', 'no', 'never', 'none', 'nobody', 'nothing', 'nowhere', 'neither', 'nor'}


def check_negation(text: str, word_pos: int, window: int = 3) -> bool:
    """Check if word at position is negated."""
    tokens = text.lower().split()
    start = max(0, word_pos - window)
    end = min(len(tokens), word_pos + window + 1)
    
    for i in range(start, end):
        if i != word_pos and tokens[i] in NEGATIONS:
            return True
    return False


def analyze_sentiment_rulebased(text: str) -> float:
    """Analyze sentiment using rule-based approach with financial domain knowledge."""
    text_lower = text.lower()
    tokens = text_lower.split()
    
    positive_score = 0.0
    negative_score = 0.0
    
    # Check for indicators
    for i, token in enumerate(tokens):
        # Check for positive indicators
        if token in POSITIVE_INDICATORS:
            score = POSITIVE_INDICATORS[token]
            # Check for negation
            if not check_negation(text_lower, i):
                # Check for intensifiers
                if i > 0 and tokens[i-1] in INTENSIFIERS:
                    score *= INTENSIFIERS[tokens[i-1]]
                elif i > 0 and tokens[i-1] in DIMINISHERS:
                    score *= DIMINISHERS[tokens[i-1]]
                positive_score += score
            else:
                # Negated positive = negative
                negative_score += score * 0.5
        
        # Check for negative indicators
        if token in NEGATIVE_INDICATORS:
            score = NEGATIVE_INDICATORS[token]
            # Check for negation
            if not check_negation(text_lower, i):
                # Check for intensifiers
                if i > 0 and tokens[i-1] in INTENSIFIERS:
                    score *= INTENSIFIERS[tokens[i-1]]
                elif i > 0 and tokens[i-1] in DIMINISHERS:
                    score *= DIMINISHERS[tokens[i-1]]
                negative_score += score
            else:
                # Negated negative = positive
                positive_score += score * 0.5
    
    # Check for multi-word phrases
    # Positive phrases
    if 'strong buy' in text_lower:
        positive_score += 3.0
    if 'price target' in text_lower or 'target price' in text_lower:
        positive_score += 1.5
    if 'beat expectations' in text_lower:
        positive_score += 2.5
    if 'positive surprise' in text_lower:
        positive_score += 2.0
    
    # Negative phrases
    if 'strong sell' in text_lower:
        negative_score += 3.0
    if 'miss expectations' in text_lower:
        negative_score += 2.5
    if 'negative surprise' in text_lower:
        negative_score += 2.0
    if 'avoid stock' in text_lower or 'avoid this' in text_lower:
        negative_score += 2.5
    
    # Calculate final score
    total_score = positive_score + negative_score
    if total_score == 0:
        return 0.0
    
    sentiment = (positive_score - negative_score) / max(total_score, 1)
    return max(-1.0, min(1.0, sentiment))


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


def analyze_company_sentiment(company: str, contexts: List[str]) -> Dict:
    """Analyze sentiment for a specific company using rule-based approach."""
    if not contexts:
        return {
            'company': company,
            'sentiment_score': 0.0,
            'mentions': 0,
            'prediction': 'NEUTRAL',
            'confidence': 0.0
        }
    
    combined_text = ' '.join(contexts)
    sentiment_score = analyze_sentiment_rulebased(combined_text)
    
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
    plt.title('Stock Performance Prediction - Rule-Based Algorithm', fontsize=14, fontweight='bold')
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
    """Analyze all transcribed text files using rule-based approach."""
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
        
        print(f"Analyzing (Rule-Based): {Path(text_file).name}")
        company_mentions = extract_company_mentions(text)
        
        if not company_mentions:
            continue
        
        print(f"  Found {len(company_mentions)} companies mentioned")
        
        results = []
        for company, contexts in company_mentions.items():
            analysis = analyze_company_sentiment(company, contexts)
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
        'algorithm': 'Rule-Based with Financial Domain Knowledge',
        'algorithm_description': 'Uses financial domain-specific rules, negation handling, and intensity modifiers',
        'source_files': [r['source_file'] for r in all_results],
        'total_companies_analyzed': len(final_results),
        'companies': final_results,
        'summary': {
            'positive': sum(1 for c in final_results if c['prediction'] == 'POSITIVE'),
            'negative': sum(1 for c in final_results if c['prediction'] == 'NEGATIVE'),
            'neutral': sum(1 for c in final_results if c['prediction'] == 'NEUTRAL')
        }
    }
    
    json_path = os.path.join(output_dir, 'sentiment_rulebased_predictions.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Rule-based predictions saved to: {json_path}")
    
    if create_chart:
        chart_path = os.path.join(output_dir, 'sentiment_rulebased_chart.png')
        create_performance_chart(output, chart_path)
        print(f"✓ Chart saved to: {chart_path}")
    
    return output


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sentiment Analyzer - Rule-Based Algorithm')
    parser.add_argument('--text-dir', default='downloads/text_files')
    parser.add_argument('--output-dir', default='downloads/analysis')
    parser.add_argument('--no-chart', action='store_true')
    args = parser.parse_args()
    
    results = analyze_transcriptions(args.text_dir, args.output_dir, create_chart=not args.no_chart)
    if results:
        print(f"\n✓ Analysis complete! {results['total_companies_analyzed']} companies analyzed")

