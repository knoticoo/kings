#!/bin/bash

# Simple test script to debug the startup issue

set -e

echo "=== Testing VPS Startup ==="
echo "Current directory: $(pwd)"
echo "Virtual environment path: $(pwd)/env"

# Check if virtual environment exists
if [ -d "env" ]; then
    echo "✓ Virtual environment directory exists"
else
    echo "✗ Virtual environment directory NOT found"
    exit 1
fi

# Check if activate script exists
if [ -f "env/bin/activate" ]; then
    echo "✓ activate script exists"
else
    echo "✗ activate script NOT found"
    exit 1
fi

# Try to activate virtual environment
echo "Attempting to activate virtual environment..."
source env/bin/activate

# Check if activation worked
echo "Python path: $(which python)"
echo "Python version: $(python --version)"

# Test Flask import
echo "Testing Flask import..."
if python -c "import flask; print('✓ Flask imported successfully')"; then
    echo "✓ Flask is available"
else
    echo "✗ Flask import failed"
    exit 1
fi

# Test app import
echo "Testing app import..."
if python -c "from app import app; print('✓ App imported successfully')"; then
    echo "✓ App can be imported"
else
    echo "✗ App import failed"
    exit 1
fi

echo "=== All tests passed! ==="
echo "The virtual environment is working correctly."