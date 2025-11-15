#!/usr/bin/env python3
"""
Comprehensive Analysis Runner
Runs all sentiment models, extracts comprehensive data, and generates AI insights.
This is the main entry point for Option 2B (Hybrid Approach).
"""

import os
import sys
from pathlib import Path

# Import comprehensive analyzer and AI insights generator
try:
    from comprehensive_stock_analyzer import run_all_analyzers
    from ai_insights_generator import generate_ai_insights
except ImportError as e:
    print(f"✗ Error importing modules: {e}")
    print("  Make sure comprehensive_stock_analyzer.py and ai_insights_generator.py are in the same directory")
    sys.exit(1)


def run_comprehensive_analysis(
    text_files_dir: str = 'downloads/text_files',
    output_dir: str = 'downloads/analysis',
    create_charts: bool = False
) -> dict:
    """
    Run comprehensive analysis pipeline:
    1. Run all sentiment models
    2. Extract comprehensive data
    3. Generate AI insights
    
    Args:
        text_files_dir: Directory containing transcribed text files
        output_dir: Directory to save analysis results
        create_charts: Whether to create visualization charts
    
    Returns:
        Dictionary containing comprehensive data and AI insights
    """
    print("=" * 60)
    print("COMPREHENSIVE STOCK ANALYSIS PIPELINE")
    print("=" * 60)
    print()
    
    # Step 1: Run all analyzers and extract comprehensive data
    print("STEP 1: Running all sentiment models and extracting data...")
    print("-" * 60)
    comprehensive_data = run_all_analyzers(
        text_files_dir=text_files_dir,
        output_dir=output_dir,
        create_chart=create_charts
    )
    
    if not comprehensive_data:
        print("✗ Failed to generate comprehensive data")
        return None
    
    print()
    
    # Step 2: Generate AI insights
    print("STEP 2: Generating AI insights and recommendations...")
    print("-" * 60)
    comprehensive_data_file = os.path.join(output_dir, 'comprehensive_analysis_data.json')
    ai_insights = generate_ai_insights(
        comprehensive_data_file=comprehensive_data_file,
        output_file=os.path.join(output_dir, 'ai_insights.json')
    )
    
    if not ai_insights:
        print("✗ Failed to generate AI insights")
        return comprehensive_data
    
    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"✓ Comprehensive data: {comprehensive_data_file}")
    print(f"✓ AI insights: {os.path.join(output_dir, 'ai_insights.json')}")
    print()
    
    return {
        'comprehensive_data': comprehensive_data,
        'ai_insights': ai_insights
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Comprehensive Stock Analysis - Runs all models and generates AI insights'
    )
    parser.add_argument(
        '--text-dir',
        default='downloads/text_files',
        help='Directory containing transcribed text files (default: downloads/text_files)'
    )
    parser.add_argument(
        '--output-dir',
        default='downloads/analysis',
        help='Output directory for analysis results (default: downloads/analysis)'
    )
    parser.add_argument(
        '--charts',
        action='store_true',
        help='Generate visualization charts'
    )
    
    args = parser.parse_args()
    
    result = run_comprehensive_analysis(
        text_files_dir=args.text_dir,
        output_dir=args.output_dir,
        create_charts=args.charts
    )
    
    if result:
        print("\n✓ Analysis pipeline completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Analysis pipeline failed")
        sys.exit(1)

