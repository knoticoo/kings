"""
King's Choice Discord Bot
A standalone Discord bot that provides all the features from the web application

Features:
- Player management (add, edit, delete, MVP assignment)
- Alliance management (add, edit, delete, winner assignment) 
- Event management (create, edit, delete, view details)
- Guide system (list, search, view guides)
- Blacklist management (add, remove, list entries)
- Dashboard commands (current MVP, winner, stats)
- Fair rotation logic for assignments
- Multi-language support (English/Russian)
"""

import os
import asyncio
import logging
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from deep_translator import GoogleTranslator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot configuration
class BotConfig:
    def __init__(self):
        self.discord_token = os.getenv('DISCORD_BOT_TOKEN')
        from config import Config
        self.database_path = os.getenv('DATABASE_PATH', Config.MAIN_DATABASE_PATH)
        self.default_language = os.getenv('DEFAULT_LANGUAGE', 'en')
        self.admin_role = os.getenv('ADMIN_ROLE', 'Admin')
        self.prefix = os.getenv('BOT_PREFIX', '!kc')
        
        if not self.discord_token:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

config = BotConfig()

# Initialize translator
translator = GoogleTranslator(source='auto', target='ru')

class KingsChoiceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=config.prefix,
            intents=intents,
            help_command=None
        )
        
        self.db_path = config.database_path
        self.translator = translator
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up bot...")
        
        # Initialize database connection
        await self.init_database()
        
        # Load all cogs
        await self.load_cogs()
        
        # Sync commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def init_database(self):
        """Initialize database connection and verify tables exist"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if tables exist
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('players', 'alliances', 'events', 'mvp_assignments', 'winner_assignments', 'guides', 'guide_categories', 'blacklist')
                """)
                tables = await cursor.fetchall()
                
                if len(tables) < 8:
                    logger.error("Database tables not found. Please ensure the web app database is properly set up.")
                    raise Exception("Database tables missing")
                
                logger.info("Database connection established successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def load_cogs(self):
        """Load all command cogs"""
        cogs = [
            'cogs.players',
            'cogs.alliances', 
            'cogs.events',
            'cogs.guides',
            'cogs.blacklist',
            'cogs.dashboard',
            'cogs.admin',
            'cogs.utility'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name="King's Choice Management"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
            return
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
            return
        
        logger.error(f"Command error: {error}")
        await ctx.send("❌ An error occurred while executing the command.")
    
    def translate_text(self, text: str, target_lang: str = 'ru') -> str:
        """Translate text to target language"""
        try:
            if target_lang == 'ru':
                return self.translator.translate(text)
            return text
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    async def get_database_connection(self):
        """Get database connection"""
        return aiosqlite.connect(self.db_path)

# Utility functions for database operations
class DatabaseHelper:
    @staticmethod
    async def execute_query(db_path: str, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results as list of dictionaries"""
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    async def execute_update(db_path: str, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.rowcount
    
    @staticmethod
    async def execute_many(db_path: str, query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries in a transaction"""
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.executemany(query, params_list)
            await db.commit()
            return cursor.rowcount

# Rotation logic helper
class RotationLogic:
    @staticmethod
    async def can_assign_mvp(db_path: str) -> bool:
        """Check if MVP can be assigned (all players have been MVP at least once)"""
        query = """
            SELECT COUNT(*) as total_players,
                   COUNT(CASE WHEN mvp_count > 0 THEN 1 END) as players_with_mvp
            FROM players 
            WHERE is_excluded = 0
        """
        result = await DatabaseHelper.execute_query(db_path, query)
        if result:
            data = result[0]
            return data['players_with_mvp'] >= data['total_players']
        return False
    
    @staticmethod
    async def get_eligible_players(db_path: str) -> List[Dict]:
        """Get players eligible for MVP assignment"""
        query = """
            SELECT * FROM players 
            WHERE is_excluded = 0 
            ORDER BY mvp_count ASC, name ASC
        """
        return await DatabaseHelper.execute_query(db_path, query)
    
    @staticmethod
    async def can_assign_winner(db_path: str) -> bool:
        """Check if winner can be assigned (all alliances have won at least once)"""
        query = """
            SELECT COUNT(*) as total_alliances,
                   COUNT(CASE WHEN win_count > 0 THEN 1 END) as alliances_with_wins
            FROM alliances
        """
        result = await DatabaseHelper.execute_query(db_path, query)
        if result:
            data = result[0]
            return data['alliances_with_wins'] >= data['total_alliances']
        return False
    
    @staticmethod
    async def get_eligible_alliances(db_path: str) -> List[Dict]:
        """Get alliances eligible for winner assignment"""
        query = """
            SELECT * FROM alliances 
            ORDER BY win_count ASC, name ASC
        """
        return await DatabaseHelper.execute_query(db_path, query)

# Create bot instance
bot = KingsChoiceBot()

# Helper functions for user-specific bot management
def send_message_to_user(user_id, message):
    """Send message to a specific user's Discord channel"""
    try:
        from models import User
        user = User.query.get(user_id)
        if user and user.discord_enabled and user.discord_bot_token and user.discord_channel_id:
            # This would need to be implemented to send to the specific channel
            # For now, just log the message
            logger.info(f"Discord message for user {user_id}: {message}")
            return True
        else:
            logger.warning(f"Discord bot not configured for user {user_id}")
            return False
    except Exception as e:
        logger.error(f"Error sending message to user {user_id}: {str(e)}")
        return False

def send_mvp_announcement(event_name, player_name, user=None):
    """Helper function to send MVP announcement for a specific user"""
    if user and user.discord_enabled and user.discord_bot_token and user.discord_channel_id:
        message = f"🏆 **MVP Announcement**\n\nPlayer: **{player_name}**\nEvent: **{event_name}**\n\nCongratulations to {player_name} for being selected as MVP!"
        return send_message_to_user(user.id, message)
    else:
        logger.warning("Discord bot not configured for user - skipping MVP announcement")
        return False

def send_winner_announcement(event_name, alliance_name, user=None):
    """Helper function to send winner announcement for a specific user"""
    if user and user.discord_enabled and user.discord_bot_token and user.discord_channel_id:
        message = f"🎉 **Winner Announcement**\n\nAlliance: **{alliance_name}**\nEvent: **{event_name}**\n\nCongratulations to {alliance_name} for winning the event!"
        return send_message_to_user(user.id, message)
    else:
        logger.warning("Discord bot not configured for user - skipping winner announcement")
        return False

# Main command to start the bot
async def main():
    """Main function to start the bot"""
    try:
        await bot.start(config.discord_token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")