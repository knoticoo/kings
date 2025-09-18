#!/bin/bash

# Fix Permissions Script for VPS
# This script fixes common permission issues

echo "🔧 Fixing Permissions for King's Choice App"
echo "==========================================="

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"

# Fix file permissions
echo "📁 Fixing file permissions..."

# Make scripts executable
chmod +x *.sh 2>/dev/null || true
chmod +x *.py 2>/dev/null || true

# Fix directory permissions
chmod 755 . 2>/dev/null || true
chmod 755 templates 2>/dev/null || true
chmod 755 static 2>/dev/null || true
chmod 755 routes 2>/dev/null || true

# Fix Python files
find . -name "*.py" -exec chmod 644 {} \; 2>/dev/null || true

# Fix database file permissions
if [ -f "kings_choice.db" ]; then
    chmod 664 kings_choice.db 2>/dev/null || true
    echo "✅ Database file permissions fixed"
fi

# Create necessary directories with proper permissions
mkdir -p user_databases logs static/css static/js static/icons
mkdir -p templates/auth templates/admin templates/feedback
mkdir -p templates/modern/alliances templates/modern/events templates/modern/players
mkdir -p translations/en/LC_MESSAGES translations/ru/LC_MESSAGES

chmod 755 user_databases logs 2>/dev/null || true
chmod 755 static templates translations 2>/dev/null || true

echo "✅ Directory permissions fixed"

# Check if we can write to current directory
if [ -w . ]; then
    echo "✅ Current directory is writable"
else
    echo "❌ Current directory is not writable"
    echo "   Try: sudo chown -R $USER:$USER ."
    echo "   Or: sudo chmod -R 755 ."
fi

# Check Python executable permissions
if [ -x "venv/bin/python" ]; then
    echo "✅ Virtual environment Python is executable"
else
    echo "⚠️  Virtual environment Python is not executable"
    chmod +x venv/bin/python 2>/dev/null || true
fi

# Check if we can run Python
if python3 --version >/dev/null 2>&1; then
    echo "✅ Python3 is accessible"
else
    echo "❌ Python3 is not accessible"
    echo "   Try: sudo apt install python3 python3-pip python3-venv"
fi

echo ""
echo "🎯 Permission fix completed!"
echo ""
echo "If you still get permission denied errors:"
echo "1. Try: sudo chown -R $USER:$USER ."
echo "2. Try: sudo chmod -R 755 ."
echo "3. Try running with: python3 start_app_safe.py"
