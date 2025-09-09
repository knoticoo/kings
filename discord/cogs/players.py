"""
Player management commands for Discord bot
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any
import logging

from core.database import DatabaseHelper
from core.rotation import RotationLogic
from utils.embeds import EmbedBuilder
from utils.helpers import ValidationHelper, FormatHelper, TextHelper
from bot import bot, slash_admin_required, slash_moderator_required

logger = logging.getLogger(__name__)

class PlayersCog(commands.Cog):
    """Player management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = bot.db_manager
        self.rotation_logic = bot.rotation_logic
    
    @app_commands.command(name="players", description="List all players")
    @app_commands.describe(show_excluded="Include excluded players in the list")
    async def list_players(self, interaction: discord.Interaction, show_excluded: bool = False):
        """List all players with their MVP status"""
        await interaction.response.defer()
        
        try:
            players = await DatabaseHelper.get_players(self.db_manager, include_excluded=show_excluded)
            
            if not players:
                embed = EmbedBuilder.create_info_embed(
                    "Players",
                    "No players found in the database."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format players list
            player_list = FormatHelper.format_player_list(players, show_mvp=True)
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                f"Players ({len(players)})",
                f"```{player_list}```"
            )
            
            # Add current MVP info
            current_mvp = await DatabaseHelper.get_current_mvp(self.db_manager)
            if current_mvp:
                embed.add_field(
                    name="Current MVP",
                    value=f"🏆 {current_mvp['name']}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing players: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to retrieve players list.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="addplayer", description="Add a new player")
    @app_commands.describe(name="Player name")
    @slash_admin_required()
    async def add_player(self, interaction: discord.Interaction, name: str):
        """Add a new player to the database"""
        await interaction.response.defer()
        
        try:
            # Validate name
            is_valid, error_msg = ValidationHelper.validate_name(name)
            if not is_valid:
                embed = EmbedBuilder.create_error_embed("Invalid Name", error_msg)
                await interaction.followup.send(embed=embed)
                return
            
            # Clean the name
            clean_name = TextHelper.clean_name(name)
            
            # Check if player already exists
            existing_players = await DatabaseHelper.get_players(self.db_manager, include_excluded=True)
            if any(p['name'].lower() == clean_name.lower() for p in existing_players):
                embed = EmbedBuilder.create_error_embed("Player Exists", f"Player '{clean_name}' already exists.")
                await interaction.followup.send(embed=embed)
                return
            
            # Add player to database
            query = """
                INSERT INTO players (name, is_current_mvp, is_excluded, mvp_count, created_at, updated_at)
                VALUES (?, 0, 0, 0, datetime('now'), datetime('now'))
            """
            await self.db_manager.execute_update(query, (clean_name,))
            
            embed = EmbedBuilder.create_success_embed(
                "Player Added",
                f"Successfully added player: **{clean_name}**"
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error adding player: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to add player.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="editplayer", description="Edit a player's name")
    @app_commands.describe(player_id="Player ID", new_name="New player name")
    @slash_admin_required()
    async def edit_player(self, interaction: discord.Interaction, player_id: int, new_name: str):
        """Edit a player's name"""
        await interaction.response.defer()
        
        try:
            # Validate new name
            is_valid, error_msg = ValidationHelper.validate_name(new_name)
            if not is_valid:
                embed = EmbedBuilder.create_error_embed("Invalid Name", error_msg)
                await interaction.followup.send(embed=embed)
                return
            
            # Clean the name
            clean_name = TextHelper.clean_name(new_name)
            
            # Check if player exists
            players = await DatabaseHelper.get_players(self.db_manager, include_excluded=True)
            player = next((p for p in players if p['id'] == player_id), None)
            
            if not player:
                embed = EmbedBuilder.create_error_embed("Player Not Found", f"Player with ID {player_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Check if new name conflicts with existing player
            if any(p['name'].lower() == clean_name.lower() and p['id'] != player_id for p in players):
                embed = EmbedBuilder.create_error_embed("Name Conflict", f"Player name '{clean_name}' is already taken.")
                await interaction.followup.send(embed=embed)
                return
            
            # Update player name
            old_name = player['name']
            query = "UPDATE players SET name = ?, updated_at = datetime('now') WHERE id = ?"
            await self.db_manager.execute_update(query, (clean_name, player_id))
            
            embed = EmbedBuilder.create_success_embed(
                "Player Updated",
                f"Player renamed from **{old_name}** to **{clean_name}**"
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error editing player: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to edit player.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="deleteplayer", description="Delete a player")
    @app_commands.describe(player_id="Player ID")
    @slash_admin_required()
    async def delete_player(self, interaction: discord.Interaction, player_id: int):
        """Delete a player from the database"""
        await interaction.response.defer()
        
        try:
            # Check if player exists
            players = await DatabaseHelper.get_players(self.db_manager, include_excluded=True)
            player = next((p for p in players if p['id'] == player_id), None)
            
            if not player:
                embed = EmbedBuilder.create_error_embed("Player Not Found", f"Player with ID {player_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            player_name = player['name']
            
            # Delete player (cascading will handle MVP assignments)
            query = "DELETE FROM players WHERE id = ?"
            await self.db_manager.execute_update(query, (player_id,))
            
            embed = EmbedBuilder.create_success_embed(
                "Player Deleted",
                f"Successfully deleted player: **{player_name}**"
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error deleting player: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to delete player.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="toggleexclusion", description="Toggle player exclusion from MVP rotation")
    @app_commands.describe(player_id="Player ID")
    @slash_admin_required()
    async def toggle_exclusion(self, interaction: discord.Interaction, player_id: int):
        """Toggle player exclusion from MVP rotation"""
        await interaction.response.defer()
        
        try:
            # Check if player exists
            players = await DatabaseHelper.get_players(self.db_manager, include_excluded=True)
            player = next((p for p in players if p['id'] == player_id), None)
            
            if not player:
                embed = EmbedBuilder.create_error_embed("Player Not Found", f"Player with ID {player_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            player_name = player['name']
            current_excluded = player['is_excluded']
            new_excluded = not current_excluded
            
            # Update exclusion status
            query = "UPDATE players SET is_excluded = ?, updated_at = datetime('now') WHERE id = ?"
            await self.db_manager.execute_update(query, (int(new_excluded), player_id))
            
            # If excluding current MVP, remove their MVP status
            if new_excluded and player['is_current_mvp']:
                await self.db_manager.execute_update(
                    "UPDATE players SET is_current_mvp = 0 WHERE id = ?",
                    (player_id,)
                )
                status_msg = f"Player **{player_name}** excluded from MVP rotation and removed as current MVP"
            elif new_excluded:
                status_msg = f"Player **{player_name}** excluded from MVP rotation"
            else:
                status_msg = f"Player **{player_name}** included in MVP rotation"
            
            embed = EmbedBuilder.create_success_embed("Exclusion Updated", status_msg)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error toggling exclusion: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to toggle player exclusion.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="assignmvp", description="Assign MVP to a player for an event")
    @app_commands.describe(player_id="Player ID", event_id="Event ID")
    @slash_admin_required()
    async def assign_mvp(self, interaction: discord.Interaction, player_id: int, event_id: int):
        """Assign MVP to a player for an event with rotation logic"""
        await interaction.response.defer()
        
        try:
            # Check if player exists
            players = await DatabaseHelper.get_players(self.db_manager, include_excluded=True)
            player = next((p for p in players if p['id'] == player_id), None)
            
            if not player:
                embed = EmbedBuilder.create_error_embed("Player Not Found", f"Player with ID {player_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Check if event exists
            events = await DatabaseHelper.get_events(self.db_manager)
            event = next((e for e in events if e['id'] == event_id), None)
            
            if not event:
                embed = EmbedBuilder.create_error_embed("Event Not Found", f"Event with ID {event_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Use rotation logic to assign MVP
            success = await self.rotation_logic.assign_mvp(player_id, event_id)
            
            if success:
                embed = EmbedBuilder.create_success_embed(
                    "MVP Assigned",
                    f"**{player['name']}** assigned as MVP for **{event['name']}**"
                )
            else:
                embed = EmbedBuilder.create_error_embed(
                    "Assignment Failed",
                    "MVP assignment failed. Check rotation logic or player eligibility."
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error assigning MVP: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to assign MVP.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="mvpstatus", description="Check MVP rotation status")
    async def mvp_status(self, interaction: discord.Interaction):
        """Check MVP rotation status and eligible players"""
        await interaction.response.defer()
        
        try:
            # Get rotation status
            status = await self.rotation_logic.get_rotation_status()
            mvp_status = status['mvp']
            
            can_assign = mvp_status['can_assign']
            eligible_players = mvp_status['eligible_players']
            stats = mvp_status['stats']
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                "MVP Rotation Status",
                f"**Can assign MVP:** {'✅ Yes' if can_assign else '❌ No'}"
            )
            
            # Add statistics
            if stats:
                embed.add_field(
                    name="Statistics",
                    value=f"Players with MVP: {stats.get('players_with_mvp', 0)}/{stats.get('total_players', 0)}\n"
                          f"Average MVP count: {stats.get('avg_mvp_count', 0):.1f}",
                    inline=False
                )
            
            # Add eligible players
            if eligible_players:
                player_names = [p['name'] for p in eligible_players[:10]]  # Limit to 10
                eligible_text = "\n".join(f"• {name}" for name in player_names)
                if len(eligible_players) > 10:
                    eligible_text += f"\n... and {len(eligible_players) - 10} more"
                
                embed.add_field(
                    name="Eligible Players",
                    value=eligible_text,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error checking MVP status: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to check MVP status.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="playerinfo", description="Get detailed information about a player")
    @app_commands.describe(player_id="Player ID")
    async def player_info(self, interaction: discord.Interaction, player_id: int):
        """Get detailed information about a specific player"""
        await interaction.response.defer()
        
        try:
            # Get player info
            players = await DatabaseHelper.get_players(self.db_manager, include_excluded=True)
            player = next((p for p in players if p['id'] == player_id), None)
            
            if not player:
                embed = EmbedBuilder.create_error_embed("Player Not Found", f"Player with ID {player_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Get MVP history
            mvp_history_query = """
                SELECT e.name as event_name, e.event_date, ma.assigned_at
                FROM mvp_assignments ma
                JOIN events e ON ma.event_id = e.id
                WHERE ma.player_id = ?
                ORDER BY ma.assigned_at DESC
            """
            mvp_history = await self.db_manager.execute_query(mvp_history_query, (player_id,))
            
            # Create player embed
            embed = EmbedBuilder.create_player_embed(player)
            
            # Add MVP history
            if mvp_history:
                history_text = ""
                for assignment in mvp_history[:5]:  # Show last 5 assignments
                    event_name = assignment['event_name']
                    date = TextHelper.format_datetime(assignment['assigned_at'], "short")
                    history_text += f"• {event_name} ({date})\n"
                
                if len(mvp_history) > 5:
                    history_text += f"... and {len(mvp_history) - 5} more"
                
                embed.add_field(
                    name="Recent MVP Assignments",
                    value=history_text or "None",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting player info: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to get player information.")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(PlayersCog(bot))