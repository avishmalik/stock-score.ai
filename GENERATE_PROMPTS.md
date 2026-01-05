# How to Generate Prompts After Running Analyzers

## Quick Answer

After running the analyzers, simply run:

```bash
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate
python scripts/create_stock_report.py
```

This will generate:
- `downloads/reports/cursor_prompt.txt` - For Cursor (report format)
- `downloads/reports/chatgpt_prompt.txt` - For ChatGPT (detailed with full transcription)
- `downloads/reports/stock_analysis_report.txt` - Human-readable summary
- `downloads/reports/stock_analysis_summary.json` - Structured JSON data

---

## Step-by-Step Guide

### Step 1: Run Analyzers (if not already done)

```bash
# Run all sentiment analyzers
python scripts/run_all_analyzers.py
```

This creates analysis files in `downloads/analysis/`:
- `sentiment_*_predictions.json` (7 files)
- `sentiment_*_chart.png` (7 files)

### Step 2: Generate Prompts

```bash
# Generate reports and prompts
python scripts/create_stock_report.py
```

**Output:**
```
🔍 Loading analysis files...
✓ Loaded 7 analysis files
✓ Loaded transcription (53920 chars)

📊 Aggregating sentiment scores...
✓ Found 17 companies

📝 Generating report...
📝 Creating prompts...

💾 Saving files...
✓ Report saved to: downloads/reports/stock_analysis_report.txt
✓ Cursor prompt saved to: downloads/reports/cursor_prompt.txt
✓ ChatGPT prompt saved to: downloads/reports/chatgpt_prompt.txt
✓ JSON summary saved to: downloads/reports/stock_analysis_summary.json

📊 Token Estimates:
   Report: ~1206 tokens
   Cursor Prompt: ~1206 tokens (optimized)
   ChatGPT Prompt: ~6275 tokens (detailed)

✅ Report generation complete!
```

### Step 3: Use the Prompts

#### For Cursor:
```bash
# Open the cursor prompt
cat downloads/reports/cursor_prompt.txt
# Copy and paste into Cursor chat
```

#### For ChatGPT:
```bash
# Open the ChatGPT prompt
cat downloads/reports/chatgpt_prompt.txt
# Copy and paste into ChatGPT
# OR use the web interface button to copy & open ChatGPT
```

---

## Custom Paths (Optional)

If your files are in different locations:

```bash
python scripts/create_stock_report.py [analysis_dir] [text_dir] [output_dir]
```

Example:
```bash
python scripts/create_stock_report.py downloads/analysis downloads/text_files downloads/reports
```

---

## Complete Workflow

```bash
# 1. Activate virtual environment
cd /Users/avishmalik/Desktop/stock-score-ai
source venv/bin/activate

# 2. Run analyzers (if needed)
python scripts/run_all_analyzers.py

# 3. Generate prompts
python scripts/create_stock_report.py

# 4. Use prompts
# - Copy cursor_prompt.txt for Cursor
# - Copy chatgpt_prompt.txt for ChatGPT
```

---

## What Gets Generated

### `cursor_prompt.txt`
- **Size**: ~1,200 tokens
- **Content**: Stock analysis report format
- **Use**: Paste into Cursor chat for quick analysis

### `chatgpt_prompt.txt`
- **Size**: ~6,000+ tokens
- **Content**: Detailed prompt with full transcription
- **Use**: Paste into ChatGPT for comprehensive analysis

### `stock_analysis_report.txt`
- **Size**: ~1,200 tokens
- **Content**: Human-readable summary
- **Use**: Quick reference, manual review

### `stock_analysis_summary.json`
- **Content**: Structured JSON data
- **Use**: Programmatic access, integrations

---

## Troubleshooting

### Error: "No analysis files found"
**Solution:** Make sure you've run the analyzers first:
```bash
python scripts/run_all_analyzers.py
```

### Error: "No transcription found"
**Solution:** Ensure transcribed files exist in `downloads/text_files/`:
```bash
ls downloads/text_files/*_transcribed.txt
```

### Empty Report
**Solution:** Check that analysis files contain company data:
```bash
ls downloads/analysis/*_predictions.json
```

---

## Quick Reference

```bash
# Generate prompts (most common)
python scripts/create_stock_report.py

# View generated prompts
cat downloads/reports/cursor_prompt.txt
cat downloads/reports/chatgpt_prompt.txt

# Open in editor
open downloads/reports/chatgpt_prompt.txt
```

---

## Integration with Web Interface

If you used the web interface (`python src/web/app.py`), prompts are **automatically generated** after analysis completes. You don't need to run this script separately - the prompts will appear in the browser!

---

## Next Steps After Generating Prompts

1. **For Cursor**: Copy `cursor_prompt.txt` → Paste in Cursor → Get quick insights
2. **For ChatGPT**: Copy `chatgpt_prompt.txt` → Paste in ChatGPT → Get detailed analysis
3. **Or use web interface**: Click "Open ChatGPT" button to copy & open automatically



