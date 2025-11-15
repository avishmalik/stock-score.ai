# Hindi/Hinglish Sentiment Analysis Guide

This workflow transcribes Hindi/Hinglish audio **without translating to English** and analyzes sentiment directly using XLM-RoBERTa (multilingual model).

## Why This Approach?

- **No Translation Loss**: Avoids translation artifacts that can affect sentiment accuracy
- **Direct Analysis**: Analyzes sentiment from original Hindi/Hinglish text
- **Better Accuracy**: XLM-RoBERTa understands multiple languages including Hindi
- **Faster**: Skips the translation step

## How It Works

1. **Transcription**: Uses Whisper with `task="transcribe"` (not `translate`)
   - Keeps original Hindi/Hinglish text
   - No English translation

2. **Sentiment Analysis**: Uses XLM-RoBERTa multilingual model
   - Understands Hindi, Hinglish, and English
   - Analyzes sentiment directly from original text

## Installation

```bash
# Required dependencies
pip install openai-whisper transformers torch matplotlib protobuf sentencepiece
```

**Note**: First run will download:
- Whisper model (~150MB-3GB depending on size)
- XLM-RoBERTa model (~500MB)

## Usage

### Option 1: Transcribe Audio and Analyze

```bash
python hindi_sentiment_analyzer.py path/to/audio.mp3
```

This will:
1. Transcribe audio (keeping Hindi/Hinglish)
2. Analyze sentiment using XLM-RoBERTa
3. Save results to `downloads/analysis/`

### Option 2: Analyze Existing Hindi Transcriptions

If you already have Hindi/Hinglish transcriptions:

```bash
python hindi_sentiment_analyzer.py --analyze-only
```

Looks for files ending with `_hindi_transcribed.txt` in `downloads/text_files/`

### Option 3: Custom Directories

```bash
python hindi_sentiment_analyzer.py audio.mp3 \
    --text-dir downloads/text_files \
    --output-dir downloads/analysis \
    --whisper-model base
```

## Output Files

- **Transcription**: `{filename}_hindi_transcribed.txt` (in original Hindi/Hinglish)
- **Analysis**: `sentiment_xlmroberta_hindi_predictions.json`
- **Chart**: `sentiment_xlmroberta_hindi_chart.png`

## Example Workflow

```bash
# 1. Transcribe Hindi/Hinglish audio (no translation)
python hindi_sentiment_analyzer.py downloads/audio/stock_news.mp3

# Output:
# - downloads/text_files/stock_news_hindi_transcribed.txt (Hindi/Hinglish text)
# - downloads/analysis/sentiment_xlmroberta_hindi_predictions.json
# - downloads/analysis/sentiment_xlmroberta_hindi_chart.png
```

## Comparison with Translation Approach

| Approach | Translation Step | Model | Pros | Cons |
|----------|-----------------|-------|------|------|
| **Current (Translation)** | Yes (Hindi→English) | FinBERT/TextBlob | Works with English models | Translation artifacts |
| **New (No Translation)** | No | XLM-RoBERTa | No translation loss, direct analysis | Requires multilingual model |

## Model Details

- **Whisper**: Speech-to-text (transcribe only, no translate)
- **XLM-RoBERTa**: `cardiffnlp/twitter-xlm-roberta-base-sentiment`
  - Trained on multilingual Twitter data
  - Supports 100+ languages including Hindi
  - Returns: positive, negative, neutral labels

## Tips

1. **For Hindi/Hinglish audio**: Use this workflow to avoid translation artifacts
2. **For English audio**: Use regular sentiment analyzers (FinBERT, TextBlob, etc.)
3. **Mixed content**: XLM-RoBERTa handles Hinglish (Hindi+English mix) well
4. **Model size**: Use `base` Whisper model for good balance of speed/accuracy

## Troubleshooting

- **No Hindi transcriptions found**: Make sure files end with `_hindi_transcribed.txt`
- **Model download fails**: Check internet connection (required for first run)
- **Memory issues**: Use smaller Whisper model (`tiny` or `base`)

