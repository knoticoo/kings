#!/usr/bin/env python3
"""
Python script to check players in the King's Choice database
This works without needing to install sqlite3 command-line tool
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = "/workspace/kings_choice.db"

def main():
    print("=== King's Choice Database Player Check ===")
    print(f"Database: {DB_PATH}")
    print()
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found at {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Show tables
        print("📊 Database Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # Check players
        print("👥 Players in Database:")
        cursor.execute("SELECT COUNT(*) FROM players;")
        player_count = cursor.fetchone()[0]
        print(f"Total players: {player_count}")
        
        if player_count > 0:
            print("\nPlayer Details:")
            cursor.execute("""
                SELECT id, name, is_current_mvp, mvp_count, is_excluded, created_at
                FROM players 
                ORDER BY name;
            """)
            players = cursor.fetchall()
            
            print(f"{'ID':<3} {'Name':<20} {'MVP':<5} {'Count':<5} {'Status':<10} {'Created'}")
            print("-" * 70)
            
            for player in players:
                id, name, is_mvp, mvp_count, is_excluded, created_at = player
                mvp_status = "✅" if is_mvp else "❌"
                status = "🚫 Excluded" if is_excluded else "✅ Active"
                created = created_at[:19] if created_at else "N/A"
                print(f"{id:<3} {name:<20} {mvp_status:<5} {mvp_count:<5} {status:<10} {created}")
        else:
            print("No players found in database.")
        
        print()
        
        # Check alliances
        print("🏆 Alliance Information:")
        cursor.execute("SELECT COUNT(*) FROM alliances;")
        alliance_count = cursor.fetchone()[0]
        print(f"Total alliances: {alliance_count}")
        
        if alliance_count > 0:
            print("\nAlliance Details:")
            cursor.execute("""
                SELECT id, name, is_current_winner, win_count, created_at
                FROM alliances 
                ORDER BY name;
            """)
            alliances = cursor.fetchall()
            
            print(f"{'ID':<3} {'Name':<20} {'Winner':<7} {'Wins':<5} {'Created'}")
            print("-" * 60)
            
            for alliance in alliances:
                id, name, is_winner, win_count, created_at = alliance
                winner_status = "🏆" if is_winner else "❌"
                created = created_at[:19] if created_at else "N/A"
                print(f"{id:<3} {name:<20} {winner_status:<7} {win_count:<5} {created}")
        
        print()
        
        # Check events
        print("📅 Recent Events:")
        cursor.execute("SELECT COUNT(*) FROM events;")
        event_count = cursor.fetchone()[0]
        print(f"Total events: {event_count}")
        
        if event_count > 0:
            print("\nLatest 5 Events:")
            cursor.execute("""
                SELECT id, name, has_mvp, has_winner, event_date
                FROM events 
                ORDER BY event_date DESC
                LIMIT 5;
            """)
            events = cursor.fetchall()
            
            print(f"{'ID':<3} {'Name':<25} {'MVP':<5} {'Winner':<7} {'Date'}")
            print("-" * 65)
            
            for event in events:
                id, name, has_mvp, has_winner, event_date = event
                mvp_status = "✅" if has_mvp else "❌"
                winner_status = "✅" if has_winner else "❌"
                date = event_date[:19] if event_date else "N/A"
                print(f"{id:<3} {name:<25} {mvp_status:<5} {winner_status:<7} {date}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()