#!/bin/bash

# VPS Startup Script with SubUser Migration
# This script ensures the database is migrated before starting the application

echo "🚀 Starting King's Choice Management App on VPS"
echo "=============================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python3."
    exit 1
fi

# Check if database file exists
if [ ! -f "kings_choice.db" ]; then
    echo "❌ Database file not found. Please check your setup."
    exit 1
fi

# Run migration script
echo "🔧 Running database migration..."
python3 vps_subuser_migration.py

if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully"
else
    echo "❌ Migration failed. Please check the error messages above."
    exit 1
fi

# Kill any existing Python processes
echo "🔄 Stopping any existing processes..."
pkill -f python3 || true

# Wait a moment
sleep 2

# Start the application
echo "🚀 Starting application..."
python3 app.py

echo "✅ Application started successfully!"
echo "🌐 Access your app at: http://your-vps-ip:5000"
