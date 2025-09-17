#!/usr/bin/env python3
"""
Script to start bots for a specific user
Usage: python3 start_user_bots.py <user_id>
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User
from user_bot_manager import start_user_bots

def start_user_bots_script(user_id):
    """Start bots for a specific user"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User with ID {user_id} not found")
            return False
        
        print(f"🚀 Starting bots for user: {user.username}")
        
        # Start bots
        results = start_user_bots(
            user_id=user.id,
            discord_token=user.discord_bot_token if user.discord_enabled else None,
            discord_channel=user.discord_channel_id if user.discord_enabled else None,
            telegram_token=user.telegram_bot_token if user.telegram_enabled else None,
            telegram_chat=user.telegram_chat_id if user.telegram_enabled else None
        )
        
        print(f"📊 Results:")
        print(f"   Discord: {'✅ Started' if results.get('discord') else '❌ Failed'}")
        print(f"   Telegram: {'✅ Started' if results.get('telegram') else '❌ Failed'}")
        
        return any(results.values())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 start_user_bots.py <user_id>")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
        success = start_user_bots_script(user_id)
        sys.exit(0 if success else 1)
    except ValueError:
        print("❌ User ID must be a number")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)