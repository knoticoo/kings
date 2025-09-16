#!/usr/bin/env python3
"""
Optimized Startup Script for King's Choice Web App

This script starts the Flask application with all performance optimizations enabled.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        "app.py",
        "requirements.txt",
        "static/css/style.min.css",
        "optimize_database.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

def optimize_database():
    """Run database optimization if needed"""
    print("🔧 Checking database optimization...")
    try:
        result = subprocess.run([sys.executable, "optimize_database.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print("✅ Database optimization completed")
        else:
            print("⚠️  Database optimization had issues, but continuing...")
    except Exception as e:
        print(f"⚠️  Could not run database optimization: {e}")

def start_app():
    """Start the Flask application"""
    print("🚀 Starting King's Choice Web App with optimizations...")
    print("=" * 60)
    print("PERFORMANCE OPTIMIZATIONS ENABLED:")
    print("• Database indexes for faster queries")
    print("• API response caching (30s)")
    print("• Optimized database queries with JOINs")
    print("• Minified CSS for faster loading")
    print("• Reduced JavaScript auto-refresh (60s)")
    print("• Smart caching to avoid unnecessary requests")
    print("=" * 60)
    print()
    
    try:
        # Set environment variables for optimization
        os.environ['FLASK_ENV'] = 'production'
        os.environ['FLASK_DEBUG'] = 'False'
        
        # Start the Flask app
        subprocess.run([sys.executable, "app.py"], cwd=os.getcwd())
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down King's Choice Web App...")
    except Exception as e:
        print(f"❌ Error starting app: {e}")

def main():
    """Main function"""
    print("🎮 King's Choice Management Web App - Optimized Startup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("❌ Please ensure all required files are present")
        sys.exit(1)
    
    # Optimize database
    optimize_database()
    
    # Start the app
    start_app()

if __name__ == "__main__":
    main()