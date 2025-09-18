#!/usr/bin/env python3
"""
Script to add SubUser table to the database

This script adds the sub_users table to the existing database.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from database import db, init_app, create_all_tables
from models import User, SubUser

def add_subuser_table():
    """Add SubUser table to the database"""
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    from config import Config
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_main_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'subuser-table-creation-script-key'
    
    # Initialize database
    init_app(app)
    
    with app.app_context():
        try:
            # Create all tables (this will add the SubUser table if it doesn't exist)
            create_all_tables(app)
            
            print("✅ SubUser table added successfully!")
            print("   The sub_users table has been created with the following structure:")
            print("   - id: Primary key")
            print("   - username: Unique username for login")
            print("   - email: Sub-user email address")
            print("   - password_hash: Hashed password")
            print("   - parent_user_id: Foreign key to parent User")
            print("   - is_active: Boolean flag for account status")
            print("   - permissions: JSON field storing specific permissions")
            print("   - created_at: When sub-user was created")
            print("   - last_login: Last login timestamp")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding SubUser table: {str(e)}")
            return False

def main():
    """Main function"""
    print("🔧 King's Choice Management App - SubUser Table Creation Script")
    print("=" * 60)
    print("Adding SubUser table to the database...")
    print("=" * 60)
    
    success = add_subuser_table()
    
    if success:
        print("\n🎉 Script completed successfully!")
        print("\nYou can now create sub-users using the web interface or the create_subuser.py script.")
    else:
        print("\n💥 Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
