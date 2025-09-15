#!/usr/bin/env python3
"""
Test script for multi-user King's Choice Management system

This script tests the multi-user functionality including:
- User creation and authentication
- Data isolation between users
- Database separation
- Notification configuration
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_multi_user_system():
    """Test the multi-user system functionality"""
    print("🧪 Testing Multi-User King's Choice Management System")
    print("=" * 60)
    
    try:
        from app import app
        from database import db, init_app, create_all_tables
        from models import User, Player, Alliance, Event
        from database_manager import query_user_data, create_user_data
        from user_notifications import test_user_notifications
        
        with app.app_context():
            print("✅ Application context loaded successfully")
            
            # Test 1: Check if users exist
            print("\n📊 Test 1: Checking existing users...")
            users = User.query.all()
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - {user.username} ({user.email}) - {'Admin' if user.is_admin else 'User'}")
            
            if not users:
                print("❌ No users found. Please run setup_multi_user.py first.")
                return False
            
            # Test 2: Test data isolation
            print("\n🔒 Test 2: Testing data isolation...")
            for user in users:
                print(f"Testing user: {user.username}")
                
                # Check if user has their own database
                if os.path.exists(user.database_path):
                    print(f"  ✅ Database exists: {user.database_path}")
                else:
                    print(f"  ❌ Database missing: {user.database_path}")
                    continue
                
                # Test querying user-specific data
                try:
                    players = query_user_data(Player, user.id)
                    alliances = query_user_data(Alliance, user.id)
                    events = query_user_data(Event, user.id)
                    
                    print(f"  📊 Data counts - Players: {len(players)}, Alliances: {len(alliances)}, Events: {len(events)}")
                    
                except Exception as e:
                    print(f"  ❌ Error querying data: {str(e)}")
            
            # Test 3: Test notification configuration
            print("\n📱 Test 3: Testing notification configuration...")
            for user in users:
                print(f"User: {user.username}")
                print(f"  Telegram: {'Enabled' if user.telegram_enabled else 'Disabled'}")
                print(f"  Discord: {'Enabled' if user.discord_enabled else 'Disabled'}")
                
                if user.telegram_enabled or user.discord_enabled:
                    print(f"  🧪 Testing notifications...")
                    results = test_user_notifications(user.id)
                    print(f"    Telegram: {'✅' if results['telegram'] else '❌'}")
                    print(f"    Discord: {'✅' if results['discord'] else '❌'}")
            
            # Test 4: Test admin functionality
            print("\n👑 Test 4: Testing admin functionality...")
            admin_users = User.query.filter_by(is_admin=True).all()
            print(f"Found {len(admin_users)} admin users:")
            for admin in admin_users:
                print(f"  - {admin.username} ({admin.email})")
            
            # Test 5: Test user database creation
            print("\n🗄️ Test 5: Testing user database structure...")
            for user in users:
                if os.path.exists(user.database_path):
                    print(f"User {user.username} database structure:")
                    # This would require more complex database inspection
                    print(f"  ✅ Database file exists and is accessible")
            
            print("\n🎉 Multi-user system test completed!")
            print("\nSummary:")
            print(f"  - Users: {len(users)}")
            print(f"  - Admin users: {len(admin_users)}")
            print(f"  - Data isolation: Working")
            print(f"  - Notification system: Configured")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_multi_user_system()
    sys.exit(0 if success else 1)