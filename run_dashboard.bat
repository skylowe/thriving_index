@echo off
REM Run the Virginia Rural Thriving Index Dashboard

echo Virginia Rural Thriving Index Dashboard
echo ========================================
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found. Installing dependencies...
    echo.
    pip install -r requirements.txt
    echo.
)

echo Starting dashboard...
echo The dashboard will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run dashboard.py
