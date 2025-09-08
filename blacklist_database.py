"""
Blacklist Database Module

Database models for blacklist management.
Uses the main database instead of a separate one for simplicity.
"""

from datetime import datetime
from database import db

def init_blacklist_app(app):
    """Initialize the blacklist database with the Flask app"""
    # No special configuration needed - using main database
    pass

def create_blacklist_tables(app):
    """Create blacklist database tables"""
    with app.app_context():
        db.create_all()
        print("Blacklist database tables created successfully!")

class Blacklist(db.Model):
    """
    Blacklist model - represents blacklisted alliances and players
    
    Attributes:
        id: Primary key
        alliance_name: Alliance name (optional, can be null for individual players)
        player_name: Player name (optional, can be null for alliance-only entries)
        created_at: When entry was added
        updated_at: Last modification time
    """
    __tablename__ = 'blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    alliance_name = db.Column(db.String(100), nullable=True)  # Optional alliance tag
    player_name = db.Column(db.String(100), nullable=True)    # Optional player name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        if self.alliance_name:
            return f'<Blacklist ({self.alliance_name}) {self.player_name}>'
        else:
            return f'<Blacklist {self.player_name}>'
    
    def to_dict(self):
        """Convert blacklist entry to dictionary for API responses"""
        return {
            'id': self.id,
            'alliance_name': self.alliance_name,
            'player_name': self.player_name,
            'display_name': self.get_display_name(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_display_name(self):
        """Get the formatted display name with alliance tag if present"""
        if self.alliance_name:
            return f"({self.alliance_name}) {self.player_name}"
        else:
            return self.player_name