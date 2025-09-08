"""
Database Models for King's Choice Management App

This module contains all SQLAlchemy models for:
- Players: Game players who can be assigned as MVP
- Alliances: Player groups that can win events
- Events: Game events that need MVP and winner assignments
- MVPAssignment: Tracks which player was MVP for which event
- WinnerAssignment: Tracks which alliance won which event
- GuideCategory: Categories for organizing guides
- Guide: Individual guide articles with rich content
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

class GuideCategory(db.Model):
    """
    Guide Category model - represents categories for organizing guides
    
    Attributes:
        id: Primary key
        name: Category name (e.g., "Knights", "Events")
        slug: URL-friendly version of name (e.g., "knights", "events")
        description: Category description
        icon: Bootstrap icon class for the category
        sort_order: Order for displaying categories
        is_active: Whether category is active
        created_at: When category was created
        updated_at: Last modification time
    """
    __tablename__ = 'guide_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='bi-book')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    guides = db.relationship('Guide', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<GuideCategory {self.name}>'
    
    def to_dict(self):
        """Convert category to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'guide_count': len(self.guides)
        }

class Guide(db.Model):
    """
    Guide model - represents individual guide articles
    
    Attributes:
        id: Primary key
        title: Guide title
        slug: URL-friendly version of title
        content: Rich HTML content of the guide
        excerpt: Short description/excerpt
        category_id: Foreign key to GuideCategory
        featured_image: URL to featured image
        is_published: Whether guide is published
        is_featured: Whether guide is featured
        view_count: Number of times guide has been viewed
        sort_order: Order for displaying guides within category
        created_at: When guide was created
        updated_at: Last modification time
    """
    __tablename__ = 'guides'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('guide_categories.id'), nullable=False)
    featured_image = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Guide {self.title}>'
    
    def to_dict(self):
        """Convert guide to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'excerpt': self.excerpt,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'featured_image': self.featured_image,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'view_count': self.view_count,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def increment_view_count(self):
        """Increment the view count for this guide"""
        self.view_count += 1
        db.session.commit()

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
    
    id = db.Column(db.Integer, primary_key=True)
    alliance_name = db.Column(db.String(100), nullable=True)  # Optional alliance tag
    player_name = db.Column(db.String(100), nullable=False)   # Required player name
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