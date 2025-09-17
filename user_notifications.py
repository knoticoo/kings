"""
User-specific notification service for King's Choice Management App

Handles sending notifications to user-specific Telegram and Discord channels.
Uses the bot manager for proper bot lifecycle management.
"""

import logging
from flask import current_app
from models import User
from user_bot_manager import bot_manager

# Configure logging
logger = logging.getLogger(__name__)

def send_telegram_message(user_id, message, parse_mode='HTML'):
    """
    Send a message to the user's Telegram channel using bot manager
    
    Args:
        user_id: ID of the user
        message: Message to send
        parse_mode: Telegram parse mode (HTML, Markdown, etc.)
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        user = User.query.get(user_id)
        if not user or not user.telegram_enabled or not user.telegram_bot_token or not user.telegram_chat_id:
            logger.warning(f"Telegram not configured for user {user_id}")
            return False
        
        # Use bot manager to send message
        return bot_manager.send_telegram_message(user_id, message)
            
    except Exception as e:
        logger.error(f"Error sending Telegram message: {str(e)}")
        return False

def send_discord_message(user_id, message, embed=None):
    """
    Send a message to the user's Discord channel using bot manager
    
    Args:
        user_id: ID of the user
        message: Message to send
        embed: Optional Discord embed object
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        user = User.query.get(user_id)
        if not user or not user.discord_enabled or not user.discord_bot_token or not user.discord_channel_id:
            logger.warning(f"Discord not configured for user {user_id}")
            return False
        
        # Use bot manager to send message
        return bot_manager.send_discord_message(user_id, message)
            
    except Exception as e:
        logger.error(f"Error sending Discord message: {str(e)}")
        return False

def send_notification(user_id, message, telegram=True, discord=True):
    """
    Send notification to both Telegram and Discord if enabled
    
    Args:
        user_id: ID of the user
        message: Message to send
        telegram: Whether to send to Telegram
        discord: Whether to send to Discord
    
    Returns:
        dict: Results for each platform
    """
    results = {
        'telegram': False,
        'discord': False
    }
    
    if telegram:
        results['telegram'] = send_telegram_message(user_id, message)
    
    if discord:
        results['discord'] = send_discord_message(user_id, message)
    
    return results

def send_mvp_announcement(user_id, player_name, event_name):
    """
    Send MVP announcement to user's channels using bot manager
    
    Args:
        user_id: ID of the user
        player_name: Name of the MVP player
        event_name: Name of the event
    
    Returns:
        dict: Results for each platform
    """
    try:
        # Use bot manager for MVP announcements
        return bot_manager.send_mvp_announcement(user_id, event_name, player_name)
    except Exception as e:
        logger.error(f"Error sending MVP announcement for user {user_id}: {str(e)}")
        return {'telegram': False, 'discord': False}

def send_winner_announcement(user_id, alliance_name, event_name):
    """
    Send winner announcement to user's channels using bot manager
    
    Args:
        user_id: ID of the user
        alliance_name: Name of the winning alliance
        event_name: Name of the event
    
    Returns:
        dict: Results for each platform
    """
    try:
        # Use bot manager for winner announcements
        return bot_manager.send_winner_announcement(user_id, event_name, alliance_name)
    except Exception as e:
        logger.error(f"Error sending winner announcement for user {user_id}: {str(e)}")
        return {'telegram': False, 'discord': False}

def test_user_notifications(user_id):
    """
    Test user's notification settings by sending a test message
    
    Args:
        user_id: ID of the user
    
    Returns:
        dict: Results for each platform
    """
    message = "🧪 <b>Test Message</b>\n\nThis is a test message to verify your notification settings are working correctly."
    
    return send_notification(user_id, message)

def ensure_user_bots_running(user_id):
    """
    Ensure that user's bots are running if they have tokens configured
    
    Args:
        user_id: ID of the user
    
    Returns:
        dict: Results for starting bots
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {'discord': False, 'telegram': False}
        
        results = {}
        
        # Start Discord bot if configured and not running
        if (user.discord_enabled and user.discord_bot_token and 
            not bot_manager.is_discord_bot_running(user_id)):
            results['discord'] = bot_manager.start_user_discord_bot(
                user_id, user.discord_bot_token, user.discord_channel_id
            )
        else:
            results['discord'] = bot_manager.is_discord_bot_running(user_id)
        
        # Start Telegram bot if configured and not running
        if (user.telegram_enabled and user.telegram_bot_token and user.telegram_chat_id and
            not bot_manager.is_telegram_bot_running(user_id)):
            results['telegram'] = bot_manager.start_user_telegram_bot(
                user_id, user.telegram_bot_token, user.telegram_chat_id
            )
        else:
            results['telegram'] = bot_manager.is_telegram_bot_running(user_id)
        
        return results
        
    except Exception as e:
        logger.error(f"Error ensuring bots are running for user {user_id}: {str(e)}")
        return {'discord': False, 'telegram': False}