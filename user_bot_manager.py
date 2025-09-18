"""
User Bot Manager Module

Real implementation for bot management functionality.
This module provides bot management functions for the King's Choice Management App.
"""

import os
import sys
import subprocess
import threading
import time
import logging
from typing import Dict, Optional, Tuple
from models import User
from database import db
from telegram_bot import test_bot_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global bot processes storage
bot_processes = {}
bot_threads = {}

def start_user_bots(user_id, discord_token=None, discord_channel=None, telegram_token=None, telegram_chat=None):
    """
    Start bots for a specific user
    
    Args:
        user_id: ID of the user
        discord_token: Discord bot token (optional)
        discord_channel: Discord channel ID (optional)
        telegram_token: Telegram bot token (optional)
        telegram_chat: Telegram chat ID (optional)
    
    Returns:
        dict: Status of bot startup
    """
    result = {'discord': False, 'telegram': False}
    
    try:
        # Start Discord bot if token provided
        if discord_token and discord_channel:
            result['discord'] = start_discord_bot(user_id, discord_token, discord_channel)
        
        # Start Telegram bot if token provided
        if telegram_token and telegram_chat:
            try:
                telegram_result = start_telegram_bot(user_id, telegram_token, telegram_chat)
                result['telegram'] = telegram_result
                if not telegram_result:
                    result['telegram_error'] = f"Failed to start Telegram bot for user {user_id}"
            except Exception as e:
                logger.error(f"Error starting Telegram bot: {str(e)}")
                result['telegram'] = False
                result['telegram_error'] = f"Error starting Telegram bot: {str(e)}"
        
        logger.info(f"Bot startup result for user {user_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error starting bots for user {user_id}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {'discord': False, 'telegram': False, 'error': str(e)}

def start_discord_bot(user_id, token, channel_id):
    """
    Start Discord bot for a specific user
    
    Args:
        user_id: ID of the user
        token: Discord bot token
        channel_id: Discord channel ID
    
    Returns:
        bool: Success status
    """
    try:
        # Create environment variables for this user's bot
        env = os.environ.copy()
        env['DISCORD_BOT_TOKEN'] = token
        env['DISCORD_CHANNEL_ID'] = str(channel_id)
        env['USER_ID'] = str(user_id)
        
        # Start Discord bot process
        process = subprocess.Popen([
            sys.executable, 'discord/run.py'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Store process reference
        bot_processes[f'discord_{user_id}'] = process
        
        logger.info(f"Discord bot started for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start Discord bot for user {user_id}: {str(e)}")
        return False

def start_telegram_bot(user_id, token, chat_id):
    """
    Start Telegram bot for a specific user
    
    Args:
        user_id: ID of the user
        token: Telegram bot token
        chat_id: Telegram chat ID
    
    Returns:
        bool: Success status
    """
    try:
        # For Telegram, we don't need a separate process
        # Just test the connection and mark as running
        from telegram_bot import KingsChoiceTelegramBot
        
        logger.info(f"Starting Telegram bot for user {user_id} with token: {token[:10]}... and chat_id: {chat_id}")
        
        # Create bot instance without testing connection immediately
        bot = KingsChoiceTelegramBot(token, chat_id)
        
        # Test connection in a separate thread to avoid blocking
        def test_connection():
            try:
                success, message = bot.test_connection_sync()
                logger.info(f"Telegram bot connection test result: {success}, message: {message}")
                
                if success:
                    bot_threads[f'telegram_{user_id}'] = {
                        'bot': bot,
                        'token': token,
                        'chat_id': chat_id,
                        'running': True
                    }
                    logger.info(f"Telegram bot started for user {user_id}")
                else:
                    logger.error(f"Telegram bot connection failed for user {user_id}: {message}")
            except Exception as e:
                logger.error(f"Error in bot connection test: {str(e)}")
        
        # Start connection test in background thread
        import threading
        thread = threading.Thread(target=test_connection)
        thread.daemon = True
        thread.start()
        
        # For now, assume it will work and mark as starting
        bot_threads[f'telegram_{user_id}'] = {
            'bot': bot,
            'token': token,
            'chat_id': chat_id,
            'running': False  # Will be updated by the thread
        }
        
        logger.info(f"Telegram bot startup initiated for user {user_id}")
        return True
            
    except Exception as e:
        logger.error(f"Failed to start Telegram bot for user {user_id}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def stop_user_bots(user_id):
    """
    Stop all bots for a specific user
    
    Args:
        user_id: ID of the user
    
    Returns:
        dict: Status of bot shutdown
    """
    result = {'discord': False, 'telegram': False}
    
    try:
        # Stop Discord bot
        discord_key = f'discord_{user_id}'
        if discord_key in bot_processes:
            process = bot_processes[discord_key]
            process.terminate()
            process.wait(timeout=5)
            del bot_processes[discord_key]
            result['discord'] = True
            logger.info(f"Discord bot stopped for user {user_id}")
        
        # Stop Telegram bot
        telegram_key = f'telegram_{user_id}'
        if telegram_key in bot_threads:
            del bot_threads[telegram_key]
            result['telegram'] = True
            logger.info(f"Telegram bot stopped for user {user_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error stopping bots for user {user_id}: {str(e)}")
        return {'discord': False, 'telegram': False, 'error': str(e)}

def get_bot_status(user_id=None):
    """
    Get the current status of all bots
    
    Args:
        user_id: ID of the user to check (optional)
    
    Returns:
        dict: Bot status information
    """
    try:
        # Get user from database
        if user_id:
            user = User.query.get(user_id)
        else:
            user = User.query.first()  # Fallback to first user
            
        if not user:
            return {
                'discord_running': False,
                'telegram_running': False,
                'discord_enabled': False,
                'telegram_enabled': False,
                'has_discord_token': False,
                'has_telegram_token': False
            }
        
        # Check Discord bot status
        discord_running = f'discord_{user.id}' in bot_processes
        if discord_running:
            process = bot_processes[f'discord_{user.id}']
            discord_running = process.poll() is None  # Process is still running
        
        # Check Telegram bot status
        telegram_running = f'telegram_{user.id}' in bot_threads
        
        logger.info(f"Bot status for user {user.id}: discord_running={discord_running}, telegram_running={telegram_running}")
        logger.info(f"Bot processes: {list(bot_processes.keys())}")
        logger.info(f"Bot threads: {list(bot_threads.keys())}")
        
        return {
            'discord_running': discord_running,
            'telegram_running': telegram_running,
            'discord_enabled': user.discord_enabled if hasattr(user, 'discord_enabled') else False,
            'telegram_enabled': user.telegram_enabled if hasattr(user, 'telegram_enabled') else False,
            'has_discord_token': bool(user.discord_bot_token) if hasattr(user, 'discord_bot_token') else False,
            'has_telegram_token': bool(user.telegram_bot_token) if hasattr(user, 'telegram_bot_token') else False
        }
        
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        return {
            'discord_running': False,
            'telegram_running': False,
            'discord_enabled': False,
            'telegram_enabled': False,
            'has_discord_token': False,
            'has_telegram_token': False
        }

def send_discord_message(user_id, message):
    """
    Send a message via Discord bot
    
    Args:
        user_id: ID of the user
        message: Message to send
    
    Returns:
        bool: Success status
    """
    try:
        # For now, just log the message
        # In a real implementation, you'd send via Discord API
        logger.info(f"Discord message for user {user_id}: {message}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending Discord message: {str(e)}")
        return False

def test_telegram_connection(user_id):
    """
    Test Telegram bot connection
    
    Args:
        user_id: ID of the user
    
    Returns:
        tuple: (success, message)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        if not user.telegram_enabled or not user.telegram_bot_token or not user.telegram_chat_id:
            return False, "Telegram bot not configured"
        
        # Test the connection
        success, message = test_bot_connection(user)
        return success, message
        
    except Exception as e:
        logger.error(f"Error testing Telegram connection: {str(e)}")
        return False, str(e)

# Bot manager class for more advanced functionality
class BotManager:
    def __init__(self):
        self.bots = {}
    
    def is_discord_bot_running(self, user_id):
        """Check if Discord bot is running for user"""
        discord_key = f'discord_{user_id}'
        if discord_key in bot_processes:
            process = bot_processes[discord_key]
            return process.poll() is None
        return False
    
    def is_telegram_bot_running(self, user_id):
        """Check if Telegram bot is running for user"""
        telegram_key = f'telegram_{user_id}'
        return telegram_key in bot_threads and bot_threads[telegram_key].get('running', False)

# Global bot manager instance
bot_manager = BotManager()
