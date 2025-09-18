#!/usr/bin/env python3
"""
Script to create a sub-user for King's Choice Management App

This script creates a sub-user (alliance leader helper) for an existing user.
Usage: python create_subuser.py <parent_username> <subuser_username> <subuser_email> <password>
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from database import db, init_app, create_all_tables
from models import User, SubUser

def create_subuser(parent_username, subuser_username, subuser_email, password):
    """Create sub-user for specified parent user"""
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    from config import Config
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_main_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'subuser-creation-script-key'
    
    # Initialize database
    init_app(app)
    
    with app.app_context():
        # Create tables if they don't exist
        create_all_tables(app)
        
        # Find parent user
        parent_user = User.query.filter_by(username=parent_username).first()
        if not parent_user:
            print(f"❌ Parent user '{parent_username}' not found!")
            return False
        
        # Check if sub-user already exists
        existing_subuser = SubUser.query.filter_by(username=subuser_username).first()
        if existing_subuser:
            print(f"❌ Sub-user '{subuser_username}' already exists!")
            return False
        
        # Check if email already exists
        if User.query.filter_by(email=subuser_email).first() or SubUser.query.filter_by(email=subuser_email).first():
            print(f"❌ Email '{subuser_email}' already exists!")
            return False
        
        try:
            # Create sub-user with default permissions
            subuser = SubUser(
                username=subuser_username,
                email=subuser_email,
                parent_user_id=parent_user.id,
                is_active=True,
                permissions={
                    'can_view_players': True,
                    'can_view_alliances': True,
                    'can_view_events': True,
                    'can_assign_mvp': False,
                    'can_assign_winner': False,
                    'can_manage_players': False,
                    'can_manage_alliances': False,
                    'can_manage_events': False,
                    'can_view_dashboard': True
                }
            )
            subuser.set_password(password)
            
            # Add to database
            db.session.add(subuser)
            db.session.commit()
            
            print("✅ Sub-user created successfully!")
            print(f"   Username: {subuser.username}")
            print(f"   Email: {subuser.email}")
            print(f"   Password: {password}")
            print(f"   Parent User: {parent_user.username}")
            print(f"   Is Active: {subuser.is_active}")
            print(f"   Sub-User ID: {subuser.id}")
            print(f"   Parent User ID: {subuser.parent_user_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating sub-user: {str(e)}")
            db.session.rollback()
            return False

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) != 5:
        print("Usage: python create_subuser.py <parent_username> <subuser_username> <subuser_email> <password>")
        print("Example: python create_subuser.py julija julija_helper julija.helper@example.com helper123")
        sys.exit(1)
    
    parent_username = sys.argv[1]
    subuser_username = sys.argv[2]
    subuser_email = sys.argv[3]
    password = sys.argv[4]
    
    print("🔧 King's Choice Management App - Sub-User Creation Script")
    print("=" * 60)
    print(f"Creating sub-user for parent: {parent_username}")
    print(f"Sub-user username: {subuser_username}")
    print(f"Sub-user email: {subuser_email}")
    print("=" * 60)
    
    success = create_subuser(parent_username, subuser_username, subuser_email, password)
    
    if success:
        print("\n🎉 Script completed successfully!")
        print(f"\nThe sub-user '{subuser_username}' can now log in to the application using:")
        print(f"  Username: {subuser_username}")
        print(f"  Password: {password}")
        print(f"\nThey will have access to {parent_username}'s data with limited permissions.")
    else:
        print("\n💥 Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
