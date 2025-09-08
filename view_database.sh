#!/bin/bash

# Database Viewer Script for King's Choice Management App
# Usage: ./view_database.sh

DB_FILE="kings_choice.db"

echo "=========================================="
echo "King's Choice Database Viewer"
echo "=========================================="
echo ""

if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database file '$DB_FILE' not found!"
    exit 1
fi

echo "Database file: $DB_FILE"
echo "File size: $(du -h $DB_FILE | cut -f1)"
echo ""

# Show all tables
echo "📋 Available Tables:"
sqlite3 "$DB_FILE" ".tables"
echo ""

# Show table schemas
echo "📊 Table Schemas:"
echo "-----------------"
sqlite3 "$DB_FILE" ".schema"
echo ""

# Show data counts
echo "📈 Data Counts:"
echo "---------------"
echo "Players: $(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM players;")"
echo "Events: $(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM events;")"
echo "Alliances: $(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM alliances;")"
echo "MVP Assignments: $(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM mvp_assignments;")"
echo "Winner Assignments: $(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM winner_assignments;")"
echo ""

# Show all data if any exists
echo "👥 Players:"
echo "-----------"
sqlite3 "$DB_FILE" "SELECT id, name, is_current_mvp, is_excluded, mvp_count, created_at FROM players;"
echo ""

echo "📅 Events:"
echo "----------"
sqlite3 "$DB_FILE" "SELECT id, name, event_date, has_mvp, has_winner, created_at FROM events;"
echo ""

echo "🏰 Alliances:"
echo "-------------"
sqlite3 "$DB_FILE" "SELECT id, name, is_current_winner, win_count, created_at FROM alliances;"
echo ""

echo "🏆 MVP Assignments:"
echo "-------------------"
sqlite3 "$DB_FILE" "SELECT ma.id, p.name as player, e.name as event, ma.assigned_at FROM mvp_assignments ma JOIN players p ON ma.player_id = p.id JOIN events e ON ma.event_id = e.id;"
echo ""

echo "🎯 Winner Assignments:"
echo "----------------------"
sqlite3 "$DB_FILE" "SELECT wa.id, a.name as alliance, e.name as event, wa.assigned_at FROM winner_assignments wa JOIN alliances a ON wa.alliance_id = a.id JOIN events e ON wa.event_id = e.id;"
echo ""

echo "=========================================="
echo "Database view complete!"
echo "=========================================="