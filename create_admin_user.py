#!/usr/bin/env python3
"""
Script to create an admin user for first-time setup
"""

from app import app
from database import db
from models import User
import os

def create_admin_user():
    """Create an admin user for first-time setup"""
    with app.app_context():
        # Check if any users exist
        existing_users = User.query.all()
        if existing_users:
            print(f"Users already exist ({len(existing_users)} users found)")
            for user in existing_users:
                print(f"  - {user.username} (Admin: {user.is_admin}, Active: {user.is_active})")
            return
        
        # Create admin user
        admin_username = "admin"
        admin_email = "admin@kingschoice.local"
        admin_password = "admin123"  # Change this in production!
        
        # Create user database path
        basedir = os.path.abspath(os.path.dirname(__file__))
        user_db_path = os.path.join(basedir, 'user_databases', f'user_{admin_username}.db')
        
        # Create user_databases directory if it doesn't exist
        os.makedirs(os.path.dirname(user_db_path), exist_ok=True)
        
        # Create admin user
        admin_user = User(
            username=admin_username,
            email=admin_email,
            is_admin=True,
            is_active=True,
            database_path=user_db_path
        )
        admin_user.set_password(admin_password)
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"Admin user created successfully!")
            print(f"Username: {admin_username}")
            print(f"Password: {admin_password}")
            print(f"Database: {user_db_path}")
            
            # Create user's database
            from auth import create_user_database
            create_user_database(admin_user.id, admin_username)
            print(f"User database created: {user_db_path}")
            
        except Exception as e:
            print(f"Error creating admin user: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_admin_user()