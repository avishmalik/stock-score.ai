#!/usr/bin/env python3
"""
AI Insights Generator
Analyzes comprehensive model outputs and generates AI-powered insights,
trends, predictions, and recommendations for stock analysis.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def calculate_growth_probability(company_data: Dict, all_data: Dict) -> float:
    """Calculate growth probability based on sentiment and indicators."""
    sentiment_score = company_data.get('sentiment_score', 0)
    confidence = company_data.get('confidence', 0)
    mentions = company_data.get('total_mentions', 0)
    
    # Base probability from sentiment
    base_prob = 0.5 + (sentiment_score * 0.4)  # Range: 0.1 to 0.9
    
    # Adjust based on confidence and mentions
    confidence_boost = confidence * 0.2
    mention_boost = min(mentions / 20, 0.1)  # More mentions = more reliable
    
    growth_prob = base_prob + confidence_boost + mention_boost
    
    # Clamp between 0 and 1
    return max(0.0, min(1.0, growth_prob))


def calculate_loss_probability(company_data: Dict, all_data: Dict) -> float:
    """Calculate loss probability based on negative sentiment and risk indicators."""
    sentiment_score = company_data.get('sentiment_score', 0)
    confidence = company_data.get('confidence', 0)
    
    # If sentiment is negative, loss probability increases
    if sentiment_score < 0:
        base_prob = 0.5 + abs(sentiment_score) * 0.4
    else:
        base_prob = 0.3 - (sentiment_score * 0.2)  # Positive sentiment reduces loss prob
    
    # Adjust based on confidence
    confidence_boost = confidence * 0.15
    
    loss_prob = base_prob + confidence_boost
    
    # Clamp between 0 and 1
    return max(0.0, min(1.0, loss_prob))


def detect_trend(company_data: Dict, all_data: Dict) -> str:
    """Detect trend direction based on sentiment and indicators."""
    sentiment_score = company_data.get('sentiment_score', 0)
    prediction = company_data.get('prediction', 'NEUTRAL')
    
    if sentiment_score > 0.3:
        return 'STRONG_BULLISH'
    elif sentiment_score > 0.1:
        return 'BULLISH'
    elif sentiment_score < -0.3:
        return 'STRONG_BEARISH'
    elif sentiment_score < -0.1:
        return 'BEARISH'
    else:
        return 'NEUTRAL'


def extract_key_factors(company_data: Dict, all_data: Dict) -> List[str]:
    """Extract key factors influencing the stock."""
    factors = []
    contexts = company_data.get('sample_contexts', [])
    
    # Analyze contexts for key factors
    positive_indicators = ['beat', 'growth', 'profit', 'gain', 'rise', 'strong', 'upgrade', 'buy']
    negative_indicators = ['miss', 'loss', 'fall', 'decline', 'downgrade', 'sell', 'concern']
    
    for context in contexts:
        context_lower = context.lower()
        
        # Check for positive factors
        for indicator in positive_indicators:
            if indicator in context_lower:
                if indicator not in factors:
                    factors.append(f"Positive: {indicator.title()}")
        
        # Check for negative factors
        for indicator in negative_indicators:
            if indicator in context_lower:
                if indicator not in factors:
                    factors.append(f"Risk: {indicator.title()}")
    
    return factors[:5]  # Return top 5 factors


def generate_ai_insights(comprehensive_data_file: str, output_file: Optional[str] = None) -> Dict:
    """
    Generate AI insights from comprehensive analysis data.
    
    Args:
        comprehensive_data_file: Path to comprehensive_analysis_data.json
        output_file: Optional path to save insights JSON
    
    Returns:
        Dictionary containing AI insights and recommendations
    """
    # Load comprehensive data
    if not os.path.exists(comprehensive_data_file):
        print(f"✗ Comprehensive data file not found: {comprehensive_data_file}")
        return None
    
    with open(comprehensive_data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Generating AI insights from comprehensive analysis...")
    
    # Initialize insights structure
    insights = {
        'generation_date': datetime.now().isoformat(),
        'source_data': comprehensive_data_file,
        'overall_analysis': {},
        'company_insights': [],
        'market_trends': {},
        'risk_assessment': {},
        'recommendations': []
    }
    
    # Overall market analysis
    summary = data.get('summary', {})
    aggregated_companies = data.get('aggregated_companies', [])
    
    total_companies = summary.get('total_companies', 0)
    positive_count = summary.get('positive', 0)
    negative_count = summary.get('negative', 0)
    neutral_count = summary.get('neutral', 0)
    
    # Calculate overall market sentiment
    if total_companies > 0:
        positive_ratio = positive_count / total_companies
        negative_ratio = negative_count / total_companies
        
        if positive_ratio > 0.6:
            market_sentiment = "STRONGLY_BULLISH"
        elif positive_ratio > 0.4:
            market_sentiment = "BULLISH"
        elif negative_ratio > 0.6:
            market_sentiment = "STRONGLY_BEARISH"
        elif negative_ratio > 0.4:
            market_sentiment = "BEARISH"
        else:
            market_sentiment = "MIXED"
    else:
        market_sentiment = "NEUTRAL"
    
    insights['overall_analysis'] = {
        'market_sentiment': market_sentiment,
        'total_companies_analyzed': total_companies,
        'positive_companies': positive_count,
        'negative_companies': negative_count,
        'neutral_companies': neutral_count,
        'bullish_ratio': round(positive_ratio, 3) if total_companies > 0 else 0,
        'bearish_ratio': round(negative_ratio, 3) if total_companies > 0 else 0
    }
    
    # Generate insights for each company
    for company_data in aggregated_companies:
        company_insight = {
            'company': company_data.get('company', 'Unknown'),
            'sentiment_score': company_data.get('sentiment_score', 0),
            'prediction': company_data.get('prediction', 'NEUTRAL'),
            'confidence': company_data.get('confidence', 0),
            'trend': detect_trend(company_data, data),
            'growth_probability': round(calculate_growth_probability(company_data, data), 3),
            'loss_probability': round(calculate_loss_probability(company_data, data), 3),
            'key_factors': extract_key_factors(company_data, data),
            'mentions': company_data.get('total_mentions', 0),
            'sample_contexts': company_data.get('sample_contexts', [])
        }
        
        insights['company_insights'].append(company_insight)
    
    # Market trends analysis
    bullish_companies = [c for c in aggregated_companies if c.get('sentiment_score', 0) > 0.2]
    bearish_companies = [c for c in aggregated_companies if c.get('sentiment_score', 0) < -0.2]
    
    insights['market_trends'] = {
        'bullish_stocks': [c['company'] for c in sorted(bullish_companies, key=lambda x: x['sentiment_score'], reverse=True)[:10]],
        'bearish_stocks': [c['company'] for c in sorted(bearish_companies, key=lambda x: x['sentiment_score'])[:10]],
        'high_confidence_picks': [c['company'] for c in sorted(aggregated_companies, key=lambda x: x.get('confidence', 0), reverse=True)[:5]],
        'most_mentioned': [c['company'] for c in sorted(aggregated_companies, key=lambda x: x.get('total_mentions', 0), reverse=True)[:10]]
    }
    
    # Risk assessment
    high_risk_companies = [
        c for c in aggregated_companies 
        if c.get('sentiment_score', 0) < -0.2 and c.get('confidence', 0) > 0.6
    ]
    
    insights['risk_assessment'] = {
        'high_risk_stocks': [{'company': c['company'], 'risk_score': round(1 - c.get('sentiment_score', 0), 3)} 
                            for c in high_risk_companies],
        'overall_risk_level': 'HIGH' if len(high_risk_companies) > total_companies * 0.3 else 'MODERATE' if len(high_risk_companies) > 0 else 'LOW',
        'risk_factors_count': len(high_risk_companies)
    }
    
    # Generate recommendations
    recommendations = []
    
    # Top bullish recommendations
    top_bullish = sorted(
        [c for c in aggregated_companies if c.get('sentiment_score', 0) > 0.2],
        key=lambda x: (x.get('sentiment_score', 0) * x.get('confidence', 0)),
        reverse=True
    )[:5]
    
    for company in top_bullish:
        recommendations.append({
            'type': 'BUY',
            'company': company['company'],
            'reason': f"Strong positive sentiment ({company.get('sentiment_score', 0):.2f}) with high confidence ({company.get('confidence', 0):.2f})",
            'growth_probability': round(calculate_growth_probability(company, data), 3)
        })
    
    # High risk warnings
    for company in high_risk_companies[:3]:
        recommendations.append({
            'type': 'CAUTION',
            'company': company['company'],
            'reason': f"Negative sentiment ({company.get('sentiment_score', 0):.2f}) with high confidence - potential downside risk",
            'loss_probability': round(calculate_loss_probability(company, data), 3)
        })
    
    insights['recommendations'] = recommendations
    
    # Generate summary text
    summary_text = f"""
MARKET ANALYSIS SUMMARY
=======================
Overall Market Sentiment: {market_sentiment}
Total Companies Analyzed: {total_companies}
Positive: {positive_count} | Negative: {negative_count} | Neutral: {neutral_count}

TOP OPPORTUNITIES:
{chr(10).join([f"- {r['company']}: {r['reason']}" for r in recommendations[:3] if r['type'] == 'BUY'])}

RISK WARNINGS:
{chr(10).join([f"- {r['company']}: {r['reason']}" for r in recommendations if r['type'] == 'CAUTION'])}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    insights['summary_text'] = summary_text
    
    # Save insights
    if output_file is None:
        output_dir = os.path.dirname(comprehensive_data_file)
        output_file = os.path.join(output_dir, 'ai_insights.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)
    
    print(f"✓ AI insights saved to: {output_file}")
    print(summary_text)
    
    return insights


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Insights Generator')
    parser.add_argument('--data-file', default='downloads/analysis/comprehensive_analysis_data.json',
                       help='Path to comprehensive analysis data JSON')
    parser.add_argument('--output', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    generate_ai_insights(args.data_file, args.output)

