#!/bin/bash
# VPS Deployment Script for King's Choice Management App

echo "🚀 Deploying King's Choice Management App to VPS..."

# Set VPS environment variable
export KINGS_CHOICE_VPS=true

# Create the user databases directory if it doesn't exist
mkdir -p /root/kings/user_databases

# Set proper permissions
chmod 755 /root/kings/user_databases

echo "✅ VPS environment configured"
echo "📁 User databases directory: /root/kings/user_databases"
echo "🔧 Environment variable KINGS_CHOICE_VPS=true set"

echo ""
echo "🎉 Deployment ready!"
echo ""
echo "To start the application:"
echo "1. cd /root/kings"
echo "2. export KINGS_CHOICE_VPS=true"
echo "3. python3 app.py"
echo ""
echo "The application will now automatically:"
echo "✅ Use correct VPS database paths"
echo "✅ Create new user databases in /root/kings/user_databases/"
echo "✅ Work with existing user_1_knotico.db and user_3_julija.db files"