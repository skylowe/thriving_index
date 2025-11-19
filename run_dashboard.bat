@echo off
REM Run the Virginia Rural Thriving Index Dashboard

echo Virginia Rural Thriving Index Dashboard
echo ========================================
echo.

REM Check Python version
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)
echo.

REM Check if streamlit is installed
echo Checking for Streamlit...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found. Installing dependencies...
    echo This may take a few minutes...
    echo.
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    echo.
    echo Installation complete!
    echo.
)

REM Verify streamlit is now installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ERROR: Streamlit installation failed
    echo.
    echo Please try installing manually:
    echo   pip install streamlit plotly pandas numpy
    echo.
    pause
    exit /b 1
)

echo Starting dashboard...
echo The dashboard will open in your browser at http://localhost:8501
echo.
echo If the browser does not open automatically, copy this URL:
echo   http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run dashboard.py
