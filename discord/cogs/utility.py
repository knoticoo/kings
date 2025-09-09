"""
Utility commands for Discord bot
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any
import logging
import asyncio

from core.database import DatabaseHelper
from utils.embeds import EmbedBuilder
from utils.helpers import TextHelper
from bot import bot

logger = logging.getLogger(__name__)

class UtilityCog(commands.Cog):
    """Utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = bot.db_manager
    
    @app_commands.command(name="help", description="Show help information")
    @app_commands.describe(command="Specific command to get help for")
    async def help_command(self, interaction: discord.Interaction, command: Optional[str] = None):
        """Show help information for commands"""
        await interaction.response.defer()
        
        try:
            if command:
                # Show help for specific command
                embed = await self.get_command_help(command)
            else:
                # Show general help
                embed = await self.get_general_help()
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing help: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to load help information.")
            await interaction.followup.send(embed=embed)
    
    async def get_general_help(self) -> discord.Embed:
        """Get general help embed"""
        embed = discord.Embed(
            title="🤖 King's Choice Bot Help",
            description="A comprehensive Discord bot for managing King's Choice game data.",
            color=0x0099ff,
            timestamp=discord.utils.utcnow()
        )
        
        # Player commands
        embed.add_field(
            name="👤 Player Commands",
            value="`/players` - List all players\n"
                  "`/addplayer` - Add new player (Admin)\n"
                  "`/editplayer` - Edit player name (Admin)\n"
                  "`/deleteplayer` - Delete player (Admin)\n"
                  "`/assignmvp` - Assign MVP (Admin)\n"
                  "`/playerinfo` - Get player details\n"
                  "`/mvpstatus` - Check MVP rotation status",
            inline=False
        )
        
        # Alliance commands
        embed.add_field(
            name="🏰 Alliance Commands",
            value="`/alliances` - List all alliances\n"
                  "`/addalliance` - Add new alliance (Admin)\n"
                  "`/editalliance` - Edit alliance name (Admin)\n"
                  "`/deletealliance` - Delete alliance (Admin)\n"
                  "`/assignwinner` - Assign winner (Admin)\n"
                  "`/allianceinfo` - Get alliance details\n"
                  "`/winnerstatus` - Check winner rotation status",
            inline=False
        )
        
        # Event commands
        embed.add_field(
            name="🎯 Event Commands",
            value="`/events` - List events\n"
                  "`/addevent` - Add new event (Admin)\n"
                  "`/editevent` - Edit event (Admin)\n"
                  "`/deleteevent` - Delete event (Admin)\n"
                  "`/eventinfo` - Get event details\n"
                  "`/availableevents` - Get available events",
            inline=False
        )
        
        # Guide commands
        embed.add_field(
            name="📖 Guide Commands",
            value="`/guides` - List guides\n"
                  "`/guide` - View specific guide\n"
                  "`/searchguides` - Search guides\n"
                  "`/categories` - List categories\n"
                  "`/featuredguides` - Show featured guides",
            inline=False
        )
        
        # Blacklist commands
        embed.add_field(
            name="🚫 Blacklist Commands",
            value="`/blacklist` - List blacklist entries\n"
                  "`/addblacklist` - Add to blacklist (Admin)\n"
                  "`/removeblacklist` - Remove from blacklist (Admin)\n"
                  "`/searchblacklist` - Search blacklist\n"
                  "`/blackliststats` - Show blacklist stats",
            inline=False
        )
        
        # Dashboard commands
        embed.add_field(
            name="📊 Dashboard Commands",
            value="`/dashboard` - Show main dashboard\n"
                  "`/stats` - Show detailed statistics\n"
                  "`/rotation` - Show rotation status\n"
                  "`/current` - Show current MVP/winner",
            inline=False
        )
        
        # Admin commands
        embed.add_field(
            name="🔧 Admin Commands",
            value="`/admin` - Show admin panel (Admin)\n"
                  "`/backup` - Create database backup (Admin)\n"
                  "`/validate` - Validate database (Admin)\n"
                  "`/cleanup` - Clean up data (Admin)\n"
                  "`/reload` - Reload cogs (Admin)\n"
                  "`/sync` - Sync commands (Admin)",
            inline=False
        )
        
        embed.set_footer(text="Use /help <command> for detailed help on a specific command")
        
        return embed
    
    async def get_command_help(self, command_name: str) -> discord.Embed:
        """Get help for specific command"""
        command_help = {
            "players": {
                "description": "List all players with their MVP status",
                "usage": "/players [show_excluded]",
                "parameters": "show_excluded: Include excluded players (optional, default: false)"
            },
            "addplayer": {
                "description": "Add a new player to the database",
                "usage": "/addplayer <name>",
                "parameters": "name: Player name (required)",
                "permission": "Admin required"
            },
            "assignmvp": {
                "description": "Assign MVP to a player for an event with rotation logic",
                "usage": "/assignmvp <player_id> <event_id>",
                "parameters": "player_id: Player ID (required), event_id: Event ID (required)",
                "permission": "Admin required"
            },
            "dashboard": {
                "description": "Show the main dashboard with current status",
                "usage": "/dashboard",
                "parameters": "None"
            },
            "guides": {
                "description": "List guides with optional filtering",
                "usage": "/guides [category] [search] [limit]",
                "parameters": "category: Filter by category (optional), search: Search term (optional), limit: Number of results (optional, default: 10)"
            }
        }
        
        if command_name.lower() not in command_help:
            return EmbedBuilder.create_error_embed(
                "Command Not Found",
                f"No help available for command '{command_name}'"
            )
        
        help_info = command_help[command_name.lower()]
        
        embed = discord.Embed(
            title=f"Help: /{command_name}",
            description=help_info["description"],
            color=0x0099ff
        )
        
        embed.add_field(
            name="Usage",
            value=f"`{help_info['usage']}`",
            inline=False
        )
        
        if "parameters" in help_info:
            embed.add_field(
                name="Parameters",
                value=help_info["parameters"],
                inline=False
            )
        
        if "permission" in help_info:
            embed.add_field(
                name="Permission",
                value=help_info["permission"],
                inline=False
            )
        
        return embed
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency and status"""
        await interaction.response.defer()
        
        try:
            # Get latency
            latency = round(self.bot.latency * 1000)
            
            # Get uptime
            uptime = self.bot.get_uptime()
            
            # Get database status
            try:
                await self.db_manager.execute_query("SELECT 1")
                db_status = "✅ Connected"
            except:
                db_status = "❌ Disconnected"
            
            # Create ping embed
            embed = discord.Embed(
                title="🏓 Pong!",
                color=0x00ff00 if latency < 200 else 0xffaa00 if latency < 500 else 0xff0000,
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(
                name="Latency",
                value=f"{latency}ms",
                inline=True
            )
            
            embed.add_field(
                name="Uptime",
                value=uptime,
                inline=True
            )
            
            embed.add_field(
                name="Database",
                value=db_status,
                inline=True
            )
            
            # Add status emoji based on latency
            if latency < 100:
                status = "🟢 Excellent"
            elif latency < 200:
                status = "🟡 Good"
            elif latency < 500:
                status = "🟠 Fair"
            else:
                status = "🔴 Poor"
            
            embed.add_field(
                name="Status",
                value=status,
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error checking ping: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to check bot status.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="info", description="Show bot information")
    async def bot_info(self, interaction: discord.Interaction):
        """Show bot information and statistics"""
        await interaction.response.defer()
        
        try:
            # Get bot statistics
            stats = await DatabaseHelper.get_stats(self.db_manager)
            
            # Get bot information
            uptime = self.bot.get_uptime()
            guild_count = len(self.bot.guilds)
            user_count = len(self.bot.users)
            command_count = len(self.bot.tree.get_commands())
            
            # Create info embed
            embed = discord.Embed(
                title="🤖 King's Choice Bot Information",
                description="A comprehensive Discord bot for managing King's Choice game data with fair rotation logic.",
                color=0x0099ff,
                timestamp=discord.utils.utcnow()
            )
            
            # Bot stats
            embed.add_field(
                name="Bot Statistics",
                value=f"Uptime: {uptime}\n"
                      f"Guilds: {guild_count}\n"
                      f"Users: {user_count}\n"
                      f"Commands: {command_count}",
                inline=True
            )
            
            # Database stats
            embed.add_field(
                name="Database Statistics",
                value=f"Players: {stats['total_players']}\n"
                      f"Alliances: {stats['total_alliances']}\n"
                      f"Events: {stats['total_events']}\n"
                      f"Guides: {stats['total_guides']}",
                inline=True
            )
            
            # Features
            features = []
            if self.bot.settings.enable_rotation_logic:
                features.append("🔄 Fair Rotation Logic")
            if self.bot.settings.enable_auto_announcements:
                features.append("📢 Auto Announcements")
            if self.bot.settings.enable_guide_system:
                features.append("📖 Guide System")
            if self.bot.settings.enable_blacklist:
                features.append("🚫 Blacklist Management")
            
            embed.add_field(
                name="Features",
                value="\n".join(features) if features else "No features enabled",
                inline=False
            )
            
            # Version and support
            embed.add_field(
                name="Version & Support",
                value=f"Version: 1.0.0\n"
                      f"Language: Python 3.8+\n"
                      f"Database: SQLite\n"
                      f"Framework: discord.py",
                inline=False
            )
            
            embed.set_footer(text="Use /help for command information")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing bot info: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to load bot information.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="invite", description="Get bot invite link")
    async def invite_link(self, interaction: discord.Interaction):
        """Get bot invite link"""
        await interaction.response.defer()
        
        try:
            # Create invite URL
            invite_url = discord.utils.oauth_url(
                client_id=self.bot.user.id,
                permissions=discord.Permissions(
                    send_messages=True,
                    embed_links=True,
                    use_slash_commands=True,
                    read_message_history=True
                )
            )
            
            embed = EmbedBuilder.create_info_embed(
                "Invite Link",
                f"Click [here]({invite_url}) to invite the bot to your server!\n\n"
                f"**Required Permissions:**\n"
                f"• Send Messages\n"
                f"• Embed Links\n"
                f"• Use Slash Commands\n"
                f"• Read Message History"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating invite link: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to create invite link.")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(UtilityCog(bot))