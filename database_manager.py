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
    if not db_path or not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found for user {user_id}")
    
    # Store original database URI
    original_uri = db.engine.url
    
    try:
        # Switch to user's database
        user_uri = f'sqlite:///{db_path}'
        db.engine.url = user_uri
        
        # Create a new session for this database
        session = db.create_scoped_session()
        g.db_session = session
        
        yield session
    finally:
        # Restore original database URI
        db.engine.url = original_uri
        if hasattr(g, 'db_session'):
            g.db_session.close()
            delattr(g, 'db_session')

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