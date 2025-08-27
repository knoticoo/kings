"""
Database initialization module for King's Choice Management App

This module handles the database setup and model initialization
to avoid circular import issues.
"""

from flask_sqlalchemy import SQLAlchemy

# Create database instance
db = SQLAlchemy()

def init_app(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
def create_all_tables(app):
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")