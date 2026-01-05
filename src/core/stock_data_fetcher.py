#!/usr/bin/env python3
"""
Stock Data Fetcher
Fetches real-time stock prices, company information, and trends from NSE India API.
"""

import requests
import json
import time
from typing import Dict, Optional, List
from pathlib import Path


# Mapping of company names to NSE symbols
COMPANY_TO_NSE_SYMBOL = {
    # Major companies
    'reliance': 'RELIANCE',
    'reliance industries': 'RELIANCE',
    'tcs': 'TCS',
    'tata consultancy': 'TCS',
    'tata consultancy services': 'TCS',
    'infosys': 'INFY',
    'infy': 'INFY',
    'hdfc': 'HDFC',
    'hdfc bank': 'HDFCBANK',
    'hdfcbank': 'HDFCBANK',
    'icici': 'ICICIBANK',
    'icici bank': 'ICICIBANK',
    'icicibank': 'ICICIBANK',
    'sbi': 'SBIN',
    'sbi bank': 'SBIN',
    'state bank': 'SBIN',
    'state bank of india': 'SBIN',
    'bharti': 'BHARTIARTL',
    'bharti airtel': 'BHARTIARTL',
    'airtel': 'BHARTIARTL',
    'lt': 'LT',
    'l&t': 'LT',
    'larsen & toubro': 'LT',
    'hcl': 'HCLTECH',
    'hcl tech': 'HCLTECH',
    'hcl technologies': 'HCLTECH',
    'wipro': 'WIPRO',
    'maruti': 'MARUTI',
    'maruti suzuki': 'MARUTI',
    'tata': 'TATAMOTORS',  # Default to Tata Motors
    'tata motors': 'TATAMOTORS',
    'adani': 'ADANIENT',
    'adani enterprises': 'ADANIENT',
    'adani ports': 'ADANIPORTS',
    'adani power': 'ADANIPOWER',
    'adani green': 'ADANIGREEN',
    'adani transmission': 'ADANITRANS',
    'jsw': 'JSWSTEEL',
    'jsw steel': 'JSWSTEEL',
    'vedanta': 'VEDL',
    'hindalco': 'HINDALCO',
    'hindalco industries': 'HINDALCO',
    'm&m': 'M&M',
    'mm': 'M&M',
    'mahindra': 'M&M',
    'mahindra & mahindra': 'M&M',
    'dlf': 'DLF',
    'grasim': 'GRASIM',
    'grasim industries': 'GRASIM',
    'ultratech': 'ULTRACEMCO',
    'ultratech cement': 'ULTRACEMCO',
    'ambuja': 'AMBUJACEM',
    'ambuja cements': 'AMBUJACEM',
    'shree cement': 'SHREECEM',
    'dabur': 'DABUR',
    'hul': 'HINDUNILVR',
    'hindustan unilever': 'HINDUNILVR',
    'itc': 'ITC',
    'asian paints': 'ASIANPAINT',
    'asianpaint': 'ASIANPAINT',
    'berger paints': 'BERGEPAINT',
    'nippon': 'NIPPONPAINT',
    'indigo': 'INDIGO',
    'interglobe aviation': 'INDIGO',
    'spicejet': 'SPICEJET',
    'jio': 'RELIANCE',  # Part of Reliance
    'reliance jio': 'RELIANCE',
    'lic': 'LICI',
    'life insurance corporation': 'LICI',
    'axis bank': 'AXISBANK',
    'kotak': 'KOTAKBANK',
    'kotak bank': 'KOTAKBANK',
    'kotak mahindra': 'KOTAKBANK',
    'pnb': 'PNB',
    'punjab national bank': 'PNB',
    'rbl bank': 'RBLBANK',
    'tata steel': 'TATASTEEL',
    'sail': 'SAIL',
    'steel authority': 'SAIL',
    'coal india': 'COALINDIA',
    'ongc': 'ONGC',
    'oil and natural gas': 'ONGC',
    'ioc': 'IOC',
    'indian oil': 'IOC',
    'bpcl': 'BPCL',
    'bharat petroleum': 'BPCL',
    'hpcl': 'HINDPETRO',
    'hindustan petroleum': 'HINDPETRO',
    'zomato': 'ZOMATO',
    'nykaa': 'NYKAA',
    'paytm': 'PAYTM',
    'one97 communications': 'PAYTM',
    'policybazaar': 'PBZ',
    'pbz': 'PBZ',
    'delhivery': 'DELHIVERY',
    'lupin': 'LUPIN',
    'dr reddy': 'DRREDDY',
    'dr reddys': 'DRREDDY',
    'sun pharma': 'SUNPHARMA',
    'cipla': 'CIPLA',
    'torrent': 'TORNTPHARM',
    'torrent pharma': 'TORNTPHARM',
    'mankind': 'MANKIND',
    'mankind pharma': 'MANKIND',
    'glenmark': 'GLENMARK',
    'nhpc': 'NHPC',
    'power grid': 'POWERGRID',
    'powergrid': 'POWERGRID',
    'ntpc': 'NTPC',
    'suzlon': 'SUZLON',
    'tata power': 'TATAPOWER',
    'upl': 'UPL',
    'coromandel': 'COROMANDEL',
    'rallis': 'RALLIS',
    'pi industries': 'PIIND',
    'piind': 'PIIND',
    'bajaj': 'BAJAJFINSV',
    'bajaj auto': 'BAJAJ-AUTO',
    'bajaj finserv': 'BAJAJFINSV',
    'bajaj finance': 'BAJFINANCE',
    'hero': 'HEROMOTOCO',
    'hero motocorp': 'HEROMOTOCO',
    'eicher': 'EICHERMOT',
    'eicher motors': 'EICHERMOT',
    'ashok leyland': 'ASHOKLEY',
    'mrf': 'MRF',
    'ceat': 'CEATLTD',
    'apollo tyres': 'APOLLOTYRE',
    'godrej': 'GODREJPROP',
    'godrej properties': 'GODREJPROP',
    'godrej consumer': 'GODREJCP',
    'nestle': 'NESTLEIND',
    'britannia': 'BRITANNIA',
    'marico': 'MARICO',
    'colgate': 'COLPAL',
    'colgate palmolive': 'COLPAL',
    'titan': 'TITAN',
    'titan company': 'TITAN',
    'dmart': 'DMART',
    'avenue supermarts': 'DMART',
    'tech mahindra': 'TECHM',
    'mindtree': 'MINDTREE',
    'lti': 'LTIM',
    'ltimindtree': 'LTIM',
    'mphasis': 'MPHASIS',
    'yes bank': 'YESBANK',
    'idfc first bank': 'IDFCFIRSTB',
    'bandhan bank': 'BANDHANBNK',
    'indusind bank': 'INDUSINDBK',
    'federal bank': 'FEDERALBNK',
    'bank of baroda': 'BANKBARODA',
    'canara bank': 'CANBK',
    'union bank': 'UNIONBANK',
    'apollo hospitals': 'APOLLOHOSP',
    'fortis': 'FORTIS',
    'max healthcare': 'MAXHEALTH',
    'bhel': 'BHEL',
    'bharat heavy electricals': 'BHEL',
    'bel': 'BEL',
    'bharat electronics': 'BEL',
    'bdl': 'BDL',
    'bharat dynamics': 'BDL',
    'irfc': 'IRFC',
    'ircon': 'IRCON',
    'rvnl': 'RVNL',
    'sjvn': 'SJVN',
    'nalco': 'NATIONALUM',
    'national aluminium': 'NATIONALUM',
    'hzl': 'HINDZINC',
    'hindustan zinc': 'HINDZINC',
}


def get_nse_symbol(company_name: str) -> Optional[str]:
    """
    Convert company name to NSE symbol.
    
    Args:
        company_name: Company name (case-insensitive)
    
    Returns:
        NSE symbol or None if not found
    """
    company_lower = company_name.lower().strip()
    
    # Direct lookup
    if company_lower in COMPANY_TO_NSE_SYMBOL:
        return COMPANY_TO_NSE_SYMBOL[company_lower]
    
    # Try partial matches
    for key, symbol in COMPANY_TO_NSE_SYMBOL.items():
        if key in company_lower or company_lower in key:
            return symbol
    
    return None


def fetch_nse_stock_data(symbol: str) -> Optional[Dict]:
    """
    Fetch stock data from NSE India API.
    
    Args:
        symbol: NSE stock symbol (e.g., "RELIANCE", "TCS")
    
    Returns:
        Dictionary containing stock data or None if error
    """
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Error fetching NSE data for {symbol}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️  Error parsing JSON for {symbol}: {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error for {symbol}: {e}")
        return None


def extract_stock_info(symbol: str, data: Dict) -> Dict:
    """
    Extract relevant stock information from NSE API response.
    
    Args:
        symbol: NSE symbol
        data: Raw API response data
    
    Returns:
        Dictionary with extracted stock information
    """
    info = {
        'symbol': symbol,
        'company_name': 'N/A',
        'last_price': None,
        'change': None,
        'change_percent': None,
        'open': None,
        'high': None,
        'low': None,
        'previous_close': None,
        'volume': None,
        'market_cap': None,
        'industry': 'N/A',
        'status': 'N/A',
        'error': None
    }
    
    try:
        # Price information
        if 'priceInfo' in data:
            price_info = data['priceInfo']
            info['last_price'] = price_info.get('lastPrice')
            info['change'] = price_info.get('change')
            info['change_percent'] = price_info.get('pChange')
            info['open'] = price_info.get('open')
            info['previous_close'] = price_info.get('previousClose')
            
            # Intraday high/low
            if 'intraDayHighLow' in price_info:
                high_low = price_info['intraDayHighLow']
                info['high'] = high_low.get('maxPrice')
                info['low'] = high_low.get('minPrice')
            
            # Volume
            info['volume'] = price_info.get('totalTradedVolume')
        
        # Company information
        if 'info' in data:
            info_data = data['info']
            info['company_name'] = info_data.get('companyName', 'N/A')
            info['industry'] = info_data.get('industry', 'N/A')
            info['market_cap'] = info_data.get('marketCap', None)
        
        # Determine status
        if info['change_percent'] is not None:
            if info['change_percent'] > 0:
                info['status'] = 'UP'
            elif info['change_percent'] < 0:
                info['status'] = 'DOWN'
            else:
                info['status'] = 'FLAT'
        
    except Exception as e:
        info['error'] = str(e)
    
    return info


def get_stock_data(company_name: str) -> Optional[Dict]:
    """
    Get stock data for a company by name.
    
    Args:
        company_name: Company name
    
    Returns:
        Stock information dictionary or None
    """
    symbol = get_nse_symbol(company_name)
    if not symbol:
        return None
    
    data = fetch_nse_stock_data(symbol)
    if not data:
        return None
    
    return extract_stock_info(symbol, data)


def get_multiple_stock_data(company_names: List[str]) -> Dict[str, Dict]:
    """
    Get stock data for multiple companies.
    
    Args:
        company_names: List of company names
    
    Returns:
        Dictionary mapping company names to stock data
    """
    results = {}
    
    for company in company_names:
        stock_data = get_stock_data(company)
        if stock_data:
            results[company] = stock_data
        # Add delay between requests to avoid rate limiting
        time.sleep(0.5)
    
    return results


def format_stock_info_for_prompt(stock_data: Dict) -> str:
    """
    Format stock information for inclusion in ChatGPT prompt.
    
    Args:
        stock_data: Stock information dictionary
    
    Returns:
        Formatted string
    """
    if not stock_data or stock_data.get('error'):
        return "  ⚠️  Stock data unavailable (please verify manually via web search)"
    
    lines = []
    lines.append(f"  📊 **Stock Symbol**: {stock_data.get('symbol', 'N/A')}")
    lines.append(f"  🏢 **Company**: {stock_data.get('company_name', 'N/A')}")
    
    if stock_data.get('last_price') is not None:
        lines.append(f"  💰 **Current Price**: ₹{stock_data.get('last_price', 'N/A')}")
    
    if stock_data.get('change') is not None and stock_data.get('change_percent') is not None:
        change = stock_data.get('change', 0)
        change_pct = stock_data.get('change_percent', 0)
        status_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        lines.append(f"  {status_emoji} **Change**: ₹{change:+.2f} ({change_pct:+.2f}%)")
    
    if stock_data.get('open') is not None:
        lines.append(f"  🔓 **Open**: ₹{stock_data.get('open', 'N/A')}")
    
    if stock_data.get('high') is not None and stock_data.get('low') is not None:
        lines.append(f"  📊 **Day Range**: ₹{stock_data.get('low', 'N/A')} - ₹{stock_data.get('high', 'N/A')}")
    
    if stock_data.get('previous_close') is not None:
        lines.append(f"  🔙 **Previous Close**: ₹{stock_data.get('previous_close', 'N/A')}")
    
    if stock_data.get('volume') is not None:
        volume = stock_data.get('volume', 0)
        if volume >= 1000000:
            volume_str = f"{volume/1000000:.2f}M"
        elif volume >= 1000:
            volume_str = f"{volume/1000:.2f}K"
        else:
            volume_str = str(volume)
        lines.append(f"  📦 **Volume**: {volume_str}")
    
    if stock_data.get('market_cap'):
        market_cap = stock_data.get('market_cap')
        if market_cap >= 1000000000000:  # Trillion
            cap_str = f"₹{market_cap/1000000000000:.2f}T"
        elif market_cap >= 10000000000:  # 10K crore
            cap_str = f"₹{market_cap/10000000000:.2f}K Cr"
        elif market_cap >= 1000000000:  # Crore
            cap_str = f"₹{market_cap/1000000000:.2f} Cr"
        else:
            cap_str = f"₹{market_cap:,.0f}"
        lines.append(f"  💎 **Market Cap**: {cap_str}")
    
    if stock_data.get('industry') != 'N/A':
        lines.append(f"  🏭 **Industry**: {stock_data.get('industry', 'N/A')}")
    
    return "\n".join(lines)


def get_company_trends_search_query(company_name: str, nse_symbol: Optional[str] = None) -> str:
    """
    Generate a web search query for company trends and news.
    
    Args:
        company_name: Company name
        nse_symbol: Optional NSE symbol
    
    Returns:
        Search query string
    """
    symbol_part = f" ({nse_symbol})" if nse_symbol else ""
    return f"{company_name}{symbol_part} stock news trends analysis India"


if __name__ == "__main__":
    # Test the functions
    test_companies = ["reliance", "tcs", "infosys", "hdfc bank"]
    
    print("🧪 Testing Stock Data Fetcher\n")
    
    for company in test_companies:
        print(f"\n{'='*60}")
        print(f"Testing: {company}")
        print(f"{'='*60}")
        
        symbol = get_nse_symbol(company)
        print(f"NSE Symbol: {symbol}")
        
        if symbol:
            stock_data = get_stock_data(company)
            if stock_data:
                formatted = format_stock_info_for_prompt(stock_data)
                print("\nStock Data:")
                print(formatted)
            else:
                print("❌ Failed to fetch stock data")
        else:
            print("⚠️  Symbol not found in mapping")
        
        time.sleep(1)  # Delay between tests

