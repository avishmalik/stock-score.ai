#!/usr/bin/env python3
"""
Company Registry
Centralized list of Indian stock market companies and indices.
All sentiment analyzers should import from this file to maintain consistency.
"""

import re

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


def get_sorted_companies() -> list:
    """
    Get companies sorted by length (longest first).
    This helps match longer company names before shorter ones to avoid partial matches.
    """
    return sorted(COMMON_COMPANIES, key=lambda x: (-len(x), x))


# Common words to exclude from matching (to avoid false positives)
# These are short abbreviations that commonly appear as parts of English words
COMMON_WORDS_TO_EXCLUDE = {
    'fact', 'idea', 'act', 'art', 'it', 'is', 'as', 'at', 'an', 'am', 'if', 'in', 'on', 'or',
    'be', 'by', 'do', 'go', 'he', 'me', 'my', 'no', 'of', 'so', 'to', 'up', 'we', 'us',
    'acc',  # matches "according", "account", etc.
    'bel',  # matches "believe", "below", etc.
    'upl',  # matches "uplift", "upload", etc. (but UPL is a real company, so need context check)
}

# Financial context keywords that indicate a real company mention
FINANCIAL_CONTEXT_KEYWORDS = {
    'stock', 'stocks', 'share', 'shares', 'company', 'companies', 'firm', 'firms',
    'bank', 'banks', 'banking', 'financial', 'finance', 'trading', 'trade', 'market', 'markets',
    'revenue', 'profit', 'loss', 'earnings', 'quarter', 'results', 'guidance', 'upgrade', 'downgrade',
    'price', 'prices', 'target', 'buy', 'sell', 'hold', 'rating', 'analyst', 'analysts',
    'ipo', 'listing', 'dividend', 'split', 'merger', 'acquisition', 'deal', 'contract',
    'growth', 'decline', 'rise', 'fall', 'surge', 'plunge', 'rally', 'crash',
    'nifty', 'sensex', 'index', 'indices', 'bse', 'nse', 'exchange',
    'crore', 'lakh', 'rupees', 'rs', 'percent', '%', 'basis points', 'bps',
    'q1', 'q2', 'q3', 'q4', 'fy', 'year', 'quarterly', 'annual',
    'ceo', 'md', 'chairman', 'management', 'board', 'director',
}

def create_company_aliases() -> dict:
    """
    Create aliases mapping common full names to registry abbreviations.
    Helps match "Bharat Dynamics" -> "bdl", "Muthoot Finance" -> "muthootfin", etc.
    """
    aliases = {
        # Full name -> registry abbreviation
        'bharat dynamics': 'bdl',
        'muthoot finance': 'muthootfin',
        'ipca labs': 'ipcalab',
        'ipca': 'ipcalab',
        'jubilant food': 'jublfood',
        'jubilant': 'jublfood',
        'pine labs': 'pinelabs',
        'hcl tech': 'hcl',
        'hcl technologies': 'hcl',
        'tata consultancy': 'tcs',
        'tata consultancy services': 'tcs',
        'sun pharma': 'sunpharma',
        'dr reddy': 'drreddy',
        'asian paints': 'asianpaint',
        'axis bank': 'axisbank',
        'kotak bank': 'kotakbank',
        'kotak mahindra': 'kotakbank',
        'hdfc bank': 'hdfcbank',
        'icici bank': 'icicibank',
        'sbi bank': 'sbin',
        'state bank': 'sbin',
        'bharti airtel': 'bhartiartl',
        'adani enterprises': 'adanient',
        'adani ports': 'adaniports',
        'adani power': 'adanipower',
        'adani green': 'adanigreen',
        'adani transmission': 'adanitrans',
        'power grid': 'powergrid',
        'coal india': 'coalindia',
        'oil india': 'oil',
        'indian oil': 'ioc',
        'bank of baroda': 'bankbaroda',
        'canara bank': 'canbk',
        'union bank': 'unionbank',
        'pnb': 'pnb',
        'punjab national bank': 'pnb',
        'idfc first bank': 'idfcfirstb',
        'bandhan bank': 'bandhanbnk',
        'yes bank': 'yesbank',
        'federal bank': 'federalbnk',
        'rbl bank': 'rblbank',
        'apollo hospitals': 'apollohosp',
        'max healthcare': 'maxhealth',
        'dr lal pathlabs': 'lalpathlab',
        'bharat electronics': 'bel',
        'bharat heavy electricals': 'bhel',
        'bharat forge': 'bharatforg',
        'larsen & toubro': 'lt',
        'l&t': 'lt',
        'mahindra & mahindra': 'm&m',
        'm&m': 'm&m',
        'grasim industries': 'grasim',
        'ultratech cement': 'ultratech',
        'ambuja cements': 'ambujacem',
        'shree cement': 'shreecement',
        'tata motors': 'tatamotors',
        'tata steel': 'tatasteel',
        'tata power': 'tatapower',
        'jsw steel': 'jswsteel',
        'vedanta limited': 'vedanta',
        'hindalco industries': 'hindalco',
        'national aluminium': 'nalco',
        'hindustan zinc': 'hzl',
        'nhpc': 'nhpc',
        'ntpc': 'ntpc',
        'sjvn': 'sjvn',
        'irfc': 'irfc',
        'ircon': 'ircon',
        'rvnl': 'rvnl',
        'bel': 'bel',
        'bhel': 'bhel',
        'bdl': 'bdl',
    }
    return aliases


def validate_company_match(company: str, sentence: str, sentence_lower: str) -> tuple[bool, float, bool]:
    """
    Validate if a company match is likely correct or a false positive.
    Returns (is_valid, confidence_score, likely_false_positive) where:
    - is_valid: whether to include this match
    - confidence_score: 0.0 to 1.0 indicating match quality
    - likely_false_positive: True if this is likely a false positive (e.g., "acc" in "according")
    
    Checks:
    1. If company is a common word that appears in non-financial contexts
    2. If the sentence contains financial context keywords
    3. If the match appears as part of a larger word (likely false positive)
    """
    company_lower = company.lower()
    confidence = 1.0
    likely_false_positive = False
    
    # Check if company name is too short and appears as part of common words
    if len(company_lower) <= 3:
        # Check if it appears as part of a larger word
        words_in_sentence = re.findall(r'\b\w+\b', sentence_lower)
        for word in words_in_sentence:
            if company_lower in word and word != company_lower:
                # It's part of a larger word - check if it's a common word
                common_prefixes = {
                    'acc': ['according', 'account', 'accepted', 'access', 'accent', 'accuser', 'accessing'],
                    'bel': ['believe', 'below', 'belong', 'bell', 'belongs', 'believed'],
                    'upl': ['uplift', 'upload', 'upland'],
                    'fact': ['factory', 'factor', 'factual', 'fact', 'factors'],
                    'idea': ['ideal', 'ideally', 'ideas', 'ideals'],
                }
                if company_lower in common_prefixes:
                    for common_word in common_prefixes[company_lower]:
                        # Check if word starts with the company name
                        if word.startswith(company_lower):
                            # Check if the next few chars match a common word pattern
                            if len(word) > len(company_lower):
                                next_chars = word[len(company_lower):len(company_lower)+3]
                                # If it matches common word patterns, likely false positive
                                if any(common_word.startswith(company_lower + next_chars[:min(2, len(next_chars))]) 
                                       for common_word in common_prefixes[company_lower]):
                                    # Likely false positive - mark it
                                    likely_false_positive = True
                                    confidence = 0.1
                                    break
                    if likely_false_positive:
                        break
    
    # Boost confidence if financial context keywords are present
    financial_context_count = sum(1 for keyword in FINANCIAL_CONTEXT_KEYWORDS if keyword in sentence_lower)
    if financial_context_count > 0:
        # Increase confidence based on number of financial keywords
        confidence = min(1.0, confidence + (financial_context_count * 0.15))
        # If we have financial context, it's less likely to be a false positive
        if financial_context_count >= 2:
            likely_false_positive = False
    elif len(company_lower) <= 3:
        # Short abbreviation without financial context - lower confidence
        confidence = max(0.2, confidence - 0.3)
        if not likely_false_positive:
            # Mark as suspicious if no financial context
            likely_false_positive = True
    
    # Check if company name appears as standalone word (higher confidence)
    standalone_pattern = r'\b' + re.escape(company_lower) + r'\b'
    is_standalone = re.search(standalone_pattern, sentence_lower)
    
    # Special handling for common words that appear standalone in non-financial contexts
    if is_standalone and len(company_lower) <= 4:
        # Check for common non-financial phrases
        non_financial_phrases = {
            'fact': ['in fact', 'the fact', 'fact is', 'fact that', 'as a matter of fact', 'well in fact'],
            'idea': ['have an idea', 'the idea', 'idea is', 'idea that', 'no idea', 'good idea', 'ideas', 'new ideas', 'bottom of ideas'],
        }
        if company_lower in non_financial_phrases:
            for phrase in non_financial_phrases[company_lower]:
                if phrase in sentence_lower:
                    # Likely false positive - common phrase usage
                    likely_false_positive = True
                    confidence = 0.2
                    break
    
    if is_standalone:
        confidence = min(1.0, confidence + 0.2)
        # Standalone word is less likely to be false positive (unless it's a common phrase)
        if confidence > 0.5 and not likely_false_positive:
            likely_false_positive = False
    
    # Special cases: if company is in registry and has financial context, trust it more
    if company_lower in COMMON_COMPANIES and financial_context_count > 0:
        confidence = max(confidence, 0.6)
        # Override false positive flag if we have strong financial context
        if financial_context_count >= 2:
            likely_false_positive = False
    
    # If marked as likely false positive, require higher confidence threshold
    if likely_false_positive:
        is_valid = confidence >= 0.5  # Higher threshold for suspicious matches
    else:
        is_valid = confidence >= 0.4  # Normal threshold
    
    return is_valid, confidence, likely_false_positive


def find_company_mentions(text: str, min_confidence: float = 0.4) -> dict:
    """
    Find all company mentions in text using flexible matching.
    Returns dict mapping company names to list of sentences where they appear.
    
    This function:
    - Matches companies case-insensitively
    - Handles partial matches (e.g., "bharat" matches "bharatforg", "bdl")
    - Handles abbreviations (BDL -> bdl, IPCA Labs -> ipcalab)
    - Sorts by length (longest first) to match longer names before shorter ones
    - Handles multi-word company names flexibly
    """
    from collections import defaultdict
    
    text_lower = text.lower()
    company_mentions = defaultdict(list)
    
    # Get aliases for common full names
    aliases = create_company_aliases()
    
    # Get companies sorted by length (longest first) to avoid partial matches
    sorted_companies = sorted(COMMON_COMPANIES, key=lambda x: (-len(x), x))
    
    # Split into sentences
    sentences = re.split(r'[.!?।]+', text)
    
    # Track which companies have been found to avoid duplicates
    found_companies = set()
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        sentence_clean = sentence.strip()
        
        if len(sentence_clean) < 10:  # Skip very short sentences
            continue
        
        # First, check aliases (full names -> abbreviations)
        for full_name, abbrev in aliases.items():
            if abbrev in COMMON_COMPANIES:
                # Check if full name appears in sentence
                full_name_words = full_name.split()
                if len(full_name_words) > 1:
                    # Multi-word: check if all words appear close together
                    all_found = True
                    positions = []
                    for word in full_name_words:
                        pattern = r'\b' + re.escape(word)
                        match = re.search(pattern, sentence_lower)
                        if match:
                            positions.append(match.start())
                        else:
                            all_found = False
                            break
                    
                    if all_found and positions:
                        max_pos = max(positions)
                        min_pos = min(positions)
                        if max_pos - min_pos < 50:  # Words close together
                            sentence_key = f"{abbrev}:{sentence_clean[:50]}"
                            if sentence_key not in found_companies:
                                company_mentions[abbrev].append(sentence_clean)
                                found_companies.add(sentence_key)
                else:
                    # Single word alias
                    if re.search(r'\b' + re.escape(full_name) + r'\b', sentence_lower):
                        sentence_key = f"{abbrev}:{sentence_clean[:50]}"
                        if sentence_key not in found_companies:
                            company_mentions[abbrev].append(sentence_clean)
                            found_companies.add(sentence_key)
        
        # Then check direct company matches
        for company in sorted_companies:
            company_lower = company.lower()
            
            # Skip if already found via alias
            sentence_key = f"{company}:{sentence_clean[:50]}"
            if sentence_key in found_companies:
                continue
            
            matched = False
            words = company_lower.split()
            
            # Skip very short company names that are common words (to avoid false positives)
            if len(company_lower) <= 3 and company_lower in COMMON_WORDS_TO_EXCLUDE:
                continue
            
            # Strategy 1: Exact match (with word boundaries)
            exact_pattern = r'\b' + re.escape(company_lower) + r'\b'
            if re.search(exact_pattern, sentence_lower):
                matched = True
            else:
                # Strategy 2: Partial match - company name appears as start of a word
                # e.g., "bdl" matches "BDL", "hcl" matches "HCL Tech"
                # But skip if it's a very short common word
                if len(company_lower) >= 4 or company_lower not in COMMON_WORDS_TO_EXCLUDE:
                    partial_pattern = r'\b' + re.escape(company_lower) + r'(\w*)?'
                    if re.search(partial_pattern, sentence_lower):
                        matched = True
                
                if not matched:
                    # Strategy 3: Multi-word matching
                    if len(words) > 1:
                        all_words_found = True
                        word_positions = []
                        
                        for word in words:
                            # Skip very short words that are common
                            if len(word) <= 2 and word in COMMON_WORDS_TO_EXCLUDE:
                                continue
                            pattern = r'\b' + re.escape(word)
                            match = re.search(pattern, sentence_lower)
                            if match:
                                word_positions.append(match.start())
                            else:
                                all_words_found = False
                                break
                        
                        if all_words_found and word_positions:
                            max_pos = max(word_positions)
                            min_pos = min(word_positions)
                            if max_pos - min_pos < 50:
                                matched = True
            
            if matched:
                # Validate the match to filter out false positives
                is_valid, match_confidence, is_false_positive = validate_company_match(company, sentence_clean, sentence_lower)
                if is_valid:
                    # Store with metadata for later filtering
                    company_mentions[company].append({
                        'sentence': sentence_clean,
                        'confidence': match_confidence,
                        'likely_false_positive': is_false_positive
                    })
                    found_companies.add(sentence_key)
    
    # Deduplicate: if both "asian paints" and "asianpaint" are found, keep only one
    # Prefer the form that exists in COMMON_COMPANIES
    deduplicated = {}
    seen_bases = set()
    
    for company, contexts in company_mentions.items():
        # Create base form (remove spaces, lowercase)
        base_form = company.replace(' ', '').lower()
        
        if base_form not in seen_bases:
            # First occurrence - use it
            deduplicated[company] = contexts
            seen_bases.add(base_form)
        else:
            # Duplicate found - check which one is in registry and prefer that
            # If current one is in registry and previous wasn't, replace
            if company in COMMON_COMPANIES:
                # Find and replace the previous entry
                for prev_company in list(deduplicated.keys()):
                    prev_base = prev_company.replace(' ', '').lower()
                    if prev_base == base_form and prev_company not in COMMON_COMPANIES:
                        # Replace with the one in registry
                        deduplicated[company] = deduplicated.pop(prev_company)
                        break
                else:
                    # Both in registry or current not in registry - merge contexts
                    for prev_company in deduplicated.keys():
                        prev_base = prev_company.replace(' ', '').lower()
                        if prev_base == base_form:
                            # Merge contexts, prefer the shorter name
                            if len(company) < len(prev_company):
                                deduplicated[company] = list(set(deduplicated.pop(prev_company) + contexts))
                            else:
                                deduplicated[prev_company].extend(contexts)
                                deduplicated[prev_company] = list(set(deduplicated[prev_company]))
                            break
    
    # Convert back to simple format (list of sentences) but keep metadata available
    # For backward compatibility, return simple dict, but analyzers can access metadata
    final_result = {}
    for company, items in deduplicated.items():
        if isinstance(items[0], dict):
            # New format with metadata
            final_result[company] = [item['sentence'] for item in items]
            # Store metadata separately for analyzers to use
            final_result[f'__meta_{company}'] = {
                'confidences': [item['confidence'] for item in items],
                'false_positives': [item['likely_false_positive'] for item in items],
                'avg_confidence': sum(item['confidence'] for item in items) / len(items),
                'has_false_positive': any(item['likely_false_positive'] for item in items)
            }
        else:
            # Old format (strings)
            final_result[company] = items
    
    return final_result


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
