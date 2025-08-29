"""
Telegram Bot for King's Choice Management App
Handles automatic announcements for MVP and winner assignments
"""

import os
import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from googletrans import Translator
from russian_templates import format_mvp_announcement, format_winner_announcement

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class KingsChoiceTelegramBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')  # Should start with @channelname or -100...
        self.bot = None
        self.translator = Translator()
        
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not found in environment variables")
        if not self.channel_id:
            logger.warning("TELEGRAM_CHANNEL_ID not found in environment variables")
            
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
    
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
            translated = self.translator.translate(text, dest='ru')
            russian_text = translated.text
            
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

# Global bot instance
telegram_bot = KingsChoiceTelegramBot()

# Helper functions for easy import
def send_mvp_announcement(event_name, player_name):
    """Helper function to send MVP announcement"""
    return telegram_bot.announce_mvp(event_name, player_name)

def send_winner_announcement(event_name, alliance_name):
    """Helper function to send winner announcement"""
    return telegram_bot.announce_winner(event_name, alliance_name)

def send_manual_message(text):
    """Helper function to translate and send manual message"""
    return telegram_bot.translate_and_send(text)

def test_bot_connection():
    """Helper function to test bot connection"""
    return telegram_bot.test_connection_sync()

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