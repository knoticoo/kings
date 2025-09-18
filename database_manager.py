"""
Database Manager for Multi-User Support

Handles switching between user-specific databases and ensuring data isolation.
"""

import os
import sqlite3
from contextlib import contextmanager
from flask import g
from database import db
from models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_user_database_path(user_id):
    """Get the database path for a specific user"""
    basedir = os.path.abspath(os.path.dirname(__file__))
    user = User.query.get(user_id)
    if user and user.database_path:
        return user.database_path
    return None

@contextmanager
def user_database_context(user_id):
    """Context manager for user-specific database operations"""
    if not user_id:
        raise ValueError("User ID is required")
    
    # Get the user's database path
    db_path = get_user_database_path(user_id)
    if not db_path:
        raise FileNotFoundError(f"Database path not configured for user {user_id}. Please set up your database in user settings.")
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}. Please check your database configuration.")
    
    # Create a new engine and session for the user's database
    user_uri = f'sqlite:///{db_path}'
    user_engine = create_engine(user_uri)
    UserSession = sessionmaker(bind=user_engine)
    user_session = UserSession()
    
    try:
        yield user_session
    finally:
        user_session.close()
        user_engine.dispose()

def get_current_user_session():
    """Get the current user's database session"""
    from flask_login import current_user
    if not current_user.is_authenticated:
        return None
    
    if not hasattr(g, 'db_session'):
        with user_database_context(current_user.id) as session:
            g.db_session = session
    
    return g.db_session

def query_user_data(model_class, user_id, **filters):
    """Query data from user's database"""
    with user_database_context(user_id) as session:
        query = session.query(model_class)
        if filters:
            query = query.filter_by(**filters)
        return query.all()

def query_user_data_with_joins(model_class, user_id, joins=None, **filters):
    """Query data from user's database with JOINs for better performance"""
    with user_database_context(user_id) as session:
        query = session.query(model_class)
        
        # Apply joins if specified
        if joins:
            for join_model, join_condition in joins:
                query = query.join(join_model, join_condition)
        
        if filters:
            query = query.filter_by(**filters)
        return query.all()

def get_user_data_optimized(user_id, include_stats=True):
    """Get optimized dashboard data with single query"""
    with user_database_context(user_id) as session:
        from models import Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist, Guide
        
        # Single query to get all dashboard data
        result = {
            'current_mvp': None,
            'current_winner': None,
            'recent_events': [],
            'stats': {}
        }
        
        # Get current MVP
        current_mvp = session.query(Player).filter_by(
            user_id=user_id, is_current_mvp=True
        ).first()
        if current_mvp:
            result['current_mvp'] = current_mvp
        
        # Get current winner
        current_winner = session.query(Alliance).filter_by(
            user_id=user_id, is_current_winner=True
        ).first()
        if current_winner:
            result['current_winner'] = current_winner
        
        # Get events with MVP assignments in single query
        events_with_mvp = session.query(Event, MVPAssignment, Player).outerjoin(
            MVPAssignment, Event.id == MVPAssignment.event_id
        ).outerjoin(
            Player, MVPAssignment.player_id == Player.id
        ).filter(
            Event.user_id == user_id,
            Event.has_mvp == True
        ).order_by(Event.event_date.desc()).all()
        
        # Group MVP assignments by event
        events_dict = {}
        for event, assignment, player in events_with_mvp:
            if event.id not in events_dict:
                events_dict[event.id] = {
                    'event': event,
                    'mvp_assignments': [],
                    'mvp_players': []
                }
            
            if assignment and player:
                events_dict[event.id]['mvp_assignments'].append(assignment)
                events_dict[event.id]['mvp_players'].append(player.name)
        
        # Convert to list and add counts
        for event_data in events_dict.values():
            event = event_data['event']
            event.mvp_assignments = event_data['mvp_assignments']
            event.mvp_players = event_data['mvp_players']
            event.mvp_count = len(event_data['mvp_assignments'])
            result['recent_events'].append(event)
        
        # Get stats in single queries
        if include_stats:
            result['stats'] = {
                'total_players': session.query(Player).filter_by(user_id=user_id).count(),
                'total_alliances': session.query(Alliance).filter_by(user_id=user_id).count(),
                'total_events': session.query(Event).filter_by(user_id=user_id).count(),
                'total_blacklist_entries': session.query(Blacklist).filter_by(user_id=user_id).count(),
                'total_guides': session.query(Guide).filter_by(user_id=user_id).count()
            }
        
        return result

def get_user_data_by_id(model_class, user_id, record_id):
    """Get a specific record from user's database"""
    with user_database_context(user_id) as session:
        return session.query(model_class).get(record_id)

def create_user_data(model_class, user_id, **data):
    """Create new record in user's database"""
    with user_database_context(user_id) as session:
        record = model_class(user_id=user_id, **data)
        session.add(record)
        session.commit()
        return record

def update_user_data(model_class, user_id, record_id, **data):
    """Update record in user's database"""
    with user_database_context(user_id) as session:
        record = session.query(model_class).get(record_id)
        if record:
            for key, value in data.items():
                setattr(record, key, value)
            session.commit()
            return record
        return None

def delete_user_data(model_class, user_id, record_id):
    """Delete record from user's database"""
    with user_database_context(user_id) as session:
        record = session.query(model_class).get(record_id)
        if record:
            session.delete(record)
            session.commit()
            return True
        return False