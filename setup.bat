@echo off
REM Setup script for YouTube Audio Downloader (Windows)
REM Creates a virtual environment and installs dependencies

echo 🚀 Setting up YouTube Audio Downloader...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed. Please install Python 3 first.
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install Python dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Check for ffmpeg
echo.
echo 🔍 Checking for ffmpeg...
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Warning: ffmpeg is not installed
    echo    Download from: https://ffmpeg.org/download.html
) else (
    echo ✓ ffmpeg is installed
    ffmpeg -version | findstr /C:"ffmpeg version"
)

echo.
echo ✅ Setup complete!
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate, run:
echo   deactivate
echo.

pause

