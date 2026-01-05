#!/usr/bin/env python3
"""
Test script to fetch stock data from NSE India API
"""

import requests
import json
from typing import Dict, Optional


def fetch_nse_stock_data(symbol: str) -> Optional[Dict]:
    """
    Fetch stock data from NSE India API.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE", "TCS", "INFY")
    
    Returns:
        Dictionary containing stock data or None if error
    """
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()  # Raise an exception for bad status codes
        data = r.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for {symbol}: {e}")
        return None


def get_price_info(symbol: str) -> Optional[Dict]:
    """
    Get price information for a stock.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Price info dictionary or None
    """
    data = fetch_nse_stock_data(symbol)
    if data and "priceInfo" in data:
        return data["priceInfo"]
    return None


def print_stock_info(symbol: str):
    """Print formatted stock information."""
    print(f"\n{'='*60}")
    print(f"Stock Symbol: {symbol}")
    print(f"{'='*60}")
    
    data = fetch_nse_stock_data(symbol)
    if not data:
        print("❌ Failed to fetch data")
        return
    
    # Print price info
    if "priceInfo" in data:
        price_info = data["priceInfo"]
        print("\n📊 Price Information:")
        print(f"  Last Price: ₹{price_info.get('lastPrice', 'N/A')}")
        print(f"  Change: ₹{price_info.get('change', 'N/A')}")
        print(f"  Change %: {price_info.get('pChange', 'N/A')}%")
        print(f"  Open: ₹{price_info.get('open', 'N/A')}")
        print(f"  High: ₹{price_info.get('intraDayHighLow', {}).get('maxPrice', 'N/A')}")
        print(f"  Low: ₹{price_info.get('intraDayHighLow', {}).get('minPrice', 'N/A')}")
        print(f"  Previous Close: ₹{price_info.get('previousClose', 'N/A')}")
    
    # Print company info if available
    if "info" in data:
        info = data["info"]
        print("\n🏢 Company Information:")
        print(f"  Company Name: {info.get('companyName', 'N/A')}")
        print(f"  Industry: {info.get('industry', 'N/A')}")
        print(f"  ISIN: {info.get('isin', 'N/A')}")
    
    # Print market data if available
    if "marketDeptOrderBook" in data:
        mkt_data = data["marketDeptOrderBook"]
        print("\n📈 Market Data:")
        print(f"  Total Buy Quantity: {mkt_data.get('totalBuyQuantity', 'N/A')}")
        print(f"  Total Sell Quantity: {mkt_data.get('totalSellQuantity', 'N/A')}")
    
    # Print full data structure (for debugging)
    print("\n📋 Full Data Structure:")
    print(f"  Available keys: {list(data.keys())}")


def test_multiple_stocks(symbols: list):
    """Test fetching data for multiple stocks."""
    print(f"\n🧪 Testing {len(symbols)} stocks...\n")
    
    results = []
    for symbol in symbols:
        price_info = get_price_info(symbol)
        if price_info:
            results.append({
                'symbol': symbol,
                'lastPrice': price_info.get('lastPrice'),
                'change': price_info.get('change'),
                'pChange': price_info.get('pChange')
            })
            print(f"✅ {symbol}: ₹{price_info.get('lastPrice', 'N/A')} ({price_info.get('pChange', 'N/A')}%)")
        else:
            print(f"❌ {symbol}: Failed to fetch")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Test with RELIANCE (as in user's example)
    if len(sys.argv) > 1:
        # Test with provided symbol(s)
        symbols = sys.argv[1:]
        for symbol in symbols:
            print_stock_info(symbol.upper())
    else:
        # Default test
        print("🧪 Testing NSE India API")
        print("\n1. Testing single stock (RELIANCE):")
        print_stock_info("RELIANCE")
        
        print("\n\n2. Testing multiple stocks:")
        test_stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        test_multiple_stocks(test_stocks)
        
        print("\n\n💡 Usage:")
        print("  python scripts/test_nse_api.py RELIANCE")
        print("  python scripts/test_nse_api.py TCS INFY HDFCBANK")

