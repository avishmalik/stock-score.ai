#!/usr/bin/env python3
"""
Sentiment Analyzer - Algorithm 4: N-gram Based
Uses n-gram (bigram and trigram) analysis to capture phrase-level sentiment.
Better at understanding context and multi-word expressions.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

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

# Positive and negative n-grams (phrases) with weights
POSITIVE_PHRASES = {
    ('buy', 'recommend'): 3.0, ('strong', 'buy'): 3.0, ('bullish', 'outlook'): 3.0,
    ('price', 'target'): 2.0, ('upgrade', 'to'): 2.5, ('beat', 'expectations'): 2.5,
    ('strong', 'growth'): 2.0, ('positive', 'momentum'): 2.0, ('good', 'performance'): 1.5,
    ('profit', 'growth'): 2.0, ('revenue', 'increase'): 1.5, ('earnings', 'beat'): 2.0,
    ('higher', 'target'): 2.0, ('upward', 'trend'): 2.0, ('breakout', 'above'): 2.5,
    ('strong', 'hold'): 1.5, ('buy', 'opportunity'): 2.5, ('positive', 'surprise'): 2.0
}

NEGATIVE_PHRASES = {
    ('sell', 'recommend'): 3.0, ('weak', 'performance'): 2.0, ('bearish', 'outlook'): 3.0,
    ('downgrade', 'to'): 2.5, ('miss', 'expectations'): 2.5, ('loss', 'concern'): 2.0,
    ('decline', 'in'): 1.5, ('fall', 'below'): 2.0, ('downward', 'trend'): 2.0,
    ('risk', 'factors'): 1.5, ('concern', 'about'): 1.5, ('trouble', 'ahead'): 2.0,
    ('avoid', 'stock'): 2.5, ('negative', 'surprise'): 2.0, ('lower', 'target'): 2.0,
    ('weak', 'momentum'): 1.5, ('sell', 'signal'): 2.5, ('correction', 'expected'): 2.0
}

# Single word keywords (fallback)
POSITIVE_KEYWORDS = {'buy', 'bullish', 'positive', 'growth', 'profit', 'gain', 'rise', 'strong', 'good', 'excellent', 'upgrade', 'beat', 'surprise', 'better', 'increase', 'higher', 'rally', 'momentum', 'breakout'}
NEGATIVE_KEYWORDS = {'sell', 'bearish', 'negative', 'loss', 'fall', 'down', 'weak', 'bad', 'poor', 'downgrade', 'miss', 'decline', 'lower', 'drop', 'crash', 'correction', 'concern', 'risk', 'worry', 'trouble', 'problem'}


def generate_ngrams(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
    """Generate n-grams from tokens."""
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def tokenize(text: str) -> List[str]:
    """Simple tokenization."""
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    return [w for w in text.split() if len(w) > 2]


def analyze_sentiment_ngram(text: str) -> float:
    """Analyze sentiment using n-gram approach (returns -1 to 1)."""
    tokens = tokenize(text)
    
    if len(tokens) < 2:
        # Fallback to single word analysis
        text_lower = text.lower()
        positive_count = sum(1 for word in POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in NEGATIVE_KEYWORDS if word in text_lower)
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        return (positive_count - negative_count) / total
    
    # Generate bigrams and trigrams
    bigrams = generate_ngrams(tokens, 2)
    trigrams = generate_ngrams(tokens, 3)
    
    positive_score = 0.0
    negative_score = 0.0
    
    # Check bigrams
    for bigram in bigrams:
        if bigram in POSITIVE_PHRASES:
            positive_score += POSITIVE_PHRASES[bigram]
        if bigram in NEGATIVE_PHRASES:
            negative_score += NEGATIVE_PHRASES[bigram]
    
    # Check trigrams
    for trigram in trigrams:
        # Check if any 2-word combination matches
        for i in range(len(trigram) - 1):
            bigram = (trigram[i], trigram[i+1])
            if bigram in POSITIVE_PHRASES:
                positive_score += POSITIVE_PHRASES[bigram] * 0.5  # Slightly lower weight
            if bigram in NEGATIVE_PHRASES:
                negative_score += NEGATIVE_PHRASES[bigram] * 0.5
    
    # Fallback to single words if no phrases found
    if positive_score == 0 and negative_score == 0:
        text_lower = text.lower()
        positive_count = sum(1 for word in POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in NEGATIVE_KEYWORDS if word in text_lower)
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        positive_score = positive_count * 1.0
        negative_score = negative_count * 1.0
    
    total_score = positive_score + negative_score
    if total_score == 0:
        return 0.0
    
    sentiment = (positive_score - negative_score) / max(total_score, 1)
    return max(-1.0, min(1.0, sentiment))


def extract_company_mentions(text: str) -> Dict[str, List[str]]:
    # Ensure project root is in path for imports
    import sys
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    """Extract company mentions and surrounding context. Uses improved matching from company registry."""
    try:
        from src.core.company_registry import find_company_mentions
        return find_company_mentions(text)
    except ImportError:
        try:
            from core.company_registry import find_company_mentions
            return find_company_mentions(text)
        except ImportError:
            # Fallback to basic matching
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
    """Analyze sentiment for a specific company using n-gram approach."""
    if not contexts:
        return {
            'company': company,
            'sentiment_score': 0.0,
            'mentions': 0,
            'prediction': 'NEUTRAL',
            'confidence': 0.0
        }
    
    combined_text = ' '.join(contexts)
    sentiment_score = analyze_sentiment_ngram(combined_text)
    
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
    plt.title('Stock Performance Prediction - N-gram Based Algorithm', fontsize=14, fontweight='bold')
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
    """Analyze all transcribed text files using n-gram approach."""
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
        
        print(f"Analyzing (N-gram): {Path(text_file).name}")
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
        'algorithm': 'N-gram Based',
        'algorithm_description': 'Uses bigram and trigram analysis to capture phrase-level sentiment',
        'source_files': [r['source_file'] for r in all_results],
        'total_companies_analyzed': len(final_results),
        'companies': final_results,
        'summary': {
            'positive': sum(1 for c in final_results if c['prediction'] == 'POSITIVE'),
            'negative': sum(1 for c in final_results if c['prediction'] == 'NEGATIVE'),
            'neutral': sum(1 for c in final_results if c['prediction'] == 'NEUTRAL')
        }
    }
    
    json_path = os.path.join(output_dir, 'sentiment_ngram_predictions.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ N-gram predictions saved to: {json_path}")
    
    if create_chart:
        chart_path = os.path.join(output_dir, 'sentiment_ngram_chart.png')
        create_performance_chart(output, chart_path)
        print(f"✓ Chart saved to: {chart_path}")
    
    return output


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sentiment Analyzer - N-gram Based Algorithm')
    parser.add_argument('--text-dir', default='downloads/text_files')
    parser.add_argument('--output-dir', default='downloads/analysis')
    parser.add_argument('--no-chart', action='store_true')
    args = parser.parse_args()
    
    results = analyze_transcriptions(args.text_dir, args.output_dir, create_chart=not args.no_chart)
    if results:
        print(f"\n✓ Analysis complete! {results['total_companies_analyzed']} companies analyzed")

