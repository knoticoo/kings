#!/usr/bin/env python3
"""
Test script for the bot management system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User
from database import db
from user_bot_manager import bot_manager
from user_notifications import send_mvp_announcement, send_winner_announcement, test_user_notifications

def test_bot_system():
    """Test the complete bot management system"""
    print("🧪 Testing Bot Management System")
    print("=" * 50)
    
    with app.app_context():
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users in database")
        
        for user in users:
            print(f"\n👤 User: {user.username} (ID: {user.id})")
            print(f"   Telegram enabled: {user.telegram_enabled}")
            print(f"   Discord enabled: {user.discord_enabled}")
            print(f"   Has Telegram token: {bool(user.telegram_bot_token)}")
            print(f"   Has Discord token: {bool(user.discord_bot_token)}")
            
            # Test bot status
            discord_running = bot_manager.is_discord_bot_running(user.id)
            telegram_running = bot_manager.is_telegram_bot_running(user.id)
            print(f"   Discord bot running: {discord_running}")
            print(f"   Telegram bot running: {telegram_running}")
            
            # Test notifications if user has tokens
            if user.telegram_enabled and user.telegram_bot_token and user.telegram_chat_id:
                print("   Testing Telegram notifications...")
                try:
                    # Test MVP announcement
                    mvp_results = send_mvp_announcement(user.id, "Test Player", "Test Event")
                    print(f"   MVP announcement results: {mvp_results}")
                    
                    # Test winner announcement
                    winner_results = send_winner_announcement(user.id, "Test Alliance", "Test Event")
                    print(f"   Winner announcement results: {winner_results}")
                    
                except Exception as e:
                    print(f"   Error testing notifications: {e}")
            
            if user.discord_enabled and user.discord_bot_token and user.discord_channel_id:
                print("   Testing Discord notifications...")
                try:
                    # Test general notification
                    test_results = test_user_notifications(user.id)
                    print(f"   Test notification results: {test_results}")
                    
                except Exception as e:
                    print(f"   Error testing Discord notifications: {e}")
        
        # Test bot manager status
        print(f"\n📊 Bot Manager Status:")
        status = bot_manager.get_status()
        print(f"   Discord bots running: {status['discord_bots']}")
        print(f"   Telegram bots running: {status['telegram_bots']}")
        print(f"   Total users with bots: {status['total_users']}")

if __name__ == "__main__":
    test_bot_system()