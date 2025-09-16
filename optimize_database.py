#!/usr/bin/env python3
"""
Database Optimization Script

This script adds indexes to the SQLite database to improve query performance.
It works directly with the SQLite database without requiring Flask.
"""

import sqlite3
import os
import sys

def add_database_indexes():
    """Add indexes to improve query performance"""
    db_path = "/workspace/kings_choice.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Please run the Flask app first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Adding database indexes for performance optimization...")
        
        # Create indexes for frequently queried columns
        indexes = [
            # User table indexes
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            
            # Player table indexes
            "CREATE INDEX IF NOT EXISTS idx_players_user_id ON players(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_players_name ON players(name)",
            "CREATE INDEX IF NOT EXISTS idx_players_is_current_mvp ON players(is_current_mvp)",
            "CREATE INDEX IF NOT EXISTS idx_players_is_excluded ON players(is_excluded)",
            "CREATE INDEX IF NOT EXISTS idx_players_mvp_count ON players(mvp_count)",
            
            # Alliance table indexes
            "CREATE INDEX IF NOT EXISTS idx_alliances_user_id ON alliances(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_alliances_name ON alliances(name)",
            "CREATE INDEX IF NOT EXISTS idx_alliances_is_current_winner ON alliances(is_current_winner)",
            "CREATE INDEX IF NOT EXISTS idx_alliances_win_count ON alliances(win_count)",
            
            # Event table indexes
            "CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date)",
            "CREATE INDEX IF NOT EXISTS idx_events_has_mvp ON events(has_mvp)",
            "CREATE INDEX IF NOT EXISTS idx_events_has_winner ON events(has_winner)",
            
            # MVP Assignment table indexes
            "CREATE INDEX IF NOT EXISTS idx_mvp_assignments_player_id ON mvp_assignments(player_id)",
            "CREATE INDEX IF NOT EXISTS idx_mvp_assignments_event_id ON mvp_assignments(event_id)",
            "CREATE INDEX IF NOT EXISTS idx_mvp_assignments_assigned_at ON mvp_assignments(assigned_at)",
            
            # Winner Assignment table indexes
            "CREATE INDEX IF NOT EXISTS idx_winner_assignments_alliance_id ON winner_assignments(alliance_id)",
            "CREATE INDEX IF NOT EXISTS idx_winner_assignments_event_id ON winner_assignments(event_id)",
            "CREATE INDEX IF NOT EXISTS idx_winner_assignments_assigned_at ON winner_assignments(assigned_at)",
            
            # Blacklist table indexes
            "CREATE INDEX IF NOT EXISTS idx_blacklist_user_id ON blacklist(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_blacklist_alliance_name ON blacklist(alliance_name)",
            "CREATE INDEX IF NOT EXISTS idx_blacklist_player_name ON blacklist(player_name)",
            
            # Guide table indexes
            "CREATE INDEX IF NOT EXISTS idx_guides_user_id ON guides(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_guides_category_id ON guides(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_guides_slug ON guides(slug)",
            "CREATE INDEX IF NOT EXISTS idx_guides_is_published ON guides(is_published)",
            "CREATE INDEX IF NOT EXISTS idx_guides_is_featured ON guides(is_featured)",
            
            # Guide Category table indexes
            "CREATE INDEX IF NOT EXISTS idx_guide_categories_user_id ON guide_categories(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_guide_categories_slug ON guide_categories(slug)",
            "CREATE INDEX IF NOT EXISTS idx_guide_categories_is_active ON guide_categories(is_active)",
            
            # Composite indexes for common query patterns
            "CREATE INDEX IF NOT EXISTS idx_players_user_excluded ON players(user_id, is_excluded)",
            "CREATE INDEX IF NOT EXISTS idx_players_user_mvp ON players(user_id, is_current_mvp)",
            "CREATE INDEX IF NOT EXISTS idx_alliances_user_winner ON alliances(user_id, is_current_winner)",
            "CREATE INDEX IF NOT EXISTS idx_events_user_mvp ON events(user_id, has_mvp)",
            "CREATE INDEX IF NOT EXISTS idx_events_user_winner ON events(user_id, has_winner)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
            except sqlite3.Error as e:
                print(f"⚠️  Index may already exist: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Database optimization completed successfully!")
        print("📈 Performance should be significantly improved.")
        print("\nKey improvements:")
        print("• Faster user-specific queries")
        print("• Optimized MVP and winner lookups")
        print("• Improved event filtering")
        print("• Better assignment tracking")
        
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing database: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_database_indexes()
    sys.exit(0 if success else 1)