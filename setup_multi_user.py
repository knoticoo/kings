#!/usr/bin/env python3
"""
Multi-User Setup Script for King's Choice Management App

This script sets up the multi-user system with:
1. Database initialization
2. Admin user creation
3. User database creation
4. System verification
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_system():
    """Setup the multi-user system"""
    print("🚀 Setting up King's Choice Management Multi-User System...")
    print("=" * 60)
    
    # Import after path setup
    from app import app
    from database import db, init_app, create_all_tables
    from models import User
    from auth import create_user_database
    
    with app.app_context():
        print("📊 Initializing main database...")
        init_app(app)
        create_all_tables(app)
        print("✅ Main database initialized")
        
        # Check if any users exist
        if User.query.first():
            print("👥 Users already exist. Current users:")
            for user in User.query.all():
                status = "Active" if user.is_active else "Inactive"
                admin = " (Admin)" if user.is_admin else ""
                print(f"  - {user.username} ({user.email}) - {status}{admin}")
            
            choice = input("\nDo you want to create a new admin user? (y/n): ").strip().lower()
            if choice != 'y':
                print("Setup complete!")
                return
        
        print("\n🔐 Creating admin user...")
        admin_username = input("Enter admin username (default: admin): ").strip() or "admin"
        admin_email = input("Enter admin email: ").strip()
        admin_password = input("Enter admin password: ").strip()
        
        if not admin_email or not admin_password:
            print("❌ Email and password are required!")
            return
        
        # Telegram configuration
        print("\n📱 Telegram Configuration (optional):")
        telegram_bot_token = input("Telegram Bot Token (press Enter to skip): ").strip()
        telegram_chat_id = input("Telegram Chat ID (press Enter to skip): ").strip()
        telegram_enabled = bool(telegram_bot_token and telegram_chat_id)
        
        # Discord configuration
        print("\n🎮 Discord Configuration (optional):")
        discord_bot_token = input("Discord Bot Token (press Enter to skip): ").strip()
        discord_channel_id = input("Discord Channel ID (press Enter to skip): ").strip()
        discord_enabled = bool(discord_bot_token and discord_channel_id)
        
        # Create database path
        basedir = os.path.abspath(os.path.dirname(__file__))
        admin_db_path = os.path.join(basedir, 'user_databases', f'admin_{admin_username}.db')
        
        # Create admin user
        admin_user = User(
            username=admin_username,
            email=admin_email,
            is_admin=True,
            is_active=True,
            database_path=admin_db_path,
            telegram_bot_token=telegram_bot_token if telegram_bot_token else None,
            telegram_chat_id=telegram_chat_id if telegram_chat_id else None,
            telegram_enabled=telegram_enabled,
            discord_bot_token=discord_bot_token if discord_bot_token else None,
            discord_channel_id=discord_channel_id if discord_channel_id else None,
            discord_enabled=discord_enabled
        )
        admin_user.set_password(admin_password)
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            # Create admin's database
            print("📁 Creating admin user database...")
            create_user_database(admin_user.id, admin_username)
            
            print("✅ Admin user created successfully!")
            print(f"   Username: {admin_username}")
            print(f"   Email: {admin_email}")
            print(f"   Database: {admin_db_path}")
            print(f"   Telegram: {'Enabled' if telegram_enabled else 'Disabled'}")
            print(f"   Discord: {'Enabled' if discord_enabled else 'Disabled'}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {str(e)}")
            return
        
        print("\n🎉 Multi-user system setup complete!")
        print("\nNext steps:")
        print("1. Run the application: python app.py")
        print("2. Login with your admin credentials")
        print("3. Create additional users via the admin panel")
        print("4. Configure Telegram/Discord for each user")
        print("\nAccess the admin panel at: /admin/users")

if __name__ == "__main__":
    setup_system()