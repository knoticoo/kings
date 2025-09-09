"""
King's Choice Discord Bot
Main bot file with modular architecture
"""

import asyncio
import logging
import os
from typing import Optional

import discord
from discord.ext import commands

from config.settings import settings
from core.database import DatabaseManager
from core.rotation import RotationLogic
from utils.helpers import PermissionHelper

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KingsChoiceBot(commands.Bot):
    """Main bot class with enhanced functionality"""
    
    def __init__(self):
        # Validate settings
        try:
            settings.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=settings.command_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        # Initialize components
        self.db_manager = DatabaseManager(settings.database_path)
        self.rotation_logic = RotationLogic(self.db_manager)
        self.settings = settings
        
        # Bot state
        self.start_time = None
        self.guild_count = 0
        self.user_count = 0
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up King's Choice Discord Bot...")
        
        # Initialize database
        await self.init_database()
        
        # Load all cogs
        await self.load_cogs()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")
    
    async def init_database(self):
        """Initialize and validate database connection"""
        try:
            if not await self.db_manager.validate_database():
                raise Exception("Database validation failed")
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
        self.start_time = discord.utils.utcnow()
        self.guild_count = len(self.guilds)
        self.user_count = len(self.users)
        
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {self.guild_count} guilds with {self.user_count} users")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="King's Choice Management"
        )
        await self.change_presence(activity=activity)
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        self.guild_count = len(self.guilds)
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
        self.guild_count = len(self.guilds)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors globally"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
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
        
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        logger.error(f"Command error in {ctx.command}: {error}")
        await ctx.send("❌ An error occurred while executing the command.")
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        """Handle slash command errors"""
        if isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
            return
        
        logger.error(f"Slash command error in {interaction.command}: {error}")
        
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ An error occurred while executing the command.", ephemeral=True)
        else:
            await interaction.followup.send("❌ An error occurred while executing the command.", ephemeral=True)
    
    def get_uptime(self) -> str:
        """Get bot uptime as string"""
        if not self.start_time:
            return "Unknown"
        
        uptime = discord.utils.utcnow() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def check_admin_permission(self, member: discord.Member) -> bool:
        """Check if member has admin permission"""
        return PermissionHelper.has_required_permission(
            member, 
            admin_role=self.settings.admin_role,
            moderator_role=self.settings.moderator_role
        )
    
    def check_moderator_permission(self, member: discord.Member) -> bool:
        """Check if member has moderator permission"""
        return PermissionHelper.has_moderator_role(member, self.settings.moderator_role)

# Global bot instance
bot = KingsChoiceBot()

# Decorators for permission checking
def admin_required():
    """Decorator to require admin permission"""
    def predicate(ctx):
        if not bot.check_admin_permission(ctx.author):
            raise commands.CheckFailure("Admin permission required")
        return True
    return commands.check(predicate)

def moderator_required():
    """Decorator to require moderator permission"""
    def predicate(ctx):
        if not bot.check_moderator_permission(ctx.author):
            raise commands.CheckFailure("Moderator permission required")
        return True
    return commands.check(predicate)

# Slash command decorators
def slash_admin_required():
    """Decorator for slash commands requiring admin permission"""
    def predicate(interaction: discord.Interaction):
        if not bot.check_admin_permission(interaction.user):
            raise discord.app_commands.MissingPermissions(["admin"])
        return True
    return discord.app_commands.check(predicate)

def slash_moderator_required():
    """Decorator for slash commands requiring moderator permission"""
    def predicate(interaction: discord.Interaction):
        if not bot.check_moderator_permission(interaction.user):
            raise discord.app_commands.MissingPermissions(["moderator"])
        return True
    return discord.app_commands.check(predicate)

async def main():
    """Main function to start the bot"""
    try:
        logger.info("Starting King's Choice Discord Bot...")
        await bot.start(settings.discord_token)
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