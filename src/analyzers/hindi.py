#!/usr/bin/env python3
"""
Hindi/Hinglish Stock News Sentiment Analyzer
Transcribes Hindi/Hinglish audio using Whisper (without translation) and 
analyzes sentiment using XLM-RoBERTa (multilingual model).
No translation step - analyzes sentiment directly from Hindi/Hinglish text.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

# Check for required libraries
try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

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

# XLM-RoBERTa model for multilingual sentiment analysis
# Using cardiffnlp's multilingual sentiment model trained on Twitter data
XLM_ROBERTA_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

whisper_model = None
sentiment_pipeline = None


def initialize_whisper(model_size: str = 'base'):
    """Initialize Whisper model for transcription."""
    global whisper_model
    
    if not HAS_WHISPER:
        print("✗ Whisper not installed. Install with: pip install openai-whisper")
        return None
    
    if whisper_model is None:
        try:
            print(f"Loading Whisper model ({model_size})...")
            whisper_model = whisper.load_model(model_size)
            print("✓ Whisper model loaded")
            return whisper_model
        except Exception as e:
            print(f"✗ Failed to load Whisper model: {e}")
            return None
    
    return whisper_model


def initialize_sentiment_model():
    """Initialize XLM-RoBERTa sentiment analysis pipeline."""
    global sentiment_pipeline
    
    if not HAS_TRANSFORMERS:
        print("✗ Transformers not installed. Install with: pip install transformers torch")
        return None
    
    if sentiment_pipeline is None:
        try:
            print("Loading XLM-RoBERTa sentiment model (this may take a moment on first run)...")
            # Use use_fast=False to avoid SentencePiece tokenizer issues
            # If sentencepiece is installed, it will use fast tokenizer automatically
            try:
                tokenizer = AutoTokenizer.from_pretrained(XLM_ROBERTA_MODEL, use_fast=False)
            except:
                # Fallback: try with use_fast=True if sentencepiece is available
                tokenizer = AutoTokenizer.from_pretrained(XLM_ROBERTA_MODEL)
            
            model = AutoModelForSequenceClassification.from_pretrained(XLM_ROBERTA_MODEL)
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer
            )
            print("✓ XLM-RoBERTa model loaded successfully")
            return sentiment_pipeline
        except Exception as e:
            print(f"✗ Error loading XLM-RoBERTa model: {e}")
            error_str = str(e).lower()
            if 'protobuf' in error_str:
                print("  Missing dependency: protobuf")
                print("  Install with: pip install protobuf")
            elif 'sentencepiece' in error_str or 'sentence' in error_str:
                print("  Missing dependency: sentencepiece")
                print("  Install with: pip install sentencepiece")
            else:
                print("  Make sure you have internet connection for first-time model download")
                print("  Install dependencies: pip install transformers torch protobuf sentencepiece")
            return None
    
    return sentiment_pipeline


def transcribe_audio_no_translation(
    audio_path: str,
    output_dir: str = 'downloads/text_files',
    model_size: str = 'base'
) -> Optional[str]:
    """
    Transcribe audio file WITHOUT translating to English.
    Keeps original Hindi/Hinglish text.
    
    Args:
        audio_path: Path to audio file
        output_dir: Directory to save text files
        model_size: Whisper model size
    
    Returns:
        Path to saved text file, or None if failed
    """
    if not HAS_WHISPER:
        print("✗ Whisper not installed")
        return None
    
    model = initialize_whisper(model_size)
    if not model:
        return None
    
    audio_file = Path(audio_path)
    if not audio_file.exists():
        print(f"✗ Audio file not found: {audio_path}")
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Transcribing (no translation): {audio_file.name}")
    
    try:
        # Use task="transcribe" instead of "translate" to keep original language
        result = model.transcribe(
            str(audio_file),
            language=None,  # Auto-detect language
            task="transcribe"  # Transcribe only, don't translate
        )
    except Exception as e:
        print(f"✗ Transcription failed: {e}")
        return None
    
    detected_language = result.get('language', 'unknown')
    text = result.get('text', '').strip()
    
    print(f"  Detected language: {detected_language}")
    print(f"  Transcription length: {len(text)} characters")
    
    # Generate output filename
    audio_stem = audio_file.stem
    text_filename = f"{audio_stem}_hindi_transcribed.txt"
    text_path = os.path.join(output_dir, text_filename)
    
    # Save transcription (in original language - Hindi/Hinglish)
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"✓ Transcription saved to: {text_path}")
    return text_path


def analyze_sentiment_xlm_roberta(text: str, pipeline_obj) -> float:
    """
    Analyze sentiment using XLM-RoBERTa (multilingual).
    Returns sentiment score from -1 to 1.
    """
    if not pipeline_obj:
        return 0.0
    
    try:
        # XLM-RoBERTa works with sentences
        # Split text into sentences for better analysis
        sentences = re.split(r'[.!?।]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return 0.0
        
        scores = []
        for sentence in sentences[:20]:  # Limit to avoid token limit
            try:
                # XLM-RoBERTa returns: [{'label': 'positive', 'score': 0.91}]
                # Labels can be: positive, negative, neutral
                result = pipeline_obj(sentence[:512])  # Limit to 512 tokens
                
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
                continue
        
        if not scores:
            return 0.0
        
        # Average the scores
        avg_score = sum(scores) / len(scores)
        return max(-1.0, min(1.0, avg_score))
    
    except Exception as e:
        print(f"  ⚠ Error in sentiment analysis: {e}")
        return 0.0


def extract_company_mentions(text: str) -> Dict[str, List[str]]:
    # Ensure project root is in path for imports
    import sys
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    """Extract company mentions from Hindi/Hinglish text. Uses improved matching from company registry."""
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
            sentences = re.split(r'[.!?।]+', text)
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
    """Analyze sentiment for a specific company using XLM-RoBERTa."""
    if not contexts:
        return {
            'company': company,
            'sentiment_score': 0.0,
            'mentions': 0,
            'prediction': 'NEUTRAL',
            'confidence': 0.0
        }
    
    # Ensure contexts is a list (handle both list and dict formats)
    if isinstance(contexts, dict):
        # If it's a dict, extract the sentences
        contexts = [item.get('sentence', item) if isinstance(item, dict) else item for item in contexts.values()]
    elif isinstance(contexts, list) and contexts and isinstance(contexts[0], dict):
        # If it's a list of dicts, extract sentences
        contexts = [item.get('sentence', item) if isinstance(item, dict) else item for item in contexts]
    
    combined_text = ' '.join(contexts)
    sentiment_score = analyze_sentiment_xlm_roberta(combined_text, pipeline_obj)
    
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
        'total_mentions': mention_count,
        'prediction': prediction,
        'confidence': round(confidence, 3),
        'sample_contexts': contexts[:3] if isinstance(contexts, list) else []
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
    plt.title('Stock Performance Prediction - XLM-RoBERTa (Hindi/Hinglish)', fontsize=14, fontweight='bold')
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


def analyze_hindi_transcriptions(
    text_files_dir: str = 'downloads/text_files',
    output_dir: str = 'downloads/analysis',
    create_chart: bool = True,
    use_translated_text: bool = True
) -> Dict:
    """
    Analyze Hindi/Hinglish transcribed text files using XLM-RoBERTa.
    
    Note: Due to poor Hindi transcription quality from Whisper, this function
    uses the English translated text (which is more accurate) and analyzes it
    with XLM-RoBERTa (which handles English well).
    
    Args:
        text_files_dir: Directory containing text files
        output_dir: Directory to save analysis results
        create_chart: Whether to create visualization chart
        use_translated_text: If True, use English translated text (better quality)
                           If False, use Hindi transcribed text (may be garbled)
    """
    if not HAS_TRANSFORMERS:
        print("✗ Transformers library not installed.")
        print("  Install with: pip install transformers torch")
        return None
    
    # Initialize sentiment model
    pipeline_obj = initialize_sentiment_model()
    if not pipeline_obj:
        print("✗ Failed to initialize XLM-RoBERTa model")
        return None
    
    text_dir = Path(text_files_dir)
    if not text_dir.exists():
        print(f"✗ Directory not found: {text_files_dir}")
        return None
    
    # Look for text files - prefer translated English text (better quality)
    if use_translated_text:
        # Use English translated text (better quality than Hindi transcription)
        text_files = list(text_dir.glob('*_transcribed.txt'))
        # Exclude Hindi transcribed files (they're garbled)
        text_files = [f for f in text_files if '_hindi_transcribed.txt' not in str(f)]
        if not text_files:
            print(f"No translated text files found in {text_files_dir}")
            print("  Looking for files ending with '_transcribed.txt' (English translation)")
            return None
        print("  Using English translated text (better quality than Hindi transcription)")
    else:
        # Use Hindi transcribed files (may be garbled)
        text_files = list(text_dir.glob('*_hindi_transcribed.txt'))
        if not text_files:
            print(f"No Hindi transcribed files found in {text_files_dir}")
            print("  Looking for files ending with '_hindi_transcribed.txt'")
            return None
    
    file_type = "translated" if use_translated_text else "Hindi/Hinglish"
    print(f"Found {len(text_files)} {file_type} transcribed file(s)\n")
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
        
        print(f"Analyzing (XLM-RoBERTa): {Path(text_file).name}")
        company_mentions_raw = extract_company_mentions(text)
        
        if not company_mentions_raw:
            print("  No company mentions found")
            continue
        
        # Extract metadata and filter out metadata keys
        company_mentions = {}
        company_metadata = {}
        for key, value in company_mentions_raw.items():
            if key.startswith('__meta_'):
                company_name = key.replace('__meta_', '')
                company_metadata[company_name] = value
            else:
                company_mentions[key] = value
        
        print(f"  Found {len(company_mentions)} companies mentioned")
        
        results = []
        for company, contexts in company_mentions.items():
            analysis = analyze_company_sentiment(company, contexts, pipeline_obj)
            
            # Add false positive flag if metadata available
            if company in company_metadata:
                meta = company_metadata[company]
                analysis['likely_false_positive'] = meta.get('has_false_positive', False)
                analysis['match_confidence'] = round(meta.get('avg_confidence', 1.0), 3)
            else:
                analysis['likely_false_positive'] = False
                analysis['match_confidence'] = 1.0
            
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
            # Handle both 'mentions' and 'total_mentions' field names
            mentions = company_data.get('total_mentions', company_data.get('mentions', 0))
            combined_companies[company]['mentions'] += mentions
            combined_companies[company]['contexts'].extend(company_data.get('sample_contexts', company_data.get('contexts', [])))
    
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
        'algorithm': 'XLM-RoBERTa (Multilingual)',
        'algorithm_description': 'Multilingual sentiment analysis using XLM-RoBERTa. Uses English translated text (better quality than Hindi transcription) and analyzes with XLM-RoBERTa which handles English well.',
        'model_name': XLM_ROBERTA_MODEL,
        'note': 'Uses English translation because Whisper Hindi transcription quality is poor. XLM-RoBERTa handles English well.',
        'source_files': [r['source_file'] for r in all_results],
        'total_companies_analyzed': len(final_results),
        'companies': final_results,
        'summary': {
            'positive': sum(1 for c in final_results if c['prediction'] == 'POSITIVE'),
            'negative': sum(1 for c in final_results if c['prediction'] == 'NEGATIVE'),
            'neutral': sum(1 for c in final_results if c['prediction'] == 'NEUTRAL')
        }
    }
    
    json_path = os.path.join(output_dir, 'sentiment_xlmroberta_hindi_predictions.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ XLM-RoBERTa predictions saved to: {json_path}")
    
    if create_chart:
        chart_path = os.path.join(output_dir, 'sentiment_xlmroberta_hindi_chart.png')
        create_performance_chart(output, chart_path)
        print(f"✓ Chart saved to: {chart_path}")
    
    return output


def process_audio_and_analyze(
    audio_path: str,
    text_output_dir: str = 'downloads/text_files',
    analysis_output_dir: str = 'downloads/analysis',
    whisper_model_size: str = 'base',
    create_chart: bool = True
) -> Dict:
    """
    Complete workflow: Transcribe Hindi/Hinglish audio (no translation) 
    and analyze sentiment using XLM-RoBERTa.
    
    Args:
        audio_path: Path to audio file
        text_output_dir: Directory to save transcriptions
        analysis_output_dir: Directory to save analysis results
        whisper_model_size: Whisper model size
        create_chart: Whether to create visualization chart
    
    Returns:
        Analysis results dictionary
    """
    print("="*60)
    print("Hindi/Hinglish Stock News Sentiment Analysis")
    print("="*60)
    print()
    
    # Step 1: Transcribe audio (no translation)
    print("Step 1: Transcribing audio (keeping Hindi/Hinglish)...")
    text_file = transcribe_audio_no_translation(
        audio_path,
        output_dir=text_output_dir,
        model_size=whisper_model_size
    )
    
    if not text_file:
        print("✗ Transcription failed")
        return None
    
    print()
    
    # Step 2: Analyze sentiment
    print("Step 2: Analyzing sentiment using XLM-RoBERTa...")
    results = analyze_hindi_transcriptions(
        text_files_dir=text_output_dir,
        output_dir=analysis_output_dir,
        create_chart=create_chart
    )
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Transcribe Hindi/Hinglish audio and analyze sentiment using XLM-RoBERTa'
    )
    parser.add_argument(
        'audio_path',
        nargs='?',
        default=None,
        help='Path to audio file (optional if analyzing existing transcriptions)'
    )
    parser.add_argument(
        '--text-dir',
        default='downloads/text_files',
        help='Directory containing Hindi transcribed text files (default: downloads/text_files)'
    )
    parser.add_argument(
        '--output-dir',
        default='downloads/analysis',
        help='Directory to save analysis results (default: downloads/analysis)'
    )
    parser.add_argument(
        '--whisper-model',
        default='base',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size (default: base)'
    )
    parser.add_argument(
        '--no-chart',
        action='store_true',
        help='Skip creating performance chart'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only analyze existing transcriptions, skip audio transcription'
    )
    parser.add_argument(
        '--use-hindi-text',
        action='store_true',
        help='Use Hindi transcribed text (default: uses English translation for better quality)'
    )
    
    args = parser.parse_args()
    
    if not HAS_WHISPER:
        print("⚠ Whisper not installed. Install with: pip install openai-whisper")
    
    if not HAS_TRANSFORMERS:
        print("⚠ Transformers not installed. Install with: pip install transformers torch")
        print("  Note: First run will download XLM-RoBERTa model (~500MB)")
    
    if args.analyze_only:
        # Only analyze existing transcriptions
        results = analyze_hindi_transcriptions(
            text_files_dir=args.text_dir,
            output_dir=args.output_dir,
            create_chart=not args.no_chart,
            use_translated_text=not args.use_hindi_text
        )
    elif args.audio_path:
        # Transcribe and analyze
        results = process_audio_and_analyze(
            audio_path=args.audio_path,
            text_output_dir=args.text_dir,
            analysis_output_dir=args.output_dir,
            whisper_model_size=args.whisper_model,
            create_chart=not args.no_chart
        )
    else:
        # Try to analyze existing transcriptions
        print("No audio file provided. Analyzing existing transcriptions...")
        results = analyze_hindi_transcriptions(
            text_files_dir=args.text_dir,
            output_dir=args.output_dir,
            create_chart=not args.no_chart,
            use_translated_text=not args.use_hindi_text
        )
    
    if results:
        print(f"\n✓ Analysis complete! {results['total_companies_analyzed']} companies analyzed")
        print("\n💡 Note: Uses English translated text (better quality) since Whisper")
        print("   Hindi transcription produces garbled text. XLM-RoBERTa handles English well.")

