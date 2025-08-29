#!/bin/bash
# Script to check players in the King's Choice database

DB_PATH="/workspace/kings_choice.db"

echo "=== King's Choice Database Player Check ==="
echo "Database: $DB_PATH"
echo

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "❌ Database file not found at $DB_PATH"
    exit 1
fi

echo "📊 Database Tables:"
sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table';" | while read table; do
    echo "  - $table"
done
echo

echo "👥 Players in Database:"
PLAYER_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM players;")
echo "Total players: $PLAYER_COUNT"

if [ "$PLAYER_COUNT" -gt 0 ]; then
    echo
    echo "Player Details:"
    sqlite3 "$DB_PATH" -header -column "
    SELECT 
        id,
        name,
        CASE WHEN is_current_mvp = 1 THEN '✅ MVP' ELSE '❌' END as 'Current MVP',
        mvp_count as 'MVP Count',
        CASE WHEN is_excluded = 1 THEN '🚫 Excluded' ELSE '✅ Active' END as 'Status',
        datetime(created_at) as 'Created'
    FROM players 
    ORDER BY name;
    "
else
    echo "No players found in database."
fi

echo
echo "🏆 Alliance Information:"
ALLIANCE_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM alliances;")
echo "Total alliances: $ALLIANCE_COUNT"

if [ "$ALLIANCE_COUNT" -gt 0 ]; then
    echo
    echo "Alliance Details:"
    sqlite3 "$DB_PATH" -header -column "
    SELECT 
        id,
        name,
        CASE WHEN is_current_winner = 1 THEN '🏆 Winner' ELSE '❌' END as 'Current Winner',
        win_count as 'Win Count',
        datetime(created_at) as 'Created'
    FROM alliances 
    ORDER BY name;
    "
fi

echo
echo "📅 Recent Events:"
EVENT_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM events;")
echo "Total events: $EVENT_COUNT"

if [ "$EVENT_COUNT" -gt 0 ]; then
    echo
    echo "Latest 5 Events:"
    sqlite3 "$DB_PATH" -header -column "
    SELECT 
        id,
        name,
        CASE WHEN has_mvp = 1 THEN '✅' ELSE '❌' END as 'Has MVP',
        CASE WHEN has_winner = 1 THEN '✅' ELSE '❌' END as 'Has Winner',
        datetime(event_date) as 'Event Date'
    FROM events 
    ORDER BY event_date DESC
    LIMIT 5;
    "
fi