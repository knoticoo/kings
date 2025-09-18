#!/usr/bin/env python3
"""
Safe startup script for King's Choice Management App
This script ensures database migration happens before app startup
"""

import os
import sys
import traceback
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Setup database with proper migration"""
    print("🔧 Setting up database...")
    
    try:
        from flask import Flask
        from database import db, init_app, create_all_tables
        from models import User, SubUser
        
        # Create Flask app for database setup
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
        
        # Initialize database
        init_app(app)
        
        with app.app_context():
            print("  - Creating/updating database tables...")
            create_all_tables(app)
            print("  ✅ Database tables ready")
            
            # Check if SubUser table exists and has data
            try:
                subuser_count = SubUser.query.count()
                print(f"  ✅ SubUser table exists with {subuser_count} records")
            except Exception as e:
                print(f"  ⚠️  SubUser table issue: {e}")
                # Try to create it manually
                try:
                    from sqlalchemy import text
                    db.session.execute(text("""
                        CREATE TABLE IF NOT EXISTS sub_users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username VARCHAR(80) UNIQUE NOT NULL,
                            email VARCHAR(120) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            parent_user_id INTEGER NOT NULL,
                            is_active BOOLEAN DEFAULT 1,
                            permissions TEXT DEFAULT '{}',
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            last_login DATETIME,
                            FOREIGN KEY (parent_user_id) REFERENCES users(id)
                        )
                    """))
                    db.session.commit()
                    print("  ✅ SubUser table created manually")
                except Exception as e2:
                    print(f"  ❌ Failed to create SubUser table: {e2}")
                    return False
            
            # Check users
            user_count = User.query.count()
            print(f"  ✅ Found {user_count} users in database")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Database setup failed: {e}")
        traceback.print_exc()
        return False

def start_application():
    """Start the main application"""
    print("🚀 Starting King's Choice Management App...")
    
    try:
        # Import and start the app
        from app import app
        
        # Get configuration
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        print(f"  - Host: {host}")
        print(f"  - Port: {port}")
        print(f"  - Debug: {debug}")
        print(f"  - Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        
        # Start the application
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        print(f"  ❌ Application startup failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main startup function"""
    print("🎯 King's Choice Management App - Safe Startup")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print()
    
    # Step 1: Setup database
    if not setup_database():
        print("\n❌ Database setup failed. Exiting.")
        sys.exit(1)
    
    print("\n✅ Database setup completed successfully!")
    
    # Step 2: Start application
    print("\n🚀 Starting application...")
    try:
        start_application()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Application crashed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
