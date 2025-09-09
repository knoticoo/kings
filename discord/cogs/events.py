"""
Event management commands for Discord bot
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from core.database import DatabaseHelper
from utils.embeds import EmbedBuilder
from utils.helpers import ValidationHelper, FormatHelper, TextHelper
from bot import bot, slash_admin_required, slash_moderator_required

logger = logging.getLogger(__name__)

class EventsCog(commands.Cog):
    """Event management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = bot.db_manager
    
    @app_commands.command(name="events", description="List all events")
    @app_commands.describe(limit="Number of events to show (default: 10)")
    async def list_events(self, interaction: discord.Interaction, limit: int = 10):
        """List events with their assignments"""
        await interaction.response.defer()
        
        try:
            # Limit the number of events
            if limit > 50:
                limit = 50
            elif limit < 1:
                limit = 10
            
            events = await DatabaseHelper.get_events(self.db_manager, limit=limit)
            
            if not events:
                embed = EmbedBuilder.create_info_embed(
                    "Events",
                    "No events found in the database."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get assignment details for each event
            events_with_assignments = []
            for event in events:
                # Get MVP assignments
                mvp_query = """
                    SELECT p.name as player_name, ma.assigned_at
                    FROM mvp_assignments ma
                    JOIN players p ON ma.player_id = p.id
                    WHERE ma.event_id = ?
                    ORDER BY ma.assigned_at DESC
                """
                mvp_assignments = await self.db_manager.execute_query(mvp_query, (event['id'],))
                
                # Get winner assignment
                winner_query = """
                    SELECT a.name as alliance_name, wa.assigned_at
                    FROM winner_assignments wa
                    JOIN alliances a ON wa.alliance_id = a.id
                    WHERE wa.event_id = ?
                """
                winner_assignments = await self.db_manager.execute_query(winner_query, (event['id'],))
                
                event['mvp_assignments'] = mvp_assignments
                event['winner_assignment'] = winner_assignments[0] if winner_assignments else None
                events_with_assignments.append(event)
            
            # Format events list
            event_list = FormatHelper.format_event_list(events_with_assignments)
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                f"Events (showing {len(events_with_assignments)})",
                f"```{event_list}```"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to retrieve events list.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="addevent", description="Add a new event")
    @app_commands.describe(
        name="Event name",
        description="Event description (optional)",
        event_date="Event date (YYYY-MM-DD format, optional)"
    )
    @slash_admin_required()
    async def add_event(self, interaction: discord.Interaction, name: str, 
                       description: Optional[str] = None, event_date: Optional[str] = None):
        """Add a new event to the database"""
        await interaction.response.defer()
        
        try:
            # Validate name
            is_valid, error_msg = ValidationHelper.validate_name(name, max_length=200)
            if not is_valid:
                embed = EmbedBuilder.create_error_embed("Invalid Name", error_msg)
                await interaction.followup.send(embed=embed)
                return
            
            # Clean the name
            clean_name = TextHelper.clean_name(name)
            
            # Parse event date
            parsed_date = datetime.utcnow()
            if event_date:
                try:
                    parsed_date = datetime.fromisoformat(event_date)
                except ValueError:
                    embed = EmbedBuilder.create_error_embed("Invalid Date", "Date must be in YYYY-MM-DD format.")
                    await interaction.followup.send(embed=embed)
                    return
            
            # Add event to database
            query = """
                INSERT INTO events (name, description, event_date, has_mvp, has_winner, created_at)
                VALUES (?, ?, ?, 0, 0, datetime('now'))
            """
            await self.db_manager.execute_update(query, (clean_name, description, parsed_date))
            
            embed = EmbedBuilder.create_success_embed(
                "Event Added",
                f"Successfully added event: **{clean_name}**"
            )
            
            if description:
                embed.add_field(name="Description", value=description, inline=False)
            
            if event_date:
                embed.add_field(name="Date", value=event_date, inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error adding event: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to add event.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="editevent", description="Edit an event")
    @app_commands.describe(
        event_id="Event ID",
        name="New event name",
        description="New event description (optional)",
        event_date="New event date (YYYY-MM-DD format, optional)"
    )
    @slash_admin_required()
    async def edit_event(self, interaction: discord.Interaction, event_id: int, name: str,
                        description: Optional[str] = None, event_date: Optional[str] = None):
        """Edit an event"""
        await interaction.response.defer()
        
        try:
            # Validate name
            is_valid, error_msg = ValidationHelper.validate_name(name, max_length=200)
            if not is_valid:
                embed = EmbedBuilder.create_error_embed("Invalid Name", error_msg)
                await interaction.followup.send(embed=embed)
                return
            
            # Clean the name
            clean_name = TextHelper.clean_name(name)
            
            # Check if event exists
            events = await DatabaseHelper.get_events(self.db_manager)
            event = next((e for e in events if e['id'] == event_id), None)
            
            if not event:
                embed = EmbedBuilder.create_error_embed("Event Not Found", f"Event with ID {event_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Parse event date if provided
            parsed_date = event['event_date']
            if event_date:
                try:
                    parsed_date = datetime.fromisoformat(event_date)
                except ValueError:
                    embed = EmbedBuilder.create_error_embed("Invalid Date", "Date must be in YYYY-MM-DD format.")
                    await interaction.followup.send(embed=embed)
                    return
            
            # Update event
            query = """
                UPDATE events 
                SET name = ?, description = ?, event_date = ?
                WHERE id = ?
            """
            await self.db_manager.execute_update(query, (clean_name, description, parsed_date, event_id))
            
            embed = EmbedBuilder.create_success_embed(
                "Event Updated",
                f"Successfully updated event: **{clean_name}**"
            )
            
            if description:
                embed.add_field(name="Description", value=description, inline=False)
            
            if event_date:
                embed.add_field(name="Date", value=event_date, inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error editing event: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to edit event.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="deleteevent", description="Delete an event")
    @app_commands.describe(event_id="Event ID")
    @slash_admin_required()
    async def delete_event(self, interaction: discord.Interaction, event_id: int):
        """Delete an event from the database"""
        await interaction.response.defer()
        
        try:
            # Check if event exists
            events = await DatabaseHelper.get_events(self.db_manager)
            event = next((e for e in events if e['id'] == event_id), None)
            
            if not event:
                embed = EmbedBuilder.create_error_embed("Event Not Found", f"Event with ID {event_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            event_name = event['name']
            
            # Get assignments before deletion to update counts
            mvp_query = "SELECT player_id FROM mvp_assignments WHERE event_id = ?"
            mvp_assignments = await self.db_manager.execute_query(mvp_query, (event_id,))
            
            winner_query = "SELECT alliance_id FROM winner_assignments WHERE event_id = ?"
            winner_assignments = await self.db_manager.execute_query(winner_query, (event_id,))
            
            # Update player MVP counts
            for assignment in mvp_assignments:
                await self.db_manager.execute_update(
                    "UPDATE players SET mvp_count = mvp_count - 1, is_current_mvp = 0 WHERE id = ?",
                    (assignment['player_id'],)
                )
            
            # Update alliance win counts
            for assignment in winner_assignments:
                await self.db_manager.execute_update(
                    "UPDATE alliances SET win_count = win_count - 1, is_current_winner = 0 WHERE id = ?",
                    (assignment['alliance_id'],)
                )
            
            # Delete event (cascading will handle assignments)
            query = "DELETE FROM events WHERE id = ?"
            await self.db_manager.execute_update(query, (event_id,))
            
            embed = EmbedBuilder.create_success_embed(
                "Event Deleted",
                f"Successfully deleted event: **{event_name}**"
            )
            
            if mvp_assignments:
                embed.add_field(name="MVP Assignments Removed", value=str(len(mvp_assignments)), inline=True)
            
            if winner_assignments:
                embed.add_field(name="Winner Assignments Removed", value=str(len(winner_assignments)), inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to delete event.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="eventinfo", description="Get detailed information about an event")
    @app_commands.describe(event_id="Event ID")
    async def event_info(self, interaction: discord.Interaction, event_id: int):
        """Get detailed information about a specific event"""
        await interaction.response.defer()
        
        try:
            # Get event info
            events = await DatabaseHelper.get_events(self.db_manager)
            event = next((e for e in events if e['id'] == event_id), None)
            
            if not event:
                embed = EmbedBuilder.create_error_embed("Event Not Found", f"Event with ID {event_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            # Get MVP assignments
            mvp_query = """
                SELECT p.name as player_name, ma.assigned_at
                FROM mvp_assignments ma
                JOIN players p ON ma.player_id = p.id
                WHERE ma.event_id = ?
                ORDER BY ma.assigned_at DESC
            """
            mvp_assignments = await self.db_manager.execute_query(mvp_query, (event_id,))
            
            # Get winner assignment
            winner_query = """
                SELECT a.name as alliance_name, wa.assigned_at
                FROM winner_assignments wa
                JOIN alliances a ON wa.alliance_id = a.id
                WHERE wa.event_id = ?
            """
            winner_assignments = await self.db_manager.execute_query(winner_query, (event_id,))
            
            # Create event embed
            embed = EmbedBuilder.create_event_embed(event)
            
            # Add MVP assignments
            if mvp_assignments:
                mvp_text = ""
                for assignment in mvp_assignments:
                    player_name = assignment['player_name']
                    date = TextHelper.format_datetime(assignment['assigned_at'], "short")
                    mvp_text += f"• {player_name} ({date})\n"
                
                embed.add_field(
                    name="MVP Assignments",
                    value=mvp_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="MVP Assignments",
                    value="None",
                    inline=False
                )
            
            # Add winner assignment
            if winner_assignments:
                winner = winner_assignments[0]
                winner_name = winner['alliance_name']
                date = TextHelper.format_datetime(winner['assigned_at'], "short")
                
                embed.add_field(
                    name="Winning Alliance",
                    value=f"🏰 {winner_name} ({date})",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Winning Alliance",
                    value="None",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting event info: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to get event information.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="availableevents", description="Get events available for assignments")
    @app_commands.describe(assignment_type="Type of assignment (mvp, winner, or both)")
    async def available_events(self, interaction: discord.Interaction, 
                              assignment_type: str = "both"):
        """Get events available for MVP or winner assignments"""
        await interaction.response.defer()
        
        try:
            if assignment_type.lower() == "mvp":
                query = "SELECT * FROM events WHERE has_mvp = 0 ORDER BY event_date DESC"
                title = "Events Available for MVP Assignment"
            elif assignment_type.lower() == "winner":
                query = "SELECT * FROM events WHERE has_winner = 0 ORDER BY event_date DESC"
                title = "Events Available for Winner Assignment"
            else:
                query = "SELECT * FROM events ORDER BY event_date DESC"
                title = "All Events"
            
            events = await self.db_manager.execute_query(query)
            
            if not events:
                embed = EmbedBuilder.create_info_embed(
                    title,
                    "No events found matching the criteria."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format events list
            event_list = FormatHelper.format_event_list(events)
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                f"{title} ({len(events)})",
                f"```{event_list}```"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting available events: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to retrieve available events.")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(EventsCog(bot))