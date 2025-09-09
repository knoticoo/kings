"""
Administrative commands for Discord bot
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any
import logging
import asyncio

from core.database import DatabaseHelper, DatabaseManager
from utils.embeds import EmbedBuilder
from utils.helpers import ValidationHelper, TextHelper
from bot import bot, slash_admin_required

logger = logging.getLogger(__name__)

class AdminCog(commands.Cog):
    """Administrative commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = bot.db_manager
    
    @app_commands.command(name="admin", description="Show admin panel")
    @slash_admin_required()
    async def admin_panel(self, interaction: discord.Interaction):
        """Show admin panel with system information"""
        await interaction.response.defer()
        
        try:
            # Get system statistics
            stats = await DatabaseHelper.get_stats(self.db_manager)
            
            # Get bot information
            uptime = self.bot.get_uptime()
            guild_count = len(self.bot.guilds)
            user_count = len(self.bot.users)
            
            # Get database info
            db_size_query = "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
            db_size_result = await self.db_manager.execute_query(db_size_query)
            db_size = db_size_result[0]['size'] if db_size_result else 0
            db_size_mb = db_size / (1024 * 1024)
            
            # Create admin embed
            embed = discord.Embed(
                title="🔧 Admin Panel",
                color=0xff6b6b,
                timestamp=discord.utils.utcnow()
            )
            
            # Bot Information
            embed.add_field(
                name="Bot Information",
                value=f"Uptime: {uptime}\n"
                      f"Guilds: {guild_count}\n"
                      f"Users: {user_count}\n"
                      f"Commands: {len(self.bot.tree.get_commands())}",
                inline=True
            )
            
            # Database Information
            embed.add_field(
                name="Database",
                value=f"Size: {db_size_mb:.2f} MB\n"
                      f"Players: {stats['total_players']}\n"
                      f"Alliances: {stats['total_alliances']}\n"
                      f"Events: {stats['total_events']}",
                inline=True
            )
            
            # Content Information
            embed.add_field(
                name="Content",
                value=f"Guides: {stats['total_guides']}\n"
                      f"Blacklist: {stats['total_blacklist']}\n"
                      f"Settings: {len(self.bot.settings.__dict__)}",
                inline=True
            )
            
            # Feature Status
            features = []
            if self.bot.settings.enable_rotation_logic:
                features.append("✅ Rotation Logic")
            if self.bot.settings.enable_auto_announcements:
                features.append("✅ Auto Announcements")
            if self.bot.settings.enable_guide_system:
                features.append("✅ Guide System")
            if self.bot.settings.enable_blacklist:
                features.append("✅ Blacklist")
            
            embed.add_field(
                name="Features",
                value="\n".join(features) if features else "No features enabled",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing admin panel: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to load admin panel.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="backup", description="Create database backup")
    @slash_admin_required()
    async def backup_database(self, interaction: discord.Interaction):
        """Create a backup of the database"""
        await interaction.response.defer()
        
        try:
            import shutil
            import os
            from datetime import datetime
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"kings_choice_backup_{timestamp}.db"
            backup_path = os.path.join(os.getcwd(), backup_filename)
            
            # Copy database file
            shutil.copy2(self.bot.settings.database_path, backup_path)
            
            # Get file size
            file_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
            
            embed = EmbedBuilder.create_success_embed(
                "Database Backup Created",
                f"Backup saved as: **{backup_filename}**\n"
                f"Size: {file_size:.2f} MB"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to create database backup.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="validate", description="Validate database integrity")
    @slash_admin_required()
    async def validate_database(self, interaction: discord.Interaction):
        """Validate database integrity"""
        await interaction.response.defer()
        
        try:
            # Check database integrity
            integrity_query = "PRAGMA integrity_check"
            integrity_result = await self.db_manager.execute_query(integrity_query)
            
            # Check foreign key constraints
            fk_query = "PRAGMA foreign_key_check"
            fk_result = await self.db_manager.execute_query(fk_query)
            
            # Get table information
            tables_query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """
            tables = await self.db_manager.execute_query(tables_query)
            
            # Create validation embed
            embed = discord.Embed(
                title="🔍 Database Validation",
                color=0x4ecdc4,
                timestamp=discord.utils.utcnow()
            )
            
            # Integrity check
            integrity_ok = integrity_result and integrity_result[0].get('integrity_check') == 'ok'
            embed.add_field(
                name="Integrity Check",
                value="✅ Passed" if integrity_ok else "❌ Failed",
                inline=True
            )
            
            # Foreign key check
            fk_ok = not fk_result or len(fk_result) == 0
            embed.add_field(
                name="Foreign Keys",
                value="✅ Valid" if fk_ok else f"❌ {len(fk_result)} violations",
                inline=True
            )
            
            # Tables
            embed.add_field(
                name="Tables",
                value=f"✅ {len(tables)} tables found",
                inline=True
            )
            
            # Table list
            table_names = [table['name'] for table in tables]
            embed.add_field(
                name="Available Tables",
                value=", ".join(table_names),
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error validating database: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to validate database.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="cleanup", description="Clean up old data")
    @slash_admin_required()
    async def cleanup_data(self, interaction: discord.Interaction):
        """Clean up old or orphaned data"""
        await interaction.response.defer()
        
        try:
            cleanup_results = []
            
            # Clean up orphaned MVP assignments
            orphaned_mvp_query = """
                DELETE FROM mvp_assignments 
                WHERE player_id NOT IN (SELECT id FROM players) 
                OR event_id NOT IN (SELECT id FROM events)
            """
            orphaned_mvp = await self.db_manager.execute_update(orphaned_mvp_query)
            cleanup_results.append(f"Orphaned MVP assignments: {orphaned_mvp}")
            
            # Clean up orphaned winner assignments
            orphaned_winner_query = """
                DELETE FROM winner_assignments 
                WHERE alliance_id NOT IN (SELECT id FROM alliances) 
                OR event_id NOT IN (SELECT id FROM events)
            """
            orphaned_winner = await self.db_manager.execute_update(orphaned_winner_query)
            cleanup_results.append(f"Orphaned winner assignments: {orphaned_winner}")
            
            # Clean up orphaned guides
            orphaned_guides_query = """
                DELETE FROM guides 
                WHERE category_id NOT IN (SELECT id FROM guide_categories)
            """
            orphaned_guides = await self.db_manager.execute_update(orphaned_guides_query)
            cleanup_results.append(f"Orphaned guides: {orphaned_guides}")
            
            # Update player MVP counts
            update_mvp_counts_query = """
                UPDATE players SET mvp_count = (
                    SELECT COUNT(*) FROM mvp_assignments 
                    WHERE player_id = players.id
                )
            """
            await self.db_manager.execute_update(update_mvp_counts_query)
            cleanup_results.append("Updated player MVP counts")
            
            # Update alliance win counts
            update_win_counts_query = """
                UPDATE alliances SET win_count = (
                    SELECT COUNT(*) FROM winner_assignments 
                    WHERE alliance_id = alliances.id
                )
            """
            await self.db_manager.execute_update(update_win_counts_query)
            cleanup_results.append("Updated alliance win counts")
            
            # Create cleanup embed
            embed = EmbedBuilder.create_success_embed(
                "Database Cleanup Complete",
                "\n".join(cleanup_results)
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to clean up database.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="reload", description="Reload bot cogs")
    @slash_admin_required()
    async def reload_cogs(self, interaction: discord.Interaction):
        """Reload all bot cogs"""
        await interaction.response.defer()
        
        try:
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
            
            reloaded = []
            failed = []
            
            for cog in cogs:
                try:
                    await self.bot.reload_extension(cog)
                    reloaded.append(cog)
                except Exception as e:
                    failed.append(f"{cog}: {str(e)}")
            
            # Create reload embed
            embed = discord.Embed(
                title="🔄 Cog Reload",
                color=0x4ecdc4,
                timestamp=discord.utils.utcnow()
            )
            
            if reloaded:
                embed.add_field(
                    name="Successfully Reloaded",
                    value="\n".join(reloaded),
                    inline=False
                )
            
            if failed:
                embed.add_field(
                    name="Failed to Reload",
                    value="\n".join(failed),
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error reloading cogs: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to reload cogs.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="sync", description="Sync slash commands")
    @slash_admin_required()
    async def sync_commands(self, interaction: discord.Interaction):
        """Sync slash commands with Discord"""
        await interaction.response.defer()
        
        try:
            synced = await self.bot.tree.sync()
            
            embed = EmbedBuilder.create_success_embed(
                "Commands Synced",
                f"Successfully synced {len(synced)} slash commands with Discord."
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error syncing commands: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to sync commands.")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AdminCog(bot))