#!/usr/bin/env python3
"""
Script to create an admin user for King's Choice Management App

This script creates an admin user with the specified credentials:
- Username: knotico
- Password: Millie1991
- Email: knotico@admin.local (default)
- Admin privileges: True
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from database import db, init_app, create_all_tables
from models import User

def create_admin_user():
    """Create admin user with specified credentials"""
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    from config import Config
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_main_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'admin-creation-script-key'
    
    # Initialize database
    init_app(app)
    
    with app.app_context():
        # Create tables if they don't exist
        create_all_tables(app)
        
        # Check if admin user already exists
        existing_user = User.query.filter_by(username='knotico').first()
        if existing_user:
            print(f"❌ User 'knotico' already exists!")
            print(f"   User ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            print(f"   Is Admin: {existing_user.is_admin}")
            print(f"   Is Active: {existing_user.is_active}")
            
            # Ask if user wants to update the existing user
            response = input("\nDo you want to update the existing user to admin? (y/N): ").strip().lower()
            if response == 'y':
                existing_user.is_admin = True
                existing_user.is_active = True
                existing_user.set_password('Millie1991')
                existing_user.email = 'knotico@admin.local'
                db.session.commit()
                print("✅ Existing user updated to admin successfully!")
            else:
                print("❌ Operation cancelled.")
            return
        
        # Create new admin user
        try:
            admin_user = User(
                username='knotico',
                email='knotico@admin.local',
                is_admin=True,
                is_active=True,
                database_path=os.path.join(basedir, 'user_databases', 'user_knotico.db'),
                created_at=datetime.utcnow()
            )
            admin_user.set_password('Millie1991')
            
            # Add to database
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Password: Millie1991")
            print(f"   Is Admin: {admin_user.is_admin}")
            print(f"   Is Active: {admin_user.is_active}")
            print(f"   User ID: {admin_user.id}")
            print(f"   Database Path: {admin_user.database_path}")
            
            # Create user's database directory
            user_db_dir = os.path.dirname(admin_user.database_path)
            os.makedirs(user_db_dir, exist_ok=True)
            print(f"✅ User database directory created: {user_db_dir}")
            
        except Exception as e:
            print(f"❌ Error creating admin user: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("🔧 King's Choice Management App - Admin User Creation Script")
    print("=" * 60)
    print("Creating admin user with credentials:")
    print("  Username: knotico")
    print("  Password: Millie1991")
    print("  Email: knotico@admin.local")
    print("  Admin privileges: Yes")
    print("=" * 60)
    
    success = create_admin_user()
    
    if success:
        print("\n🎉 Script completed successfully!")
        print("\nYou can now log in to the application using:")
        print("  Username: knotico")
        print("  Password: Millie1991")
    else:
        print("\n💥 Script failed!")
        sys.exit(1)