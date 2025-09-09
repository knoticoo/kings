"""
Blacklist management commands for Discord bot
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any
import logging

from core.database import DatabaseHelper
from utils.embeds import EmbedBuilder
from utils.helpers import ValidationHelper, TextHelper
from bot import bot, slash_admin_required, slash_moderator_required

logger = logging.getLogger(__name__)

class BlacklistCog(commands.Cog):
    """Blacklist management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = bot.db_manager
    
    @app_commands.command(name="blacklist", description="List blacklist entries")
    @app_commands.describe(limit="Number of entries to show (default: 20)")
    async def list_blacklist(self, interaction: discord.Interaction, limit: int = 20):
        """List blacklist entries"""
        await interaction.response.defer()
        
        try:
            # Limit the number of entries
            if limit > 50:
                limit = 50
            elif limit < 1:
                limit = 20
            
            # Get blacklist entries
            query = "SELECT * FROM blacklist ORDER BY created_at DESC LIMIT ?"
            entries = await self.db_manager.execute_query(query, (limit,))
            
            if not entries:
                embed = EmbedBuilder.create_info_embed(
                    "Blacklist",
                    "No blacklist entries found."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Separate entries by type
            alliance_entries = [e for e in entries if e.get('alliance_name') and not e.get('player_name')]
            player_entries = [e for e in entries if e.get('player_name')]
            
            # Format entries
            entries_text = ""
            
            if alliance_entries:
                entries_text += "**Alliance Entries:**\n"
                for i, entry in enumerate(alliance_entries, 1):
                    alliance_name = entry['alliance_name']
                    date = TextHelper.format_datetime(entry['created_at'], "short")
                    entries_text += f"{i}. {alliance_name} ({date})\n"
                entries_text += "\n"
            
            if player_entries:
                entries_text += "**Player Entries:**\n"
                for i, entry in enumerate(player_entries, 1):
                    alliance_name = entry.get('alliance_name', '')
                    player_name = entry['player_name']
                    date = TextHelper.format_datetime(entry['created_at'], "short")
                    
                    if alliance_name:
                        entries_text += f"{i}. ({alliance_name}) {player_name} ({date})\n"
                    else:
                        entries_text += f"{i}. {player_name} ({date})\n"
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                f"Blacklist ({len(entries)} entries)",
                entries_text
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing blacklist: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to retrieve blacklist entries.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="addblacklist", description="Add entry to blacklist")
    @app_commands.describe(
        alliance_name="Alliance name (optional)",
        player_name="Player name (optional)"
    )
    @slash_admin_required()
    async def add_blacklist(self, interaction: discord.Interaction, 
                           alliance_name: Optional[str] = None,
                           player_name: Optional[str] = None):
        """Add entry to blacklist"""
        await interaction.response.defer()
        
        try:
            # Validate input
            if not alliance_name and not player_name:
                embed = EmbedBuilder.create_error_embed(
                    "Invalid Input", 
                    "Either alliance name or player name must be provided."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Clean names
            clean_alliance = TextHelper.clean_name(alliance_name) if alliance_name else None
            clean_player = TextHelper.clean_name(player_name) if player_name else None
            
            # Check for duplicates
            duplicate_query = """
                SELECT id FROM blacklist 
                WHERE alliance_name = ? AND player_name = ?
            """
            duplicates = await self.db_manager.execute_query(
                duplicate_query, 
                (clean_alliance, clean_player)
            )
            
            if duplicates:
                embed = EmbedBuilder.create_error_embed(
                    "Duplicate Entry", 
                    "This entry already exists in the blacklist."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Add to blacklist
            insert_query = """
                INSERT INTO blacklist (alliance_name, player_name, created_at, updated_at)
                VALUES (?, ?, datetime('now'), datetime('now'))
            """
            await self.db_manager.execute_update(insert_query, (clean_alliance, clean_player))
            
            # Create success message
            if clean_alliance and clean_player:
                entry_name = f"({clean_alliance}) {clean_player}"
            elif clean_alliance:
                entry_name = clean_alliance
            else:
                entry_name = clean_player
            
            embed = EmbedBuilder.create_success_embed(
                "Entry Added",
                f"Successfully added to blacklist: **{entry_name}**"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error adding to blacklist: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to add entry to blacklist.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="removeblacklist", description="Remove entry from blacklist")
    @app_commands.describe(entry_id="Blacklist entry ID")
    @slash_admin_required()
    async def remove_blacklist(self, interaction: discord.Interaction, entry_id: int):
        """Remove entry from blacklist"""
        await interaction.response.defer()
        
        try:
            # Check if entry exists
            entry_query = "SELECT * FROM blacklist WHERE id = ?"
            entries = await self.db_manager.execute_query(entry_query, (entry_id,))
            
            if not entries:
                embed = EmbedBuilder.create_error_embed(
                    "Entry Not Found", 
                    f"Blacklist entry with ID {entry_id} not found."
                )
                await interaction.followup.send(embed=embed)
                return
            
            entry = entries[0]
            
            # Create entry name for display
            if entry.get('alliance_name') and entry.get('player_name'):
                entry_name = f"({entry['alliance_name']}) {entry['player_name']}"
            elif entry.get('alliance_name'):
                entry_name = entry['alliance_name']
            else:
                entry_name = entry['player_name']
            
            # Remove from blacklist
            delete_query = "DELETE FROM blacklist WHERE id = ?"
            await self.db_manager.execute_update(delete_query, (entry_id,))
            
            embed = EmbedBuilder.create_success_embed(
                "Entry Removed",
                f"Successfully removed from blacklist: **{entry_name}**"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error removing from blacklist: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to remove entry from blacklist.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="searchblacklist", description="Search blacklist entries")
    @app_commands.describe(
        query="Search query",
        limit="Number of results (default: 10)"
    )
    async def search_blacklist(self, interaction: discord.Interaction, query: str, limit: int = 10):
        """Search blacklist entries"""
        await interaction.response.defer()
        
        try:
            # Limit the number of results
            if limit > 20:
                limit = 20
            elif limit < 1:
                limit = 10
            
            # Search blacklist entries
            search_query = """
                SELECT * FROM blacklist 
                WHERE alliance_name LIKE ? OR player_name LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            search_term = f"%{query}%"
            entries = await self.db_manager.execute_query(
                search_query, 
                (search_term, search_term, limit)
            )
            
            if not entries:
                embed = EmbedBuilder.create_info_embed(
                    "Search Results",
                    f"No blacklist entries found matching '{query}'."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format search results
            results_text = ""
            for i, entry in enumerate(entries, 1):
                alliance_name = entry.get('alliance_name', '')
                player_name = entry.get('player_name', '')
                date = TextHelper.format_datetime(entry['created_at'], "short")
                
                if alliance_name and player_name:
                    entry_display = f"({alliance_name}) {player_name}"
                elif alliance_name:
                    entry_display = alliance_name
                else:
                    entry_display = player_name
                
                results_text += f"{i}. {entry_display} ({date})\n"
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                f"Blacklist Search Results for '{query}' ({len(entries)})",
                results_text
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error searching blacklist: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to search blacklist.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="blackliststats", description="Show blacklist statistics")
    async def blacklist_stats(self, interaction: discord.Interaction):
        """Show blacklist statistics"""
        await interaction.response.defer()
        
        try:
            # Get total count
            total_query = "SELECT COUNT(*) as total FROM blacklist"
            total_result = await self.db_manager.execute_query(total_query)
            total_count = total_result[0]['total'] if total_result else 0
            
            # Get alliance entries count
            alliance_query = "SELECT COUNT(*) as count FROM blacklist WHERE alliance_name IS NOT NULL AND player_name IS NULL"
            alliance_result = await self.db_manager.execute_query(alliance_query)
            alliance_count = alliance_result[0]['count'] if alliance_result else 0
            
            # Get player entries count
            player_query = "SELECT COUNT(*) as count FROM blacklist WHERE player_name IS NOT NULL"
            player_result = await self.db_manager.execute_query(player_query)
            player_count = player_result[0]['count'] if player_result else 0
            
            # Get recent entries (last 7 days)
            recent_query = """
                SELECT COUNT(*) as count FROM blacklist 
                WHERE created_at >= datetime('now', '-7 days')
            """
            recent_result = await self.db_manager.execute_query(recent_query)
            recent_count = recent_result[0]['count'] if recent_result else 0
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                "Blacklist Statistics",
                f"**Total Entries:** {total_count}\n"
                f"**Alliance Entries:** {alliance_count}\n"
                f"**Player Entries:** {player_count}\n"
                f"**Recent (7 days):** {recent_count}"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting blacklist stats: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to retrieve blacklist statistics.")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(BlacklistCog(bot))