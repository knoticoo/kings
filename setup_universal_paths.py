#!/usr/bin/env python3
"""
Universal Path Setup Script for King's Choice Management App

This script helps configure the application for different deployment environments
and migrates existing data to the new universal path system.
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🔧 King's Choice Universal Path Setup")
    print("=" * 60)
    print()

def detect_current_setup():
    """Detect the current application setup"""
    print("🔍 Detecting current setup...")
    
    # Check if we can import the config
    try:
        from config import Config
        print(f"✅ Config module loaded from: {Config.APP_DIR}")
        
        deployment_type = Config.detect_deployment_type()
        print(f"🎯 Deployment type: {deployment_type}")
        
        # Check current paths
        print(f"📂 Current data directory: {Config.get_data_directory()}")
        print(f"📂 Current main DB path: {Config.get_main_database_path()}")
        print(f"📂 Current user DB dir: {Config.get_user_database_directory()}")
        
        return Config
    except ImportError as e:
        print(f"❌ Could not load config: {e}")
        return None

def find_existing_databases():
    """Find existing database files"""
    print("\n🔍 Looking for existing databases...")
    
    possible_locations = [
        Path.cwd() / "kings_choice.db",
        Path("/root/kings/kings_choice.db"),
        Path("/workspace/kings_choice.db"),
        Path.home() / "kings_choice.db",
    ]
    
    found_databases = []
    for location in possible_locations:
        try:
            if location.exists():
                print(f"✅ Found database: {location}")
                found_databases.append(location)
            else:
                print(f"❌ Not found: {location}")
        except PermissionError:
            print(f"🔒 Permission denied: {location}")
        except Exception as e:
            print(f"⚠️  Error checking {location}: {e}")
    
    return found_databases

def migrate_database(Config, old_db_path, new_db_path):
    """Migrate database to new location"""
    print(f"\n🚚 Migrating database...")
    print(f"   From: {old_db_path}")
    print(f"   To: {new_db_path}")
    
    # Ensure target directory exists
    new_db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy database
    shutil.copy2(old_db_path, new_db_path)
    print("✅ Database copied successfully")
    
    # Update user database paths in the database
    print("🔄 Updating user database paths...")
    conn = sqlite3.connect(new_db_path)
    cursor = conn.cursor()
    
    try:
        # Get all users
        cursor.execute('SELECT id, username FROM users')
        users = cursor.fetchall()
        
        for user_id, username in users:
            new_user_db_path = Config.get_user_database_path(user_id, username)
            cursor.execute('UPDATE users SET database_path = ? WHERE id = ?', 
                         (new_user_db_path, user_id))
            print(f"   Updated user {username}: {new_user_db_path}")
        
        conn.commit()
        print("✅ User database paths updated")
        
    except Exception as e:
        print(f"❌ Error updating user paths: {e}")
    finally:
        conn.close()

def create_user_databases(Config):
    """Create user database files"""
    print("\n🗄️ Creating user databases...")
    
    main_db_path = Config.get_main_database_path()
    if not Path(main_db_path).exists():
        print("❌ Main database not found. Please run the application first.")
        return
    
    # Import auth module for database creation
    sys.path.append(str(Config.APP_DIR))
    try:
        from auth import create_user_database
        
        # Get users from main database
        conn = sqlite3.connect(main_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, database_path FROM users')
        users = cursor.fetchall()
        conn.close()
        
        for user_id, username, db_path in users:
            print(f"📝 User {user_id} ({username}): {db_path}")
            
            if Path(db_path).exists():
                print(f"   ✅ Database already exists")
            else:
                try:
                    create_user_database(user_id, username)
                    print(f"   ✅ Database created successfully")
                except Exception as e:
                    print(f"   ❌ Error creating database: {e}")
        
    except ImportError as e:
        print(f"❌ Could not import auth module: {e}")

def setup_environment_file(Config):
    """Create environment file for the current setup"""
    print("\n📝 Setting up environment file...")
    
    env_file = Config.APP_DIR / ".env"
    
    # Determine recommended data directory based on deployment
    deployment_type = Config.detect_deployment_type()
    
    if deployment_type == 'vps_root':
        recommended_data_dir = "/root/kings_choice_data"
    elif deployment_type == 'vps_user':
        recommended_data_dir = f"{Path.home()}/kings_choice_data"
    else:
        recommended_data_dir = str(Config.APP_DIR / "data")
    
    env_content = f"""# King's Choice Environment Configuration
# Generated by setup_universal_paths.py

# Data directory (recommended for your deployment type: {deployment_type})
KINGS_CHOICE_DATA_DIR={recommended_data_dir}

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production

# Optional: Discord/Telegram Bot Configuration
# DISCORD_BOT_TOKEN=your-discord-bot-token
# TELEGRAM_BOT_TOKEN=your-telegram-bot-token
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Environment file created: {env_file}")
    print(f"📂 Recommended data directory: {recommended_data_dir}")

def main():
    print_banner()
    
    # Detect current setup
    Config = detect_current_setup()
    if not Config:
        print("❌ Cannot proceed without config module")
        return 1
    
    # Find existing databases
    existing_dbs = find_existing_databases()
    
    # Ensure data directories exist
    print("\n📁 Creating data directories...")
    Config.ensure_data_directories()
    
    # If we found existing databases, ask about migration
    current_main_db = Config.get_main_database_path()
    if existing_dbs and not Path(current_main_db).exists():
        print(f"\n🤔 Found existing databases but none at current location: {current_main_db}")
        
        # Use the first found database
        source_db = existing_dbs[0]
        migrate_database(Config, source_db, Path(current_main_db))
    
    # Create user databases
    create_user_databases(Config)
    
    # Setup environment file
    setup_environment_file(Config)
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print()
    print("🚀 Next steps:")
    print("1. Review and edit the .env file if needed")
    print("2. Start your application normally")
    print("3. The app will automatically use the new universal paths")
    print()
    print("🔧 To use a custom data directory, set:")
    print("   export KINGS_CHOICE_DATA_DIR=/your/custom/path")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())