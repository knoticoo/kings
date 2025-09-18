#!/usr/bin/env python3
"""
VPS SubUser Migration Script

This script safely migrates the VPS database to include the SubUser table.
Run this on your VPS before starting the application.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_vps_database():
    """Migrate VPS database to include SubUser table"""
    
    print("🔧 VPS SubUser Migration Script")
    print("=" * 50)
    
    try:
        from flask import Flask
        from database import db, init_app, create_all_tables
        from models import User, SubUser
        
        # Initialize Flask app
        app = Flask(__name__)
        
        # Database configuration for VPS
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'vps-migration-key'
        
        # Initialize database
        init_app(app)
        
        with app.app_context():
            print("📊 Checking database status...")
            
            # Check if SubUser table exists
            try:
                # Try to query SubUser table
                SubUser.query.first()
                print("✅ SubUser table already exists")
                return True
            except Exception as e:
                if "no such table" in str(e).lower():
                    print("❌ SubUser table not found, creating...")
                else:
                    print(f"⚠️  Database error: {e}")
                    return False
            
            # Create all tables (this will add SubUser table)
            print("🔨 Creating SubUser table...")
            create_all_tables(app)
            
            print("✅ SubUser table created successfully!")
            print("🎉 VPS database migration completed!")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def check_database_connection():
    """Check if database connection works"""
    try:
        from flask import Flask
        from database import db, init_app
        from models import User
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-key'
        
        init_app(app)
        
        with app.app_context():
            # Try to query users
            users = User.query.all()
            print(f"✅ Database connection successful. Found {len(users)} users.")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting VPS SubUser Migration...")
    print("=" * 50)
    
    # First check database connection
    if not check_database_connection():
        print("❌ Cannot connect to database. Please check your database file.")
        return False
    
    # Run migration
    if migrate_vps_database():
        print("\n🎉 Migration completed successfully!")
        print("You can now start your application on VPS.")
        return True
    else:
        print("\n💥 Migration failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
