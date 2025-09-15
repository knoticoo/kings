"""
User-specific notification service for King's Choice Management App

Handles sending notifications to user-specific Telegram and Discord channels.
"""

import requests
import json
from flask import current_app
from models import User

def send_telegram_message(user_id, message, parse_mode='HTML'):
    """
    Send a message to the user's Telegram channel
    
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
            return False
        
        url = f"https://api.telegram.org/bot{user.telegram_bot_token}/sendMessage"
        
        data = {
            'chat_id': user.telegram_chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('ok', False)
        else:
            print(f"Telegram API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending Telegram message: {str(e)}")
        return False

def send_discord_message(user_id, message, embed=None):
    """
    Send a message to the user's Discord channel
    
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
            return False
        
        url = f"https://discord.com/api/v10/channels/{user.discord_channel_id}/messages"
        
        headers = {
            'Authorization': f'Bot {user.discord_bot_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'content': message
        }
        
        if embed:
            payload['embeds'] = [embed]
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Discord API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending Discord message: {str(e)}")
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
    Send MVP announcement to user's channels
    
    Args:
        user_id: ID of the user
        player_name: Name of the MVP player
        event_name: Name of the event
    
    Returns:
        dict: Results for each platform
    """
    message = f"🏆 <b>MVP Announcement</b>\n\n"
    message += f"Player: <b>{player_name}</b>\n"
    message += f"Event: <b>{event_name}</b>\n\n"
    message += f"Congratulations to {player_name} for being selected as MVP!"
    
    return send_notification(user_id, message)

def send_winner_announcement(user_id, alliance_name, event_name):
    """
    Send winner announcement to user's channels
    
    Args:
        user_id: ID of the user
        alliance_name: Name of the winning alliance
        event_name: Name of the event
    
    Returns:
        dict: Results for each platform
    """
    message = f"🎉 <b>Winner Announcement</b>\n\n"
    message += f"Alliance: <b>{alliance_name}</b>\n"
    message += f"Event: <b>{event_name}</b>\n\n"
    message += f"Congratulations to {alliance_name} for winning the event!"
    
    return send_notification(user_id, message)

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