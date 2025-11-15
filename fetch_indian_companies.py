import requests
import csv
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_from_nse_website():
    """
    Attempts to fetch company list from NSE website.
    """
    try:
        # NSE company list URL
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        # First, visit the main page to get cookies
        session.get("https://www.nseindia.com/", timeout=10)
        time.sleep(1)
        
        # Try to get Nifty 500 or similar broad index
        indices = ["NIFTY%20500", "NIFTY%20NEXT%2050", "NIFTY%20100", "NIFTY%20200"]
        all_companies = []
        
        for index in indices:
            try:
                url = f"https://www.nseindia.com/api/equity-stockIndices?index={index}"
                resp = session.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'data' in data:
                        for item in data['data']:
                            company_name = item.get('symbol', '').strip()
                            if company_name and company_name not in all_companies:
                                all_companies.append(company_name.lower())
                time.sleep(0.5)
            except Exception as e:
                print(f"Error fetching {index}: {e}")
                continue
        
        return all_companies[:300] if all_companies else None
    except Exception as e:
        print(f"Error fetching from NSE: {e}")
        return None

def fetch_from_screener_in():
    """
    Attempts to fetch top companies from screener.in using web scraping.
    """
    try:
        # Screener.in has lists of companies by market cap
        url = "https://www.screener.in/screens/599148/companies-by-market-cap/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        companies = []
        
        # Try to find company names in the page
        # Screener.in typically has company names in links or table cells
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            # Screener.in company links typically look like /company/COMPANYNAME/
            if '/company/' in href and text:
                company_name = href.split('/company/')[-1].strip('/').lower()
                if company_name and company_name not in companies:
                    companies.append(company_name)
        
        # Also try to find in table cells
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if cells:
                    # Usually company name is in first or second cell
                    for cell in cells[:2]:
                        text = cell.get_text(strip=True).lower()
                        if text and len(text) > 2 and text not in companies:
                            companies.append(text)
        
        return companies[:300] if companies else None
    except Exception as e:
        print(f"Error fetching from screener.in: {e}")
        return None

def fetch_from_csv_url(csv_url):
    """
    Fetches a CSV of listed companies and returns a list of company names.
    """
    try:
        resp = requests.get(csv_url, timeout=15)
        resp.raise_for_status()
        text = resp.text
        
        reader = csv.reader(text.splitlines())
        header = next(reader)
        
        # Find the column with company name
        name_col = None
        for i, col in enumerate(header):
            col_lower = col.lower()
            if 'company' in col_lower and 'name' in col_lower:
                name_col = i
                break
            elif 'name' in col_lower:
                name_col = i
                break
        
        if name_col is None:
            name_col = 0
        
        companies = []
        for row in reader:
            if len(row) > name_col:
                name = row[name_col].strip().lower()
                if name and name not in companies:
                    companies.append(name)
        
        return companies[:300] if companies else None
    except Exception as e:
        print(f"Error fetching from CSV URL: {e}")
        return None

def get_top_indian_companies():
    """
    Main function to fetch top 300 Indian companies using multiple methods.
    """
    print("Attempting to fetch Indian stock market companies...")
    
    # Method 1: Try NSE website
    print("Trying NSE website...")
    companies = fetch_from_nse_website()
    if companies and len(companies) >= 100:
        print(f"✓ Found {len(companies)} companies from NSE")
        return companies[:300]
    
    # Method 2: Try screener.in
    print("Trying screener.in...")
    companies = fetch_from_screener_in()
    if companies and len(companies) >= 100:
        print(f"✓ Found {len(companies)} companies from screener.in")
        return companies[:300]
    
    # Method 3: Use a curated list of top Indian companies as fallback
    print("Using curated list of top Indian companies...")
    top_companies = [
        "reliance", "tcs", "infosys", "hdfc bank", "icici bank", "sbi", "bharti airtel",
        "lt", "hcl technologies", "wipro", "maruti suzuki", "tata motors", "adani enterprises",
        "jsw steel", "vedanta", "hindalco", "m&m", "mahindra", "dlf", "grasim", "ultratech cement",
        "ambuja cements", "shree cement", "dabur", "hul", "itc", "asian paints", "berger paints",
        "nippon paint", "indigo", "spicejet", "lic", "axis bank", "kotak mahindra bank",
        "pnb", "rbl bank", "tata steel", "sail", "coal india", "ongc", "ioc", "bpcl", "hpcl",
        "zomato", "nykaa", "paytm", "policybazaar", "delhivery", "lupin", "dr reddy", "sun pharma",
        "cipla", "torrent pharma", "mankind pharma", "glenmark", "nhpc", "power grid", "ntpc",
        "suzlon", "adani green", "tata power", "upl", "coromandel", "rallis", "pi industries",
        "bajaj finance", "bajaj finserv", "hdfc life", "sbi life", "icici prudential",
        "nestle", "britannia", "titan", "tata consumer", "godrej consumer", "marico",
        "colgate", "p&g", "unilever", "hero motocorp", "bajaj auto", "eicher motors",
        "ashok leyland", "apollo tyres", "mrf", "ceat", "balkrishna industries",
        "tata chemicals", "ghcl", "deepak nitrite", "vinati organics", "sumitomo chemical",
        "alkem", "cadila", "biocon", "aurobindo pharma", "divis labs", "laurus labs",
        "natco pharma", "zydus", "alembic", "ajanta pharma", "ipca labs", "reddy labs",
        "bharat electronics", "bharat heavy electricals", "suzlon energy", "adani ports",
        "container corporation", "delhi airport", "indian railways", "irctc",
        "tata communications", "bharti airtel", "reliance jio", "vodafone idea",
        "adani transmission", "tata power", "torrent power", "renewable energy",
        "adani total gas", "indian oil", "gail", "petronet lng", "gujarat gas",
        "mahanagar gas", "castrol", "gulf oil", "hpcl", "mrpl",
        "hindustan zinc", "national aluminium", "jindal steel", "jsw energy",
        "adani power", "ntpc", "power grid", "nhpc", "suzlon", "inox wind",
        "renew", "greenko", "orient green", "websol energy", "indian energy exchange",
        "bse", "nse", "mcx", "ncdx", "metropolitan stock exchange",
        "hdfc asset management", "uti asset management", "sbi mutual fund",
        "icici prudential amc", "kotak mahindra amc", "axis bank", "yes bank",
        "idfc first bank", "federal bank", "south indian bank", "karnataka bank",
        "city union bank", "dcb bank", "bandhan bank", "au small finance bank",
        "equitas small finance", "ujjivan small finance", "suryoday small finance",
        "shriram finance", "bajaj finserv", "m&m financial", "cholamandalam",
        "tata capital", "l&t finance", "piramal enterprises", "edelweiss",
        "motilal oswal", "angel one", "icici securities", "hdfc securities",
        "kotak securities", "geojit", "india bulls", "centrum", "anand rathi",
        "aditya birla capital", "reliance capital", "future group", "d mart",
        "trent", "shoppers stop", "pantaloon", "lifestyle", "max", "westside",
        "reliance retail", "future retail", "spencer", "big bazaar", "croma",
        "tata steel", "jsw steel", "sail", "jindal steel", "essar steel",
        "hindalco", "vedanta", "hzl", "nalco", "moil", "ratnamani metals",
        "apollo hospitals", "fortis", "max healthcare", "narayana hrudayalaya",
        "aster dm", "dr lal pathlabs", "metropolis", "thyrocare", "lal pathlab",
        "cipla", "lupin", "dr reddy", "sun pharma", "torrent", "cadila", "biocon",
        "aurobindo", "divis", "laurus", "natco", "zydus", "alembic", "ajanta",
        "ipca", "reddy", "glenmark", "mankind", "alkem", "wockhardt", "pfizer",
        "abbott", "sanofi", "novartis", "gsk", "merck", "bayer", "roche",
        "tata consultancy", "infosys", "wipro", "hcl", "tech mahindra", "lt infotech",
        "mindtree", "mphasis", "cognizant", "accenture", "capgemini", "tcs",
        "persistent", "cyient", "lt technology", "zensar", "sonata", "newgen",
        "intellect", "ramco", "3i infotech", "niit", "aptech", "maveric",
        "tata elxsi", "ltimindtree", "cyient", "zoho", "freshworks", "chargebee"
    ]
    
    return top_companies[:300]

def generate_json(companies, description, last_updated):
    return {
        "description": description,
        "last_updated": last_updated,
        "companies": companies
    }

if __name__ == "__main__":
    print("=" * 60)
    print("Fetching Top 300 Indian Stock Market Companies")
    print("=" * 60)
    
    companies = get_top_indian_companies()
    
    if not companies:
        print("Error: Could not fetch company list")
        exit(1)
    
    # Get current date
    from datetime import datetime
    last_updated = datetime.now().strftime("%Y-%m-%d")
    
    output = generate_json(
        companies=companies,
        description="Indian Stock Market Companies Registry - Top 300 Companies",
        last_updated=last_updated
    )
    
    # Write to file
    output_file = "config/india_companies_registry.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Successfully wrote {len(companies)} companies to {output_file}")
    print(f"  Last updated: {last_updated}")
    print(f"  Description: {output['description']}")

