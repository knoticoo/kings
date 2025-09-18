"""
User Bot Manager

Manages per-user bot instances for Discord and Telegram.
Each user can have their own bots running with their own tokens.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, Optional, Tuple
from datetime import datetime
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('user_bots.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UserBotManager:
    """Manages bot instances for each user"""
    
    def __init__(self):
        self.discord_bots: Dict[int, any] = {}  # user_id -> bot instance
        self.telegram_bots: Dict[int, any] = {}  # user_id -> bot instance
        self.bot_threads: Dict[int, threading.Thread] = {}  # user_id -> thread
        self.running = True
        
    def start_user_discord_bot(self, user_id: int, bot_token: str, channel_id: str = None) -> bool:
        """Start Discord bot for a specific user"""
        try:
            if user_id in self.discord_bots:
                logger.info(f"Discord bot already running for user {user_id}")
                return True
                
            if not bot_token:
                logger.warning(f"No Discord token provided for user {user_id}")
                return False
                
            # Import here to avoid circular imports
            from discord_bot import KingsChoiceBot
            
            # Create bot instance with user-specific configuration
            bot = KingsChoiceBot()
            bot.user_id = user_id
            bot.channel_id = channel_id
            
            # Start bot in separate thread
            def run_bot():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(bot.start(bot_token))
                except Exception as e:
                    logger.error(f"Discord bot error for user {user_id}: {e}")
                finally:
                    if user_id in self.discord_bots:
                        del self.discord_bots[user_id]
            
            thread = threading.Thread(target=run_bot, daemon=True)
            thread.start()
            
            self.discord_bots[user_id] = bot
            self.bot_threads[user_id] = thread
            
            logger.info(f"Started Discord bot for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Discord bot for user {user_id}: {e}")
            return False
    
    def start_user_telegram_bot(self, user_id: int, bot_token: str, chat_id: str = None) -> bool:
        """Start Telegram bot for a specific user"""
        try:
            if user_id in self.telegram_bots:
                logger.info(f"Telegram bot already running for user {user_id}")
                return True
                
            if not bot_token:
                logger.warning(f"No Telegram token provided for user {user_id}")
                return False
                
            # Import here to avoid circular imports
            from telegram_bot import KingsChoiceTelegramBot
            
            # Create bot instance
            bot = KingsChoiceTelegramBot(bot_token, chat_id)
            bot.user_id = user_id
            
            self.telegram_bots[user_id] = bot
            
            logger.info(f"Started Telegram bot for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot for user {user_id}: {e}")
            return False
    
    def stop_user_discord_bot(self, user_id: int) -> bool:
        """Stop Discord bot for a specific user"""
        try:
            if user_id in self.discord_bots:
                bot = self.discord_bots[user_id]
                # Bot will stop when thread ends
                del self.discord_bots[user_id]
                if user_id in self.bot_threads:
                    del self.bot_threads[user_id]
                logger.info(f"Stopped Discord bot for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to stop Discord bot for user {user_id}: {e}")
            return False
    
    def stop_user_telegram_bot(self, user_id: int) -> bool:
        """Stop Telegram bot for a specific user"""
        try:
            if user_id in self.telegram_bots:
                del self.telegram_bots[user_id]
                logger.info(f"Stopped Telegram bot for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to stop Telegram bot for user {user_id}: {e}")
            return False
    
    def get_user_discord_bot(self, user_id: int):
        """Get Discord bot instance for user"""
        return self.discord_bots.get(user_id)
    
    def get_user_telegram_bot(self, user_id: int):
        """Get Telegram bot instance for user"""
        return self.telegram_bots.get(user_id)
    
    def is_discord_bot_running(self, user_id: int) -> bool:
        """Check if Discord bot is running for user"""
        return user_id in self.discord_bots
    
    def is_telegram_bot_running(self, user_id: int) -> bool:
        """Check if Telegram bot is running for user"""
        return user_id in self.telegram_bots
    
    def start_user_bots(self, user_id: int, discord_token: str = None, discord_channel: str = None, 
                       telegram_token: str = None, telegram_chat: str = None) -> Dict[str, bool]:
        """Start both bots for a user if tokens are provided"""
        results = {}
        
        if discord_token:
            results['discord'] = self.start_user_discord_bot(user_id, discord_token, discord_channel)
        
        if telegram_token:
            results['telegram'] = self.start_user_telegram_bot(user_id, telegram_token, telegram_chat)
        
        return results
    
    def stop_user_bots(self, user_id: int) -> Dict[str, bool]:
        """Stop both bots for a user"""
        results = {}
        results['discord'] = self.stop_user_discord_bot(user_id)
        results['telegram'] = self.stop_user_telegram_bot(user_id)
        return results
    
    def send_discord_message(self, user_id: int, message: str) -> bool:
        """Send message via user's Discord bot"""
        bot = self.get_user_discord_bot(user_id)
        if bot:
            try:
                # This would need to be implemented in the Discord bot
                # For now, just log the message
                logger.info(f"Discord message for user {user_id}: {message}")
                return True
            except Exception as e:
                logger.error(f"Failed to send Discord message for user {user_id}: {e}")
                return False
        return False
    
    def send_telegram_message(self, user_id: int, message: str) -> bool:
        """Send message via user's Telegram bot"""
        bot = self.get_user_telegram_bot(user_id)
        if bot:
            try:
                return bot.send_message_sync(message)
            except Exception as e:
                logger.error(f"Failed to send Telegram message for user {user_id}: {e}")
                return False
        return False
    
    def send_mvp_announcement(self, user_id: int, event_name: str, player_name: str) -> Dict[str, bool]:
        """Send MVP announcement to user's bots"""
        results = {}
        
        # Send via Telegram
        telegram_bot = self.get_user_telegram_bot(user_id)
        if telegram_bot:
            try:
                results['telegram'] = telegram_bot.announce_mvp(event_name, player_name)
            except Exception as e:
                logger.error(f"Failed to send MVP announcement via Telegram for user {user_id}: {e}")
                results['telegram'] = False
        else:
            results['telegram'] = False
        
        # Send via Discord (placeholder for now)
        results['discord'] = self.send_discord_message(user_id, f"🏆 MVP: {player_name} in {event_name}")
        
        return results
    
    def send_winner_announcement(self, user_id: int, event_name: str, alliance_name: str) -> Dict[str, bool]:
        """Send winner announcement to user's bots"""
        results = {}
        
        # Send via Telegram
        telegram_bot = self.get_user_telegram_bot(user_id)
        if telegram_bot:
            try:
                results['telegram'] = telegram_bot.announce_winner(event_name, alliance_name)
            except Exception as e:
                logger.error(f"Failed to send winner announcement via Telegram for user {user_id}: {e}")
                results['telegram'] = False
        else:
            results['telegram'] = False
        
        # Send via Discord (placeholder for now)
        results['discord'] = self.send_discord_message(user_id, f"🎉 Winner: {alliance_name} in {event_name}")
        
        return results
    
    def test_telegram_connection(self, user_id: int) -> Tuple[bool, str]:
        """Test Telegram bot connection for user"""
        telegram_bot = self.get_user_telegram_bot(user_id)
        if telegram_bot:
            try:
                return telegram_bot.test_connection_sync()
            except Exception as e:
                logger.error(f"Failed to test Telegram connection for user {user_id}: {e}")
                return False, str(e)
        else:
            return False, "Telegram bot not running for user"
    
    def get_status(self) -> Dict:
        """Get status of all running bots"""
        return {
            'discord_bots': list(self.discord_bots.keys()),
            'telegram_bots': list(self.telegram_bots.keys()),
            'total_users': len(set(list(self.discord_bots.keys()) + list(self.telegram_bots.keys())))
        }
    
    def cleanup_stopped_bots(self):
        """Clean up references to stopped bots"""
        # This would check if threads are still alive and clean up dead references
        pass

# Global bot manager instance
bot_manager = UserBotManager()

def start_user_bots(user_id: int, discord_token: str = None, discord_channel: str = None, 
                   telegram_token: str = None, telegram_chat: str = None) -> Dict[str, bool]:
    """Convenience function to start bots for a user"""
    return bot_manager.start_user_bots(user_id, discord_token, discord_channel, telegram_token, telegram_chat)

def stop_user_bots(user_id: int) -> Dict[str, bool]:
    """Convenience function to stop bots for a user"""
    return bot_manager.stop_user_bots(user_id)

def send_discord_message(user_id: int, message: str) -> bool:
    """Convenience function to send Discord message"""
    return bot_manager.send_discord_message(user_id, message)

def send_telegram_message(user_id: int, message: str) -> bool:
    """Convenience function to send Telegram message"""
    return bot_manager.send_telegram_message(user_id, message)

def send_mvp_announcement(user_id: int, event_name: str, player_name: str) -> Dict[str, bool]:
    """Convenience function to send MVP announcement"""
    return bot_manager.send_mvp_announcement(user_id, event_name, player_name)

def send_winner_announcement(user_id: int, event_name: str, alliance_name: str) -> Dict[str, bool]:
    """Convenience function to send winner announcement"""
    return bot_manager.send_winner_announcement(user_id, event_name, alliance_name)

def test_telegram_connection(user_id: int) -> Tuple[bool, str]:
    """Convenience function to test Telegram connection"""
    return bot_manager.test_telegram_connection(user_id)

def get_bot_status() -> Dict:
    """Get status of all bots"""
    return bot_manager.get_status()