"""
Blacklist Database Module

Separate database configuration for blacklist management.
Uses a dedicated SQLite database file for blacklist data.
"""

from datetime import datetime
import os

# Import the main database instance instead of creating a new one
from database import db

def init_blacklist_app(app):
    """Initialize the blacklist database with the Flask app"""
    # Configure separate database URI for blacklist
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['BLACKLIST_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "blacklist.db")}'
    
    # Configure SQLAlchemy for blacklist database using binds
    if 'SQLALCHEMY_BINDS' not in app.config:
        app.config['SQLALCHEMY_BINDS'] = {}
    
    app.config['SQLALCHEMY_BINDS']['blacklist'] = app.config['BLACKLIST_DATABASE_URI']

def create_blacklist_tables(app):
    """Create blacklist database tables"""
    with app.app_context():
        db.create_all(bind_key='blacklist')
        print("Blacklist database tables created successfully!")

class Blacklist(db.Model):
    """
    Blacklist model - represents blacklisted alliances and players
    
    Attributes:
        id: Primary key
        alliance_name: Alliance name (optional, can be null for individual players)
        player_name: Player name (required)
        created_at: When entry was added
        updated_at: Last modification time
    """
    __tablename__ = 'blacklist'
    __bind_key__ = 'blacklist'  # Use the blacklist database
    
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