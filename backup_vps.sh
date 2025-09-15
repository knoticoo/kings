#!/bin/bash

# VPS Database Backup Script
# This script helps you backup your database from VPS before reinstalling

echo "🔄 King's Choice Database Backup Script"
echo "========================================"

# Configuration
DB_PATH="/path/to/your/kings_choice.db"  # Update this path
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="kings_choice_backup_${TIMESTAMP}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📁 Creating backup directory: $BACKUP_DIR"

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "❌ Error: Database not found at $DB_PATH"
    echo "Please update the DB_PATH variable in this script with the correct path"
    exit 1
fi

echo "📊 Database found: $DB_PATH"

# Create SQL dump
echo "🔄 Creating SQL dump..."
sqlite3 "$DB_PATH" .dump > "$BACKUP_DIR/${BACKUP_NAME}.sql"

if [ $? -eq 0 ]; then
    echo "✅ SQL dump created: $BACKUP_DIR/${BACKUP_NAME}.sql"
else
    echo "❌ Failed to create SQL dump"
    exit 1
fi

# Create binary backup
echo "🔄 Creating binary backup..."
cp "$DB_PATH" "$BACKUP_DIR/${BACKUP_NAME}.db"

if [ $? -eq 0 ]; then
    echo "✅ Binary backup created: $BACKUP_DIR/${BACKUP_NAME}.db"
else
    echo "❌ Failed to create binary backup"
    exit 1
fi

# Show file sizes
echo ""
echo "📊 Backup Summary:"
echo "=================="
ls -lh "$BACKUP_DIR/${BACKUP_NAME}"*

echo ""
echo "✅ Backup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Download the backup files from your VPS:"
echo "   scp user@your-vps:$BACKUP_DIR/${BACKUP_NAME}.* ."
echo ""
echo "2. Restore to your workspace:"
echo "   python3 backup_database.py restore ${BACKUP_NAME}.sql kings_choice.db"
echo ""
echo "3. Verify the restoration:"
echo "   python3 backup_database.py verify kings_choice.db"