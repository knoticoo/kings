"""
Database Index Optimization Script

This script adds indexes to frequently queried columns to improve performance.
Run this script after the initial database setup to add performance indexes.
"""

from database import db
from models import Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist, Guide, GuideCategory, User
from app import app

def add_database_indexes():
    """Add indexes to improve query performance"""
    with app.app_context():
        try:
            # Create indexes for frequently queried columns
            print("Adding database indexes for performance optimization...")
            
            # User table indexes
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            
            # Player table indexes
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_players_user_id ON players(user_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_players_name ON players(name)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_players_is_current_mvp ON players(is_current_mvp)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_players_is_excluded ON players(is_excluded)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_players_mvp_count ON players(mvp_count)")
            
            # Alliance table indexes
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_alliances_user_id ON alliances(user_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_alliances_name ON alliances(name)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_alliances_is_current_winner ON alliances(is_current_winner)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_alliances_win_count ON alliances(win_count)")
            
            # Event table indexes
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_events_has_mvp ON events(has_mvp)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_events_has_winner ON events(has_winner)")
            
            # MVP Assignment table indexes
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_mvp_assignments_player_id ON mvp_assignments(player_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_mvp_assignments_event_id ON mvp_assignments(event_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_mvp_assignments_assigned_at ON mvp_assignments(assigned_at)")
            
            # Winner Assignment table indexes
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_winner_assignments_alliance_id ON winner_assignments(alliance_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_winner_assignments_event_id ON winner_assignments(event_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_winner_assignments_assigned_at ON winner_assignments(assigned_at)")
            
            # Blacklist table indexes
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_blacklist_user_id ON blacklist(user_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_blacklist_alliance_name ON blacklist(alliance_name)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_blacklist_player_name ON blacklist(player_name)")
            
            # Guide table indexes
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_guides_user_id ON guides(user_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_guides_category_id ON guides(category_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_guides_slug ON guides(slug)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_guides_is_published ON guides(is_published)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_guides_is_featured ON guides(is_featured)")
            
            # Guide Category table indexes
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_guide_categories_user_id ON guide_categories(user_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_guide_categories_slug ON guide_categories(slug)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_guide_categories_is_active ON guide_categories(is_active)")
            
            # Composite indexes for common query patterns
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_players_user_excluded ON players(user_id, is_excluded)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_players_user_mvp ON players(user_id, is_current_mvp)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_alliances_user_winner ON alliances(user_id, is_current_winner)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_events_user_mvp ON events(user_id, has_mvp)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_events_user_winner ON events(user_id, has_winner)")
            
            print("✅ Database indexes added successfully!")
            print("Performance should be significantly improved.")
            
        except Exception as e:
            print(f"❌ Error adding indexes: {str(e)}")
            print("Some indexes may already exist, which is normal.")

if __name__ == "__main__":
    add_database_indexes()