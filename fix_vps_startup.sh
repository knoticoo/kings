#!/bin/bash

# Quick VPS Fix Script
# This script fixes the most common VPS startup issues

echo "🔧 King's Choice App - VPS Quick Fix"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please run this script from the app directory."
    exit 1
fi

# Stop any running processes
echo "🔄 Stopping existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
sudo systemctl stop kings-choice.service 2>/dev/null || true

# Check Python and dependencies
echo "🐍 Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Installing..."
    sudo apt update && sudo apt install -y python3 python3-pip python3-venv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Fix database issues
echo "🗄️ Fixing database..."
python3 -c "
import os
import sys
sys.path.insert(0, '.')

from flask import Flask
from database import db, init_app, create_all_tables
from models import User, SubUser

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fix-key-12345'

# Initialize database
init_app(app)

with app.app_context():
    try:
        # Create all tables
        create_all_tables(app)
        print('✅ Database tables created/updated')
        
        # Check SubUser table specifically
        try:
            SubUser.query.first()
            print('✅ SubUser table is working')
        except Exception as e:
            print(f'⚠️  SubUser table issue: {e}')
            # Create SubUser table manually
            from sqlalchemy import text
            db.session.execute(text('''
                CREATE TABLE IF NOT EXISTS sub_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    parent_user_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    permissions TEXT DEFAULT '{}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    FOREIGN KEY (parent_user_id) REFERENCES users(id)
                )
            '''))
            db.session.commit()
            print('✅ SubUser table created manually')
        
        # Check users
        user_count = User.query.count()
        print(f'✅ Found {user_count} users')
        
    except Exception as e:
        print(f'❌ Database fix failed: {e}')
        sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database fix failed"
    exit 1
fi

# Test the application
echo "🧪 Testing application..."
python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from app import app
    print('✅ App imports successfully')
    
    # Test basic configuration
    print(f'  - Database: {app.config.get(\"SQLALCHEMY_DATABASE_URI\")}')
    print(f'  - Secret Key: {\"Set\" if app.config.get(\"SECRET_KEY\") else \"Not set\"}')
    
except Exception as e:
    print(f'❌ App test failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Application test failed"
    exit 1
fi

# Start the application
echo "🚀 Starting application..."
echo "   Access at: http://$(hostname -I | awk '{print $1}'):5000"
echo "   Press Ctrl+C to stop"

# Use the safe startup script
python3 start_app_safe.py
