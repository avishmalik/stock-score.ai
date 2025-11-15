#!/usr/bin/env python3
"""
Company Registry
Centralized list of Indian stock market companies and indices.
All sentiment analyzers should import from this file to maintain consistency.
"""

# Indian Stock Market Companies
INDIAN_COMPANIES = {
    # Major Indian companies
    'reliance', 'tcs', 'infosys', 'hdfc', 'icici', 'sbi', 'bharti', 'lt', 'hcl', 'wipro',
    'maruti', 'tata', 'adani', 'jsw', 'vedanta', 'hindalco', 'tata motors', 'm&m', 'mm', 'mahindra',
    'dlf', 'grasim', 'ultratech', 'ambuja', 'shree cement', 'dabur', 'hul', 'itc',
    'asian paints', 'berger paints', 'nippon', 'indigo', 'spicejet', 'airtel', 'jio',
    'lic', 'sbi bank', 'hdfc bank', 'icici bank', 'axis bank', 'kotak', 'pnb', 'rbl bank',
    'tata steel', 'jsw steel', 'sail', 'coal india', 'ongc', 'ioc', 'bpcl', 'hpcl',
    'zomato', 'nykaa', 'paytm', 'policybazaar', 'delhivery',
    'lupin', 'dr reddy', 'sun pharma', 'cipla', 'torrent', 'mankind', 'glenmark', 'mankind pharma',
    'nhpc', 'power grid', 'ntpc', 'suzlon', 'adani green', 'tata power',
    'upl', 'coromandel', 'rallis', 'pi industries',
    'chola', 'cummins', 'abb', 'abb india', 'zyder', 'life sciences', 'goedrich', 'goedrich properties',
    'amber', 'crompton', 'ncc', 'apollo', 'apollo hospital', 'jsw', 'fortis', 'ge', 'varunova',
    'seaman', 'tata elxsi', 'container corporation', 'jeffries', 'grasim payal',
    'man-kind pharma', 'upn', 'chohada', 'vyada', 'bazaar',
    
    # Additional Indian companies
    'bajaj', 'bajaj auto', 'bajaj finserv', 'bajaj finance', 'hero motocorp', 'hero',
    'eicher motors', 'eicher', 'ashok leyland', 'mrf', 'ceat', 'apollo tyres',
    'godrej', 'godrej properties', 'godrej consumer', 'nestle', 'britannia', 'marico',
    'colgate', 'colgate palmolive', 'procter & gamble', 'pg', 'unilever', 'hul',
    'titan', 'titan company', 'tanishq', 'kalyan jewellers', 'pc jeweller',
    'dmart', 'avenue supermarts', 'reliance retail', 'future retail', 'shoppers stop',
    'bharti airtel', 'vodafone idea', 'vi', 'reliance jio', 'bsnl',
    'tata communications', 'tech mahindra', 'mindtree', 'lti', 'ltimindtree',
    'mphasis', 'cyient', 'zensar', 'persistent', 'quick heal',
    'adani ports', 'adani enterprises', 'adani power', 'adani transmission', 'adani total gas',
    'jindal steel', 'jindal saw', 'jindal stainless', 'jindal power',
    'hindalco', 'vedanta', 'hzl', 'hindustan zinc', 'national aluminium', 'nalco',
    'gail', 'petronet lng', 'indian oil', 'ioc', 'hpcl', 'bpcl', 'ongc',
    'ntpc', 'nhpc', 'power grid', 'suzlon', 'inox wind', 'orient green',
    'renewable energy', 'adani green', 'tata power', 'reliance power',
    'yes bank', 'idfc first bank', 'bandhan bank', 'au small finance', 'equitas small finance',
    'indusind bank', 'federal bank', 'south indian bank', 'karnataka bank',
    'bajaj holdings', 'bajaj auto', 'bajaj electricals', 'bajaj healthcare',
    'tata chemicals', 'tata coffee', 'tata global', 'tata metaliks',
    'ultratech cement', 'ambuja cement', 'acc', 'shree cement', 'dalmia cement',
    'ramco cements', 'india cements', 'orient cement', 'prism cement',
    'grasim', 'aditya birla', 'birla corporation', 'century textiles',
    'reliance industries', 'reliance jio', 'reliance retail', 'reliance infra',
    'adani group', 'adani ports', 'adani power', 'adani enterprises',
    'tata group', 'tata motors', 'tata steel', 'tata power', 'tata consultancy',
    'mahindra group', 'mahindra & mahindra', 'mahindra finance', 'mahindra logistics',
    'godrej group', 'godrej properties', 'godrej consumer', 'godrej industries',
    'bharti group', 'bharti airtel', 'bharti infratel',
    
    # Pharma companies
    'sun pharma', 'dr reddy', 'cipla', 'lupin', 'torrent', 'glenmark', 'cadila',
    'aurobindo', 'divis labs', 'biocon', 'natco', 'alembic', 'wockhardt',
    'piramal', 'piramal enterprises', 'strides pharma', 'laurus labs',
    
    # IT companies
    'tcs', 'infosys', 'wipro', 'hcl', 'tech mahindra', 'lti', 'ltimindtree',
    'mindtree', 'mphasis', 'cyient', 'persistent', 'zensar', 'quick heal',
    'tata elxsi', 'sonata software', 'niit', 'aptech',
    
    # Auto companies
    'maruti', 'mahindra', 'tata motors', 'bajaj auto', 'hero motocorp',
    'eicher motors', 'ashok leyland', 'tv motor', 'force motors',
    'mrf', 'ceat', 'apollo tyres', 'jk tyre', 'balkrishna industries',
    
    # FMCG companies
    'hul', 'itc', 'nestle', 'britannia', 'marico', 'dabur', 'colgate',
    'godrej consumer', 'tata consumer', 'emami', 'radico khaitan',
    
    # Banking & Finance
    'sbi', 'hdfc bank', 'icici bank', 'axis bank', 'kotak mahindra bank',
    'indusind bank', 'yes bank', 'pnb', 'bank of baroda', 'canara bank',
    'union bank', 'indian bank', 'central bank', 'idfc first bank',
    'bandhan bank', 'au small finance', 'rbl bank', 'federal bank',
    'bajaj finserv', 'bajaj finance', 'hdfc', 'lic housing', 'dhfl',
    
    # Real Estate
    'dlf', 'godrej properties', 'oberoi realty', 'prestige', 'sobha',
    'brigade', 'mahindra lifespaces', 'lodha', 'indiabulls real estate',
    
    # Media & Entertainment
    'zee entertainment', 'sun tv', 'tv today', 'network18', 'zee media',
    'disney', 'star india', 'sony', 'viacom18',
    
    # E-commerce & Internet
    'zomato', 'nykaa', 'paytm', 'policybazaar', 'delhivery', 'info edge',
    'just dial', 'indiamart', 'makemytrip', 'yatra',
    
    # Airlines
    'indigo', 'spicejet', 'air india', 'vistara', 'air asia',
    
    # Telecom
    'bharti airtel', 'reliance jio', 'vodafone idea', 'vi', 'bsnl',
    
    # Energy
    'reliance', 'ongc', 'oil india', 'gail', 'petronet lng',
    'indian oil', 'hpcl', 'bpcl', 'mahanagar gas', 'gujarat gas',
    
    # Power
    'ntpc', 'nhpc', 'power grid', 'tata power', 'adani power',
    'reliance power', 'torrent power', 'cesc', 'adani transmission',
    
    # Infrastructure
    'lt', 'l&t', 'larsen & toubro', 'irb infrastructure', 'mep infrastructure',
    'adani ports', 'gujarat port', 'container corporation',
    
    # Metals & Mining
    'tata steel', 'jsw steel', 'sail', 'hindalco', 'vedanta',
    'hindustan zinc', 'hzl', 'national aluminium', 'nalco', 'coal india',
    
    # Cement
    'ultratech', 'ambuja', 'acc', 'shree cement', 'dalmia cement',
    'ramco cements', 'india cements', 'orient cement',
    
    # Chemicals
    'tata chemicals', 'upl', 'rallis', 'pi industries', 'coromandel',
    'ghcl', 'deepak nitrite', 'alkem', 'vinati organics',
    
    # Textiles
    'grasim', 'aditya birla', 'welspun', 'trident', 'arvind',
    
    # Paints
    'asian paints', 'berger paints', 'kansai nerolac', 'indigo paints',
    'akzo nobel', 'shalimar paints',
    
    # Capital Goods
    'bhel', 'bharat electronics', 'bel', 'suzlon', 'inox wind',
    'thermax', 'voltas', 'bluestar', 'hitachi',
    
    # Consumer Durables
    'whirlpool', 'lg', 'samsung', 'godrej appliances', 'voltas',
    'bluestar', 'hitachi', 'daikin',
    
    # Healthcare
    'apollo hospitals', 'fortis', 'max healthcare', 'narayana hrudayalaya',
    'dr lal pathlabs', 'metropolis', 'thyrocare',
    
    # Education
    'extramarks', 'vedantu', 'byju', 'unacademy', 'whitehat jr',
    
    # Agriculture
    'upl', 'coromandel', 'rallis', 'pi industries', 'dhanuka',
    'bayer crop', 'syngenta', 'rallis',
}

# Indian Stock Market Indices
INDIAN_INDICES = {
    'nifty', 'sensex', 'bank nifty', 'nifty 50', 'nifty bank',
    'nifty it', 'nifty pharma', 'nifty auto', 'nifty fmcg',
    'nifty metal', 'nifty energy', 'nifty infra', 'nifty psu bank',
    'nifty private bank', 'nifty midcap', 'nifty smallcap', 'nifty next 50',
    'nifty 100', 'nifty 200', 'nifty 500', 'nifty midcap 50',
    'nifty smallcap 50', 'nifty midcap 100', 'nifty smallcap 100',
    'bse sensex', 'bse 500', 'bse midcap', 'bse smallcap',
    'nse', 'bse', 'ncdx', 'mcx'
}

# Combine all Indian companies and indices
ALL_INDIAN_COMPANIES = INDIAN_COMPANIES | INDIAN_INDICES

# Export the main list (for backward compatibility)
COMMON_COMPANIES = ALL_INDIAN_COMPANIES


def get_companies_by_sector(sector: str = None) -> set:
    """
    Get companies by sector (if needed in future).
    Currently returns all companies.
    """
    return ALL_INDIAN_COMPANIES


def add_custom_companies(companies: list) -> None:
    """
    Add custom companies to the registry.
    Useful for adding company-specific names or variations.
    
    Args:
        companies: List of company names to add
    """
    global ALL_INDIAN_COMPANIES, COMMON_COMPANIES
    for company in companies:
        ALL_INDIAN_COMPANIES.add(company.lower())
    COMMON_COMPANIES = ALL_INDIAN_COMPANIES


def load_companies_from_file(file_path: str = None) -> None:
    """
    Load companies from a JSON file.
    Useful for maintaining a separate company list file.
    
    Args:
        file_path: Path to JSON file with companies list 
                   (defaults to config/india_companies_registry.json)
    """
    import json
    import os
    global ALL_INDIAN_COMPANIES, COMMON_COMPANIES
    
    if file_path is None:
        # Default to config/india_companies_registry.json relative to project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # Try india_companies_registry.json first, fallback to companies.json
        india_registry = os.path.join(project_root, 'config', 'india_companies_registry.json')
        if os.path.exists(india_registry):
            file_path = india_registry
        else:
            file_path = os.path.join(project_root, 'config', 'companies.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            companies = set(data.get('companies', []))
            # Replace existing companies with those from file (to use the registry as source of truth)
            ALL_INDIAN_COMPANIES = companies.copy()
            COMMON_COMPANIES = ALL_INDIAN_COMPANIES
            print(f"✓ Loaded {len(companies)} companies from {file_path}")
    except Exception as e:
        print(f"⚠ Error loading companies from file: {e}")
        print(f"  Using default company list instead.")


# Auto-load companies from registry file on import
# This ensures all analyzers use the latest company list
# Must be called after load_companies_from_file is defined
try:
    load_companies_from_file()
except:
    # If loading fails, use default list
    pass


if __name__ == '__main__':
    print(f"Total companies in registry: {len(ALL_INDIAN_COMPANIES)}")
    print(f"Indian companies: {len(INDIAN_COMPANIES)}")
    print(f"Indices: {len(INDIAN_INDICES)}")
    print("\nSample companies:")
    for i, company in enumerate(sorted(ALL_INDIAN_COMPANIES)):
        if i < 20:
            print(f"  - {company}")
        else:
            break
    print("  ...")

