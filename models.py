"""
Database Models for King's Choice Management App

This module contains all SQLAlchemy models for:
- Players: Game players who can be assigned as MVP
- Alliances: Player groups that can win events
- Events: Game events that need MVP and winner assignments
- MVPAssignment: Tracks which player was MVP for which event
- WinnerAssignment: Tracks which alliance won which event
"""

from datetime import datetime
from database import db

class Player(db.Model):
    """
    Player model - represents game players
    
    Attributes:
        id: Primary key
        name: Player name (unique)
        is_current_mvp: Boolean flag for current MVP status
        is_excluded: Boolean flag for exclusion from MVP rotation
        mvp_count: Total number of times this player was MVP
        created_at: When player was added
        updated_at: Last modification time
    """
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    is_current_mvp = db.Column(db.Boolean, default=False, nullable=False)
    is_excluded = db.Column(db.Boolean, default=False, nullable=False)
    mvp_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mvp_assignments = db.relationship('MVPAssignment', backref='player', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Player {self.name}>'
    
    def to_dict(self):
        """Convert player to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'is_current_mvp': self.is_current_mvp,
            'is_excluded': self.is_excluded,
            'mvp_count': self.mvp_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Alliance(db.Model):
    """
    Alliance model - represents player alliances/guilds
    
    Attributes:
        id: Primary key
        name: Alliance name (unique)
        is_current_winner: Boolean flag for current winner status
        win_count: Total number of times this alliance won
        created_at: When alliance was added
        updated_at: Last modification time
    """
    __tablename__ = 'alliances'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    is_current_winner = db.Column(db.Boolean, default=False, nullable=False)
    win_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    winner_assignments = db.relationship('WinnerAssignment', backref='alliance', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Alliance {self.name}>'
    
    def to_dict(self):
        """Convert alliance to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'is_current_winner': self.is_current_winner,
            'win_count': self.win_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Event(db.Model):
    """
    Event model - represents game events that need MVP and winner assignments
    
    Attributes:
        id: Primary key
        name: Event name
        description: Optional event description
        event_date: When the event occurred
        has_mvp: Whether this event has an MVP assigned
        has_winner: Whether this event has a winning alliance
        created_at: When event was created
    """
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    has_mvp = db.Column(db.Boolean, default=False, nullable=False)
    has_winner = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    mvp_assignments = db.relationship('MVPAssignment', backref='event', lazy=True, cascade='all, delete-orphan')
    winner_assignments = db.relationship('WinnerAssignment', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Event {self.name}>'
    
    def to_dict(self):
        """Convert event to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'has_mvp': self.has_mvp,
            'has_winner': self.has_winner,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MVPAssignment(db.Model):
    """
    MVP Assignment model - tracks which player was MVP for which event
    
    This is crucial for the rotation logic - we need to track all assignments
    to ensure fair rotation (only assign MVP when all players have been MVP)
    """
    __tablename__ = 'mvp_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Allow multiple MVP assignments per event for recurring events
    
    def __repr__(self):
        return f'<MVPAssignment Player:{self.player_id} Event:{self.event_id}>'
    
    def to_dict(self):
        """Convert assignment to dictionary for API responses"""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'event_id': self.event_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'player_name': self.player.name if self.player else None,
            'event_name': self.event.name if self.event else None
        }

class WinnerAssignment(db.Model):
    """
    Winner Assignment model - tracks which alliance won which event
    
    This is crucial for the rotation logic - we need to track all assignments
    to ensure fair rotation (only assign winner when all alliances have won)
    """
    __tablename__ = 'winner_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    alliance_id = db.Column(db.Integer, db.ForeignKey('alliances.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Allow multiple winner assignments per event for recurring events
    
    def __repr__(self):
        return f'<WinnerAssignment Alliance:{self.alliance_id} Event:{self.event_id}>'
    
    def to_dict(self):
        """Convert assignment to dictionary for API responses"""
        return {
            'id': self.id,
            'alliance_id': self.alliance_id,
            'event_id': self.event_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'alliance_name': self.alliance.name if self.alliance else None,
            'event_name': self.event.name if self.event else None
        }