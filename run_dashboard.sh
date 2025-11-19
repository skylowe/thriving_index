#!/bin/bash
# Run the Virginia Rural Thriving Index Dashboard

echo "Virginia Rural Thriving Index Dashboard"
echo "========================================"
echo ""

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Streamlit not found. Installing dependencies..."
    echo ""
    pip3 install -r requirements.txt
    echo ""
fi

echo "Starting dashboard..."
echo "The dashboard will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run dashboard.py
