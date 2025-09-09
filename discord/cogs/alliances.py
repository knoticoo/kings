"""
Alliance management commands for Discord bot
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

class AlliancesCog(commands.Cog):
    """Alliance management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = bot.db_manager
        self.rotation_logic = bot.rotation_logic
    
    @app_commands.command(name="alliances", description="List all alliances")
    async def list_alliances(self, interaction: discord.Interaction):
        """List all alliances with their win status"""
        await interaction.response.defer()
        
        try:
            alliances = await DatabaseHelper.get_alliances(self.db_manager)
            
            if not alliances:
                embed = EmbedBuilder.create_info_embed(
                    "Alliances",
                    "No alliances found in the database."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format alliances list
            alliance_list = FormatHelper.format_alliance_list(alliances)
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                f"Alliances ({len(alliances)})",
                f"```{alliance_list}```"
            )
            
            # Add current winner info
            current_winner = await DatabaseHelper.get_current_winner(self.db_manager)
            if current_winner:
                embed.add_field(
                    name="Current Winner",
                    value=f"🏰 {current_winner['name']}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing alliances: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to retrieve alliances list.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="addalliance", description="Add a new alliance")
    @app_commands.describe(name="Alliance name")
    @slash_admin_required()
    async def add_alliance(self, interaction: discord.Interaction, name: str):
        """Add a new alliance to the database"""
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
            
            # Check if alliance already exists
            existing_alliances = await DatabaseHelper.get_alliances(self.db_manager)
            if any(a['name'].lower() == clean_name.lower() for a in existing_alliances):
                embed = EmbedBuilder.create_error_embed("Alliance Exists", f"Alliance '{clean_name}' already exists.")
                await interaction.followup.send(embed=embed)
                return
            
            # Add alliance to database
            query = """
                INSERT INTO alliances (name, is_current_winner, win_count, created_at, updated_at)
                VALUES (?, 0, 0, datetime('now'), datetime('now'))
            """
            await self.db_manager.execute_update(query, (clean_name,))
            
            embed = EmbedBuilder.create_success_embed(
                "Alliance Added",
                f"Successfully added alliance: **{clean_name}**"
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error adding alliance: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to add alliance.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="editalliance", description="Edit an alliance's name")
    @app_commands.describe(alliance_id="Alliance ID", new_name="New alliance name")
    @slash_admin_required()
    async def edit_alliance(self, interaction: discord.Interaction, alliance_id: int, new_name: str):
        """Edit an alliance's name"""
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
            
            # Check if alliance exists
            alliances = await DatabaseHelper.get_alliances(self.db_manager)
            alliance = next((a for a in alliances if a['id'] == alliance_id), None)
            
            if not alliance:
                embed = EmbedBuilder.create_error_embed("Alliance Not Found", f"Alliance with ID {alliance_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Check if new name conflicts with existing alliance
            if any(a['name'].lower() == clean_name.lower() and a['id'] != alliance_id for a in alliances):
                embed = EmbedBuilder.create_error_embed("Name Conflict", f"Alliance name '{clean_name}' is already taken.")
                await interaction.followup.send(embed=embed)
                return
            
            # Update alliance name
            old_name = alliance['name']
            query = "UPDATE alliances SET name = ?, updated_at = datetime('now') WHERE id = ?"
            await self.db_manager.execute_update(query, (clean_name, alliance_id))
            
            embed = EmbedBuilder.create_success_embed(
                "Alliance Updated",
                f"Alliance renamed from **{old_name}** to **{clean_name}**"
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error editing alliance: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to edit alliance.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="deletealliance", description="Delete an alliance")
    @app_commands.describe(alliance_id="Alliance ID")
    @slash_admin_required()
    async def delete_alliance(self, interaction: discord.Interaction, alliance_id: int):
        """Delete an alliance from the database"""
        await interaction.response.defer()
        
        try:
            # Check if alliance exists
            alliances = await DatabaseHelper.get_alliances(self.db_manager)
            alliance = next((a for a in alliances if a['id'] == alliance_id), None)
            
            if not alliance:
                embed = EmbedBuilder.create_error_embed("Alliance Not Found", f"Alliance with ID {alliance_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            alliance_name = alliance['name']
            
            # Delete alliance (cascading will handle winner assignments)
            query = "DELETE FROM alliances WHERE id = ?"
            await self.db_manager.execute_update(query, (alliance_id,))
            
            embed = EmbedBuilder.create_success_embed(
                "Alliance Deleted",
                f"Successfully deleted alliance: **{alliance_name}**"
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error deleting alliance: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to delete alliance.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="assignwinner", description="Assign winning alliance for an event")
    @app_commands.describe(alliance_id="Alliance ID", event_id="Event ID")
    @slash_admin_required()
    async def assign_winner(self, interaction: discord.Interaction, alliance_id: int, event_id: int):
        """Assign winning alliance for an event with rotation logic"""
        await interaction.response.defer()
        
        try:
            # Check if alliance exists
            alliances = await DatabaseHelper.get_alliances(self.db_manager)
            alliance = next((a for a in alliances if a['id'] == alliance_id), None)
            
            if not alliance:
                embed = EmbedBuilder.create_error_embed("Alliance Not Found", f"Alliance with ID {alliance_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Check if event exists
            events = await DatabaseHelper.get_events(self.db_manager)
            event = next((e for e in events if e['id'] == event_id), None)
            
            if not event:
                embed = EmbedBuilder.create_error_embed("Event Not Found", f"Event with ID {event_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Use rotation logic to assign winner
            success = await self.rotation_logic.assign_winner(alliance_id, event_id)
            
            if success:
                embed = EmbedBuilder.create_success_embed(
                    "Winner Assigned",
                    f"**{alliance['name']}** assigned as winner for **{event['name']}**"
                )
            else:
                embed = EmbedBuilder.create_error_embed(
                    "Assignment Failed",
                    "Winner assignment failed. Check rotation logic or alliance eligibility."
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error assigning winner: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to assign winner.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="winnerstatus", description="Check winner rotation status")
    async def winner_status(self, interaction: discord.Interaction):
        """Check winner rotation status and eligible alliances"""
        await interaction.response.defer()
        
        try:
            # Get rotation status
            status = await self.rotation_logic.get_rotation_status()
            winner_status = status['winner']
            
            can_assign = winner_status['can_assign']
            eligible_alliances = winner_status['eligible_alliances']
            stats = winner_status['stats']
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                "Winner Rotation Status",
                f"**Can assign winner:** {'✅ Yes' if can_assign else '❌ No'}"
            )
            
            # Add statistics
            if stats:
                embed.add_field(
                    name="Statistics",
                    value=f"Alliances with wins: {stats.get('alliances_with_wins', 0)}/{stats.get('total_alliances', 0)}\n"
                          f"Average win count: {stats.get('avg_win_count', 0):.1f}",
                    inline=False
                )
            
            # Add eligible alliances
            if eligible_alliances:
                alliance_names = [a['name'] for a in eligible_alliances[:10]]  # Limit to 10
                eligible_text = "\n".join(f"• {name}" for name in alliance_names)
                if len(eligible_alliances) > 10:
                    eligible_text += f"\n... and {len(eligible_alliances) - 10} more"
                
                embed.add_field(
                    name="Eligible Alliances",
                    value=eligible_text,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error checking winner status: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to check winner status.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="allianceinfo", description="Get detailed information about an alliance")
    @app_commands.describe(alliance_id="Alliance ID")
    async def alliance_info(self, interaction: discord.Interaction, alliance_id: int):
        """Get detailed information about a specific alliance"""
        await interaction.response.defer()
        
        try:
            # Get alliance info
            alliances = await DatabaseHelper.get_alliances(self.db_manager)
            alliance = next((a for a in alliances if a['id'] == alliance_id), None)
            
            if not alliance:
                embed = EmbedBuilder.create_error_embed("Alliance Not Found", f"Alliance with ID {alliance_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Get win history
            win_history_query = """
                SELECT e.name as event_name, e.event_date, wa.assigned_at
                FROM winner_assignments wa
                JOIN events e ON wa.event_id = e.id
                WHERE wa.alliance_id = ?
                ORDER BY wa.assigned_at DESC
            """
            win_history = await self.db_manager.execute_query(win_history_query, (alliance_id,))
            
            # Create alliance embed
            embed = EmbedBuilder.create_alliance_embed(alliance)
            
            # Add win history
            if win_history:
                history_text = ""
                for assignment in win_history[:5]:  # Show last 5 wins
                    event_name = assignment['event_name']
                    date = TextHelper.format_datetime(assignment['assigned_at'], "short")
                    history_text += f"• {event_name} ({date})\n"
                
                if len(win_history) > 5:
                    history_text += f"... and {len(win_history) - 5} more"
                
                embed.add_field(
                    name="Recent Wins",
                    value=history_text or "None",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting alliance info: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to get alliance information.")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AlliancesCog(bot))