#!/usr/bin/env python3
"""
Sentiment Analyzer - Algorithm 6: FinBERT
Uses FinBERT (ProsusAI) - a BERT model fine-tuned on financial news sentiment.
Handles finance-specific wording like "margin contraction", "beat estimates", etc.
Much more accurate for stock price correlation tasks.
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
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("⚠ Transformers not found. Install with: pip install transformers torch")

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

# FinBERT model configuration
FINBERT_MODEL = "ProsusAI/finbert"
finbert_pipeline = None


def initialize_finbert():
    """Initialize FinBERT model and pipeline."""
    global finbert_pipeline
    
    if not HAS_TRANSFORMERS:
        return None
    
    if finbert_pipeline is None:
        try:
            print("Loading FinBERT model (this may take a moment on first run)...")
            tokenizer = AutoTokenizer.from_pretrained(FINBERT_MODEL)
            model = AutoModelForSequenceClassification.from_pretrained(FINBERT_MODEL)
            finbert_pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer
            )
            print("✓ FinBERT model loaded successfully")
            return finbert_pipeline
        except Exception as e:
            print(f"✗ Error loading FinBERT model: {e}")
            print("  Make sure you have internet connection for first-time model download")
            return None
    
    return finbert_pipeline


def analyze_sentiment_finbert(text: str, pipeline_obj) -> float:
    """
    Analyze sentiment using FinBERT (returns -1 to 1).
    FinBERT returns labels: 'positive', 'negative', 'neutral'
    """
    if not pipeline_obj:
        return 0.0
    
    try:
        # FinBERT works best with shorter text segments
        # Split long text into sentences and analyze each
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return 0.0
        
        # Analyze each sentence
        scores = []
        for sentence in sentences[:10]:  # Limit to first 10 sentences to avoid token limit
            try:
                result = pipeline_obj(sentence[:512])  # Limit to 512 tokens
                
                # FinBERT returns: [{'label': 'positive', 'score': 0.91}]
                label = result[0]['label'].lower()
                score = result[0]['score']
                
                # Convert to -1 to 1 range
                if label == 'positive':
                    sentiment_score = score  # 0 to 1
                elif label == 'negative':
                    sentiment_score = -score  # -1 to 0
                else:  # neutral
                    sentiment_score = 0.0
                
                scores.append(sentiment_score)
            except Exception as e:
                # Skip sentences that cause errors
                continue
        
        if not scores:
            return 0.0
        
        # Average the scores
        avg_score = sum(scores) / len(scores)
        return max(-1.0, min(1.0, avg_score))
    
    except Exception as e:
        print(f"  ⚠ Error in FinBERT analysis: {e}")
        return 0.0


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


def analyze_company_sentiment(company: str, contexts: List[str], pipeline_obj) -> Dict:
    """Analyze sentiment for a specific company using FinBERT."""
    if not contexts:
        return {
            'company': company,
            'sentiment_score': 0.0,
            'mentions': 0,
            'prediction': 'NEUTRAL',
            'confidence': 0.0
        }
    
    # Combine contexts but keep them manageable for FinBERT
    # FinBERT works better with individual sentences, so we'll analyze each context
    combined_text = ' '.join(contexts)
    sentiment_score = analyze_sentiment_finbert(combined_text, pipeline_obj)
    
    mention_count = len(contexts)
    
    if sentiment_score > 0.2:
        prediction = 'POSITIVE'
    elif sentiment_score < -0.2:
        prediction = 'NEGATIVE'
    else:
        prediction = 'NEUTRAL'
    
    # Confidence based on sentiment strength and mention count
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
    plt.title('Stock Performance Prediction - FinBERT Algorithm', fontsize=14, fontweight='bold')
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
    """Analyze all transcribed text files using FinBERT."""
    if not HAS_TRANSFORMERS:
        print("✗ Transformers library not installed.")
        print("  Install with: pip install transformers torch")
        return None
    
    # Initialize FinBERT
    pipeline_obj = initialize_finbert()
    if not pipeline_obj:
        print("✗ Failed to initialize FinBERT model")
        return None
    
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
        
        print(f"Analyzing (FinBERT): {Path(text_file).name}")
        company_mentions = extract_company_mentions(text)
        
        if not company_mentions:
            continue
        
        print(f"  Found {len(company_mentions)} companies mentioned")
        
        results = []
        for company, contexts in company_mentions.items():
            analysis = analyze_company_sentiment(company, contexts, pipeline_obj)
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
        'algorithm': 'FinBERT (ProsusAI)',
        'algorithm_description': 'BERT model fine-tuned on financial news sentiment. Handles finance-specific wording like "margin contraction", "beat estimates", etc.',
        'model_name': FINBERT_MODEL,
        'source_files': [r['source_file'] for r in all_results],
        'total_companies_analyzed': len(final_results),
        'companies': final_results,
        'summary': {
            'positive': sum(1 for c in final_results if c['prediction'] == 'POSITIVE'),
            'negative': sum(1 for c in final_results if c['prediction'] == 'NEGATIVE'),
            'neutral': sum(1 for c in final_results if c['prediction'] == 'NEUTRAL')
        }
    }
    
    json_path = os.path.join(output_dir, 'sentiment_finbert_predictions.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ FinBERT predictions saved to: {json_path}")
    
    if create_chart:
        chart_path = os.path.join(output_dir, 'sentiment_finbert_chart.png')
        create_performance_chart(output, chart_path)
        print(f"✓ Chart saved to: {chart_path}")
    
    return output


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sentiment Analyzer - FinBERT Algorithm')
    parser.add_argument('--text-dir', default='downloads/text_files')
    parser.add_argument('--output-dir', default='downloads/analysis')
    parser.add_argument('--no-chart', action='store_true')
    args = parser.parse_args()
    
    if not HAS_TRANSFORMERS:
        print("⚠ Transformers library not installed.")
        print("  Install with: pip install transformers torch")
        print("  Note: First run will download the FinBERT model (~500MB)")
    
    results = analyze_transcriptions(args.text_dir, args.output_dir, create_chart=not args.no_chart)
    if results:
        print(f"\n✓ Analysis complete! {results['total_companies_analyzed']} companies analyzed")
        print("\n💡 Tip: FinBERT is fine-tuned on financial news and handles")
        print("   finance-specific terminology better than general sentiment models.")

