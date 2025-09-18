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
import hashlib
from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """
    User model - represents application users with isolated data
    
    Attributes:
        id: Primary key
        username: Unique username for login
        email: User email address
        password_hash: Hashed password
        is_admin: Boolean flag for admin privileges
        is_active: Boolean flag for account status
        created_at: When user was created
        last_login: Last login timestamp
        database_path: Path to user's isolated database file
        telegram_bot_token: Telegram bot token for this user
        telegram_chat_id: Telegram chat ID for this user
        telegram_enabled: Whether Telegram notifications are enabled
        discord_bot_token: Discord bot token for this user
        discord_channel_id: Discord channel ID for this user
        discord_enabled: Whether Discord notifications are enabled
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    database_path = db.Column(db.String(255), nullable=False)
    
    # Telegram configuration
    telegram_bot_token = db.Column(db.String(255), nullable=True)
    telegram_chat_id = db.Column(db.String(100), nullable=True)
    telegram_enabled = db.Column(db.Boolean, default=False, nullable=False)
    
    # Discord configuration
    discord_bot_token = db.Column(db.String(255), nullable=True)
    discord_channel_id = db.Column(db.String(100), nullable=True)
    discord_enabled = db.Column(db.Boolean, default=False, nullable=False)
    
    # Language preference
    language = db.Column(db.String(10), default='en', nullable=False)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        # Handle simple SHA256 hash format for testing
        if self.password_hash.startswith('sha256:'):
            try:
                parts = self.password_hash.split(':')
                if len(parts) == 3:
                    salt_hex = parts[1]
                    stored_hash = parts[2]
                    
                    # Recreate the hash
                    salt = bytes.fromhex(salt_hex)
                    hash_obj = hashlib.sha256()
                    hash_obj.update(salt + password.encode('utf-8'))
                    computed_hash = hash_obj.hexdigest()
                    
                    return computed_hash == stored_hash
            except Exception:
                pass
        
        # Fall back to werkzeug's check_password_hash for other formats
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'telegram_enabled': self.telegram_enabled,
            'discord_enabled': self.discord_enabled
        }

class SubUser(UserMixin, db.Model):
    """
    SubUser model - represents alliance leader helpers with limited access to parent user's data
    
    Attributes:
        id: Primary key
        username: Unique username for login
        email: Sub-user email address
        password_hash: Hashed password
        parent_user_id: Foreign key to parent User
        is_active: Boolean flag for account status
        permissions: JSON field storing specific permissions
        created_at: When sub-user was created
        last_login: Last login timestamp
    """
    __tablename__ = 'sub_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    parent_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    permissions = db.Column(db.JSON, default=lambda: {
        'can_view_players': True,
        'can_view_alliances': True,
        'can_view_events': True,
        'can_assign_mvp': False,
        'can_assign_winner': False,
        'can_manage_players': False,
        'can_manage_alliances': False,
        'can_manage_events': False,
        'can_view_dashboard': True
    }, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship to parent user
    parent_user = db.relationship('User', backref='sub_users', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        # Handle simple SHA256 hash format for testing
        if self.password_hash.startswith('sha256:'):
            try:
                parts = self.password_hash.split(':')
                if len(parts) == 3:
                    salt_hex = parts[1]
                    stored_hash = parts[2]
                    
                    # Recreate the hash
                    salt = bytes.fromhex(salt_hex)
                    hash_obj = hashlib.sha256()
                    hash_obj.update(salt + password.encode('utf-8'))
                    computed_hash = hash_obj.hexdigest()
                    
                    return computed_hash == stored_hash
            except Exception:
                pass
        
        # Fall back to werkzeug's check_password_hash for other formats
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """Check if sub-user has specific permission"""
        return self.permissions.get(permission, False)
    
    def get_user_id(self):
        """Return parent user ID for data access"""
        return self.parent_user_id
    
    def __repr__(self):
        return f'<SubUser {self.username} (parent: {self.parent_user_id})>'
    
    def to_dict(self):
        """Convert sub-user to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'parent_user_id': self.parent_user_id,
            'is_active': self.is_active,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Player(db.Model):
    """
    Player model - represents game players
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User (for data isolation)
        name: Player name (unique per user)
        is_current_mvp: Boolean flag for current MVP status
        is_excluded: Boolean flag for exclusion from MVP rotation
        mvp_count: Total number of times this player was MVP
        created_at: When player was added
        updated_at: Last modification time
    """
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_current_mvp = db.Column(db.Boolean, default=False, nullable=False)
    is_excluded = db.Column(db.Boolean, default=False, nullable=False)
    mvp_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint on name per user
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='unique_player_per_user'),)
    
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
        user_id: Foreign key to User (for data isolation)
        name: Alliance name (unique per user)
        is_current_winner: Boolean flag for current winner status
        win_count: Total number of times this alliance won
        created_at: When alliance was added
        updated_at: Last modification time
    """
    __tablename__ = 'alliances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_current_winner = db.Column(db.Boolean, default=False, nullable=False)
    win_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint on name per user
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='unique_alliance_per_user'),)
    
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
        user_id: Foreign key to User (for data isolation)
        name: Event name
        description: Optional event description
        event_date: When the event occurred
        has_mvp: Whether this event has an MVP assigned
        has_winner: Whether this event has a winning alliance
        created_at: When event was created
    """
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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


class Blacklist(db.Model):
    """
    Blacklist model - represents blacklisted alliances and players
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User (for data isolation)
        alliance_name: Alliance name (optional, can be null for individual players)
        player_name: Player name (optional, can be null for alliance-only entries)
        created_at: When entry was added
        updated_at: Last modification time
    """
    __tablename__ = 'blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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

class Feedback(db.Model):
    """
    Feedback model - represents user feedback and suggestions
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User (who submitted the feedback)
        title: Brief title/subject of the feedback
        message: Detailed feedback message
        category: Type of feedback (suggestion, bug_report, feature_request, etc.)
        status: Status of the feedback (pending, reviewed, implemented, rejected)
        admin_notes: Admin response or notes
        created_at: When feedback was submitted
        updated_at: Last modification time
        reviewed_at: When admin reviewed the feedback
        reviewed_by: Admin user who reviewed the feedback
    """
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='suggestion', nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='feedback_submissions')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='feedback_reviews')
    
    def __repr__(self):
        return f'<Feedback {self.title} by {self.user.username if self.user else "Unknown"}>'
    
    def to_dict(self):
        """Convert feedback to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'title': self.title,
            'message': self.message,
            'category': self.category,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewer': self.reviewer.username if self.reviewer else None
        }