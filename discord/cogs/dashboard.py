"""
Dashboard commands for Discord bot
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any
import logging

from core.database import DatabaseHelper
from core.rotation import RotationLogic
from utils.embeds import EmbedBuilder
from utils.helpers import TextHelper
from bot import bot

logger = logging.getLogger(__name__)

class DashboardCog(commands.Cog):
    """Dashboard and overview commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = bot.db_manager
        self.rotation_logic = bot.rotation_logic
    
    @app_commands.command(name="dashboard", description="Show the main dashboard")
    async def dashboard(self, interaction: discord.Interaction):
        """Show the main dashboard with current status"""
        await interaction.response.defer()
        
        try:
            # Get current MVP and winner
            current_mvp = await DatabaseHelper.get_current_mvp(self.db_manager)
            current_winner = await DatabaseHelper.get_current_winner(self.db_manager)
            
            # Get recent events
            recent_events = await DatabaseHelper.get_events(self.db_manager, limit=5)
            
            # Get statistics
            stats = await DatabaseHelper.get_stats(self.db_manager)
            
            # Get rotation status
            rotation_status = await self.rotation_logic.get_rotation_status()
            
            # Create main dashboard embed
            embed = discord.Embed(
                title="🏆 King's Choice Dashboard",
                color=0x0099ff,
                timestamp=discord.utils.utcnow()
            )
            
            # Current MVP
            if current_mvp:
                embed.add_field(
                    name="Current MVP",
                    value=f"🏆 **{current_mvp['name']}**\nMVP Count: {current_mvp['mvp_count']}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="Current MVP",
                    value="None assigned",
                    inline=True
                )
            
            # Current Winner
            if current_winner:
                embed.add_field(
                    name="Current Winner",
                    value=f"🏰 **{current_winner['name']}**\nWin Count: {current_winner['win_count']}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="Current Winner",
                    value="None assigned",
                    inline=True
                )
            
            # Rotation Status
            mvp_can_assign = rotation_status['mvp']['can_assign']
            winner_can_assign = rotation_status['winner']['can_assign']
            
            embed.add_field(
                name="Rotation Status",
                value=f"MVP: {'✅' if mvp_can_assign else '❌'}\nWinner: {'✅' if winner_can_assign else '❌'}",
                inline=True
            )
            
            # Statistics
            embed.add_field(
                name="Statistics",
                value=f"Players: {stats['total_players']}\nAlliances: {stats['total_alliances']}\nEvents: {stats['total_events']}",
                inline=True
            )
            
            embed.add_field(
                name="Content",
                value=f"Guides: {stats['total_guides']}\nBlacklist: {stats['total_blacklist']}",
                inline=True
            )
            
            # Recent Events
            if recent_events:
                recent_text = ""
                for event in recent_events[:3]:  # Show last 3 events
                    date = TextHelper.format_datetime(event['event_date'], "short")
                    status_icons = ""
                    if event.get('has_mvp'):
                        status_icons += " 🏆"
                    if event.get('has_winner'):
                        status_icons += " 🏰"
                    
                    recent_text += f"• {event['name']} ({date}){status_icons}\n"
                
                embed.add_field(
                    name="Recent Events",
                    value=recent_text,
                    inline=False
                )
            
            # Bot uptime
            uptime = self.bot.get_uptime()
            embed.set_footer(text=f"Bot Uptime: {uptime}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing dashboard: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to load dashboard.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="stats", description="Show detailed statistics")
    async def stats(self, interaction: discord.Interaction):
        """Show detailed statistics"""
        await interaction.response.defer()
        
        try:
            # Get basic statistics
            stats = await DatabaseHelper.get_stats(self.db_manager)
            
            # Get rotation status
            rotation_status = await self.rotation_logic.get_rotation_status()
            
            # Get top players by MVP count
            top_players_query = """
                SELECT name, mvp_count, is_current_mvp
                FROM players 
                WHERE is_excluded = 0
                ORDER BY mvp_count DESC, name ASC
                LIMIT 5
            """
            top_players = await self.db_manager.execute_query(top_players_query)
            
            # Get top alliances by win count
            top_alliances_query = """
                SELECT name, win_count, is_current_winner
                FROM alliances
                ORDER BY win_count DESC, name ASC
                LIMIT 5
            """
            top_alliances = await self.db_manager.execute_query(top_alliances_query)
            
            # Get recent activity
            recent_assignments_query = """
                SELECT 'MVP' as type, p.name as name, e.name as event_name, ma.assigned_at
                FROM mvp_assignments ma
                JOIN players p ON ma.player_id = p.id
                JOIN events e ON ma.event_id = e.id
                UNION ALL
                SELECT 'Winner' as type, a.name as name, e.name as event_name, wa.assigned_at
                FROM winner_assignments wa
                JOIN alliances a ON wa.alliance_id = a.id
                JOIN events e ON wa.event_id = e.id
                ORDER BY assigned_at DESC
                LIMIT 10
            """
            recent_activity = await self.db_manager.execute_query(recent_assignments_query)
            
            # Create stats embed
            embed = EmbedBuilder.create_stats_embed(stats)
            
            # Add top players
            if top_players:
                players_text = ""
                for i, player in enumerate(top_players, 1):
                    name = player['name']
                    mvp_count = player['mvp_count']
                    is_current = " 🏆" if player['is_current_mvp'] else ""
                    players_text += f"{i}. {name}: {mvp_count} MVPs{is_current}\n"
                
                embed.add_field(
                    name="Top Players (MVP Count)",
                    value=players_text,
                    inline=True
                )
            
            # Add top alliances
            if top_alliances:
                alliances_text = ""
                for i, alliance in enumerate(top_alliances, 1):
                    name = alliance['name']
                    win_count = alliance['win_count']
                    is_current = " 🏰" if alliance['is_current_winner'] else ""
                    alliances_text += f"{i}. {name}: {win_count} wins{is_current}\n"
                
                embed.add_field(
                    name="Top Alliances (Win Count)",
                    value=alliances_text,
                    inline=True
                )
            
            # Add rotation details
            mvp_stats = rotation_status['mvp']['stats']
            winner_stats = rotation_status['winner']['stats']
            
            if mvp_stats and winner_stats:
                rotation_text = f"**MVP Rotation:**\n"
                rotation_text += f"Players with MVP: {mvp_stats.get('players_with_mvp', 0)}/{mvp_stats.get('total_players', 0)}\n"
                rotation_text += f"Avg MVP count: {mvp_stats.get('avg_mvp_count', 0):.1f}\n\n"
                rotation_text += f"**Winner Rotation:**\n"
                rotation_text += f"Alliances with wins: {winner_stats.get('alliances_with_wins', 0)}/{winner_stats.get('total_alliances', 0)}\n"
                rotation_text += f"Avg win count: {winner_stats.get('avg_win_count', 0):.1f}"
                
                embed.add_field(
                    name="Rotation Details",
                    value=rotation_text,
                    inline=False
                )
            
            # Add recent activity
            if recent_activity:
                activity_text = ""
                for activity in recent_activity[:5]:  # Show last 5 activities
                    activity_type = activity['type']
                    name = activity['name']
                    event_name = activity['event_name']
                    date = TextHelper.format_datetime(activity['assigned_at'], "short")
                    icon = "🏆" if activity_type == "MVP" else "🏰"
                    activity_text += f"{icon} {name} → {event_name} ({date})\n"
                
                embed.add_field(
                    name="Recent Activity",
                    value=activity_text,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing stats: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to load statistics.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="rotation", description="Show rotation status details")
    async def rotation_status(self, interaction: discord.Interaction):
        """Show detailed rotation status"""
        await interaction.response.defer()
        
        try:
            # Get rotation status
            status = await self.rotation_logic.get_rotation_status()
            
            # Create rotation status embed
            embed = EmbedBuilder.create_rotation_status_embed(status)
            
            # Add detailed statistics
            mvp_stats = status['mvp']['stats']
            winner_stats = status['winner']['stats']
            
            if mvp_stats:
                embed.add_field(
                    name="MVP Statistics",
                    value=f"Total Players: {mvp_stats.get('total_players', 0)}\n"
                          f"Players with MVP: {mvp_stats.get('players_with_mvp', 0)}\n"
                          f"Average MVP Count: {mvp_stats.get('avg_mvp_count', 0):.1f}\n"
                          f"Max MVP Count: {mvp_stats.get('max_mvp_count', 0)}\n"
                          f"Min MVP Count: {mvp_stats.get('min_mvp_count', 0)}",
                    inline=True
                )
            
            if winner_stats:
                embed.add_field(
                    name="Winner Statistics",
                    value=f"Total Alliances: {winner_stats.get('total_alliances', 0)}\n"
                          f"Alliances with Wins: {winner_stats.get('alliances_with_wins', 0)}\n"
                          f"Average Win Count: {winner_stats.get('avg_win_count', 0):.1f}\n"
                          f"Max Win Count: {winner_stats.get('max_win_count', 0)}\n"
                          f"Min Win Count: {winner_stats.get('min_win_count', 0)}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing rotation status: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to load rotation status.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="current", description="Show current MVP and winner")
    async def current_status(self, interaction: discord.Interaction):
        """Show current MVP and winner status"""
        await interaction.response.defer()
        
        try:
            # Get current MVP and winner
            current_mvp = await DatabaseHelper.get_current_mvp(self.db_manager)
            current_winner = await DatabaseHelper.get_current_winner(self.db_manager)
            
            # Create embed
            embed = discord.Embed(
                title="🏆 Current Status",
                color=0x0099ff,
                timestamp=discord.utils.utcnow()
            )
            
            # Current MVP
            if current_mvp:
                embed.add_field(
                    name="Current MVP",
                    value=f"🏆 **{current_mvp['name']}**\n"
                          f"Total MVPs: {current_mvp['mvp_count']}\n"
                          f"Excluded: {'Yes' if current_mvp['is_excluded'] else 'No'}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="Current MVP",
                    value="No MVP currently assigned",
                    inline=True
                )
            
            # Current Winner
            if current_winner:
                embed.add_field(
                    name="Current Winner",
                    value=f"🏰 **{current_winner['name']}**\n"
                          f"Total Wins: {current_winner['win_count']}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="Current Winner",
                    value="No winner currently assigned",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing current status: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to load current status.")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(DashboardCog(bot))