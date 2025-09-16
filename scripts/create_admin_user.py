#!/usr/bin/env python3
"""
Admin User Creation Script for King's Choice Management App

This script creates a hardcoded admin user for initial system access.
Username: knotico
Password: Millie1991

Usage:
    python3 scripts/create_admin_user.py

Security:
    - Password is hashed using SHA-256 with salt
    - User is created with admin privileges
    - Database is initialized if it doesn't exist
"""

import os
import sys
import sqlite3
import hashlib
import secrets
from datetime import datetime

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def hash_password(password):
    """Hash password using SHA-256 with salt for security"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def create_database_schema(cursor):
    """Create the users table if it doesn't exist"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT 0 NOT NULL,
            is_active BOOLEAN DEFAULT 1 NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME,
            database_path VARCHAR(255) NOT NULL,
            telegram_bot_token VARCHAR(255),
            telegram_chat_id VARCHAR(100),
            telegram_enabled BOOLEAN DEFAULT 0 NOT NULL,
            discord_bot_token VARCHAR(255),
            discord_channel_id VARCHAR(100),
            discord_enabled BOOLEAN DEFAULT 0 NOT NULL
        )
    ''')
    print("✅ Database schema created/verified")

def create_admin_user():
    """Create the hardcoded admin user"""
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'kings_choice.db')
    
    print("🚀 Creating hardcoded admin user...")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create database schema
        create_database_schema(cursor)
        
        # Check if admin user already exists
        cursor.execute("SELECT id, username FROM users WHERE username = ?", ('knotico',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("⚠️  Admin user 'knotico' already exists!")
            print(f"   ID: {existing_user[0]}")
            
            # Update the existing user to ensure it's admin
            password_hash = hash_password('Millie1991')
            admin_db_path = os.path.join(project_root, 'user_databases', 'admin_knotico.db')
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, is_admin = 1, is_active = 1, email = ?, database_path = ?
                WHERE username = ?
            ''', (password_hash, 'admin@knotico.com', admin_db_path, 'knotico'))
            
            print("✅ Admin user updated successfully!")
        else:
            # Create new admin user
            password_hash = hash_password('Millie1991')
            admin_db_path = os.path.join(project_root, 'user_databases', 'admin_knotico.db')
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, is_admin, is_active, database_path, created_at, telegram_enabled, discord_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('knotico', 'admin@knotico.com', password_hash, 1, 1, admin_db_path, datetime.utcnow().isoformat(), 0, 0))
            
            print("✅ Admin user created successfully!")
        
        # Create user_databases directory
        user_db_dir = os.path.join(project_root, 'user_databases')
        os.makedirs(user_db_dir, exist_ok=True)
        print("✅ User databases directory created")
        
        # Commit changes
        conn.commit()
        
        # Display admin user details
        print("\n📋 Admin User Details:")
        print(f"   Username: knotico")
        print(f"   Email: admin@knotico.com")
        print(f"   Password: Millie1991")
        print(f"   Database: {admin_db_path}")
        print(f"   Is Admin: True")
        print(f"   Is Active: True")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function"""
    success = create_admin_user()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Admin user setup complete!")
        print("\nNext steps:")
        print("1. Start the application: python3 app.py")
        print("2. Login with username: knotico")
        print("3. Login with password: Millie1991")
        print("4. Access admin features at /admin/users")
    else:
        print("\n" + "=" * 50)
        print("❌ Admin user setup failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()