#!/bin/bash

# King's Choice Management App - Server Startup Script
# This script sets up the virtual environment and starts the Flask server

echo "🚀 Starting King's Choice Management Web App..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/lib/python*/site-packages/flask" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the Flask application
echo "🌐 Starting Flask server on http://0.0.0.0:5001"
python3 app.py