"""
Telegram Bot for King's Choice Management App
Handles automatic announcements for MVP and winner assignments
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
from deep_translator import GoogleTranslator
from russian_templates import format_mvp_announcement, format_winner_announcement

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class KingsChoiceTelegramBot:
    def __init__(self, bot_token=None, channel_id=None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = channel_id or os.getenv('TELEGRAM_CHANNEL_ID')  # Should start with @channelname or -100...
        self.bot = None
        self._translator = None  # Lazy initialization
        
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not provided")
        if not self.channel_id:
            logger.warning("TELEGRAM_CHANNEL_ID not provided")
            
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
    
    @property
    def translator(self):
        """Lazy initialization of translator"""
        if self._translator is None:
            self._translator = GoogleTranslator(source='auto', target='ru')
        return self._translator
    
    async def send_message(self, message):
        """Send a message to the configured Telegram channel"""
        if not self.bot or not self.channel_id:
            logger.error("Bot token or channel ID not configured")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Message sent successfully: {message[:50]}...")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def send_message_sync(self, message):
        """Synchronous wrapper for sending messages"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.send_message(message))
    
    def announce_mvp(self, event_name, player_name):
        """Send MVP announcement to Telegram channel"""
        message = format_mvp_announcement(event_name, player_name)
        logger.info(f"Sending MVP announcement: {event_name} -> {player_name}")
        return self.send_message_sync(message)
    
    def announce_winner(self, event_name, alliance_name):
        """Send alliance winner announcement to Telegram channel"""
        message = format_winner_announcement(event_name, alliance_name)
        logger.info(f"Sending winner announcement: {event_name} -> {alliance_name}")
        return self.send_message_sync(message)
    
    def translate_and_send(self, text):
        """Translate text to Russian and send to channel"""
        try:
            # Translate to Russian
            russian_text = self.translator.translate(text)
            
            logger.info(f"Translated text: {text[:30]}... -> {russian_text[:30]}...")
            
            # Send the translated message
            return self.send_message_sync(russian_text)
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # If translation fails, send original text
            logger.info("Sending original text due to translation failure")
            return self.send_message_sync(text)
    
    async def test_connection(self):
        """Test the bot connection and channel access"""
        if not self.bot or not self.channel_id:
            return False, "Bot token or channel ID not configured"
        
        try:
            # Try to get bot info
            bot_info = await self.bot.get_me()
            logger.info(f"Bot connected: {bot_info.username}")
            
            # Try to send a test message
            test_message = "🤖 King's Choice Bot connection test"
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=test_message
            )
            
            return True, f"Bot {bot_info.username} connected successfully"
            
        except TelegramError as e:
            logger.error(f"Connection test failed: {e}")
            return False, str(e)
    
    def test_connection_sync(self):
        """Synchronous wrapper for testing connection"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.test_connection())

# Helper functions for easy import - now support user-specific configurations
def send_mvp_announcement(event_name, player_name, user=None):
    """Helper function to send MVP announcement for a specific user"""
    if user and user.telegram_enabled and user.telegram_bot_token and user.telegram_chat_id:
        bot = KingsChoiceTelegramBot(user.telegram_bot_token, user.telegram_chat_id)
        return bot.announce_mvp(event_name, player_name)
    else:
        logger.warning("Telegram bot not configured for user - skipping MVP announcement")
        return False

def send_winner_announcement(event_name, alliance_name, user=None):
    """Helper function to send winner announcement for a specific user"""
    if user and user.telegram_enabled and user.telegram_bot_token and user.telegram_chat_id:
        bot = KingsChoiceTelegramBot(user.telegram_bot_token, user.telegram_chat_id)
        return bot.announce_winner(event_name, alliance_name)
    else:
        logger.warning("Telegram bot not configured for user - skipping winner announcement")
        return False

def send_manual_message(text, user=None):
    """Helper function to translate and send manual message for a specific user"""
    if user and user.telegram_enabled and user.telegram_bot_token and user.telegram_chat_id:
        bot = KingsChoiceTelegramBot(user.telegram_bot_token, user.telegram_chat_id)
        return bot.translate_and_send(text)
    else:
        logger.warning("Telegram bot not configured for user - skipping manual message")
        return False

def test_bot_connection(user=None):
    """Helper function to test bot connection for a specific user"""
    if user and user.telegram_enabled and user.telegram_bot_token and user.telegram_chat_id:
        bot = KingsChoiceTelegramBot(user.telegram_bot_token, user.telegram_chat_id)
        return bot.test_connection_sync()
    else:
        logger.warning("Telegram bot not configured for user")
        return False, "Telegram bot not configured for user"

if __name__ == "__main__":
    # Test the bot if run directly
    print("Testing Telegram bot...")
    success, message = test_bot_connection()
    print(f"Connection test: {'✅ Success' if success else '❌ Failed'}")
    print(f"Message: {message}")
    
    if success:
        print("\nTesting announcements...")
        send_mvp_announcement("Test Event", "Test Player")
        send_winner_announcement("Test Event", "Test Alliance")
        send_manual_message("This is a test manual message that will be translated to Russian")