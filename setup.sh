#!/bin/bash
# Setup script for YouTube Audio Downloader
# Creates a virtual environment and installs dependencies

set -e  # Exit on error

echo "🚀 Setting up YouTube Audio Downloader..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check for ffmpeg
echo ""
echo "🔍 Checking for ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✓ ffmpeg is installed"
    ffmpeg -version | head -n 1
else
    echo "⚠️  Warning: ffmpeg is not installed"
    echo "   Install it with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate, run:"
echo "  deactivate"
echo ""

