# Company Registry Guide

## Overview

The company registry system centralizes all Indian stock market company names in one place, making it easy to maintain and update without modifying multiple files.

## Architecture

### 1. `company_registry.py` (Python Module)
- **Primary source**: Contains all company names as Python sets
- **Easy to import**: All analyzers import from this file
- **Programmatic access**: Can add companies dynamically

### 2. `companies.json` (JSON File)
- **Alternative source**: JSON format for easy editing
- **Can be loaded**: Use `load_companies_from_file()` function
- **Human-readable**: Easy to edit manually

## Usage

### For Analyzers (Recommended)

All sentiment analyzers should import from `company_registry.py`:

```python
from company_registry import COMMON_COMPANIES

# Use in your analyzer
for company in COMMON_COMPANIES:
    if company in text.lower():
        # Found company mention
        pass
```

### Adding Companies

#### Method 1: Edit `company_registry.py` (Recommended)

```python
# In company_registry.py, add to INDIAN_COMPANIES set
INDIAN_COMPANIES = {
    # ... existing companies ...
    'new company name',
    'another company',
}
```

#### Method 2: Use JSON File

Edit `companies.json`:
```json
{
  "companies": [
    "reliance",
    "tcs",
    "new company name"
  ]
}
```

Then load it:
```python
from company_registry import load_companies_from_file
load_companies_from_file('companies.json')
```

#### Method 3: Programmatically Add

```python
from company_registry import add_custom_companies

add_custom_companies(['new company', 'another company'])
```

## Updating Existing Analyzers

To update existing analyzers to use the centralized registry:

### Before:
```python
COMMON_COMPANIES = {
    'reliance', 'tcs', 'infosys', ...
}
```

### After:
```python
from company_registry import COMMON_COMPANIES
# That's it! No need to define the list again
```

## Benefits

1. **Single Source of Truth**: One file to update, all analyzers benefit
2. **Easy Maintenance**: Add/remove companies in one place
3. **Consistency**: All analyzers use the same company list
4. **Version Control**: Track changes to company list separately
5. **Flexibility**: Can load from JSON or add programmatically

## File Structure

```
stock-score-ai/
├── company_registry.py          # Main registry (Python)
├── companies.json               # Alternative JSON format
├── stock_sentiment_analyzer.py  # Imports from registry
├── sentiment_analyzer_textblob.py  # Imports from registry
├── sentiment_analyzer_vader.py    # Imports from registry
└── ... (other analyzers)
```

## Migration Steps

1. **Update each analyzer** to import from `company_registry.py`:
   ```python
   # Remove local COMMON_COMPANIES definition
   # Add: from company_registry import COMMON_COMPANIES
   ```

2. **Test**: Run analyzers to ensure they still work

3. **Update company list**: Add/remove companies in `company_registry.py` only

## Best Practices

1. **Use lowercase**: All company names should be lowercase for matching
2. **Include variations**: Add common name variations (e.g., "tata motors", "tata")
3. **Update regularly**: Add new companies as they become relevant
4. **Document additions**: Comment why you're adding specific companies
5. **Test after changes**: Verify analyzers still detect companies correctly

## Example: Adding a New Company

```python
# In company_registry.py

INDIAN_COMPANIES = {
    # ... existing companies ...
    
    # New IPO - added 2025-11-15
    'new ipo company',
    'newipo',  # Ticker variation
}
```

Then all analyzers automatically detect this company!

## Troubleshooting

### Company not detected?
1. Check if it's in `company_registry.py`
2. Verify spelling (case-insensitive matching)
3. Check for word boundaries in matching logic

### Want to add US stocks?
Create a separate registry file:
```python
# us_company_registry.py
US_COMPANIES = {'nvidia', 'apple', ...}
```

Then import both:
```python
from company_registry import ALL_INDIAN_COMPANIES
from us_company_registry import US_COMPANIES
ALL_COMPANIES = ALL_INDIAN_COMPANIES | US_COMPANIES
```

## Current Status

- ✅ `company_registry.py` created with Indian companies
- ✅ `companies.json` created
- ✅ `comprehensive_stock_analyzer.py` updated to use registry
- ⏳ Other analyzers can be updated gradually (backward compatible)

