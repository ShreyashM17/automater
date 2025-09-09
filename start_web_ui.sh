#!/bin/bash

# Text Replacer Web UI Startup Script

echo "🚀 Starting Text Replacer Web UI..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "🔍 Checking dependencies..."
pip list | grep -q "Flask" || {
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
}

# Start the web application
echo "🌐 Starting web server..."
echo "   URL: http://localhost:5001"
echo "   Press Ctrl+C to stop"
echo ""

python app.py
