"""
Guide management commands for Discord bot
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any
import logging

from core.database import DatabaseHelper
from utils.embeds import EmbedBuilder
from utils.helpers import SearchHelper, TextHelper
from bot import bot, slash_admin_required, slash_moderator_required

logger = logging.getLogger(__name__)

class GuidesCog(commands.Cog):
    """Guide management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = bot.db_manager
    
    @app_commands.command(name="guides", description="List guides")
    @app_commands.describe(
        category="Category to filter by (optional)",
        search="Search term (optional)",
        limit="Number of guides to show (default: 10)"
    )
    async def list_guides(self, interaction: discord.Interaction, 
                         category: Optional[str] = None,
                         search: Optional[str] = None,
                         limit: int = 10):
        """List guides with optional filtering"""
        await interaction.response.defer()
        
        try:
            # Limit the number of guides
            if limit > 20:
                limit = 20
            elif limit < 1:
                limit = 10
            
            # Get category ID if category name provided
            category_id = None
            if category:
                categories_query = "SELECT id FROM guide_categories WHERE name LIKE ? AND is_active = 1"
                categories = await self.db_manager.execute_query(categories_query, (f"%{category}%",))
                if categories:
                    category_id = categories[0]['id']
                else:
                    embed = EmbedBuilder.create_error_embed("Category Not Found", f"Category '{category}' not found.")
                    await interaction.followup.send(embed=embed)
                    return
            
            # Get guides
            guides = await DatabaseHelper.get_guides(
                self.db_manager, 
                category_id=category_id,
                search_term=search,
                limit=limit
            )
            
            if not guides:
                embed = EmbedBuilder.create_info_embed(
                    "Guides",
                    "No guides found matching your criteria."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format guides list
            guides_text = ""
            for i, guide in enumerate(guides, 1):
                title = guide['title']
                category_name = guide.get('category_name', 'Uncategorized')
                view_count = guide.get('view_count', 0)
                featured = "⭐ " if guide.get('is_featured') else ""
                
                # Truncate title if too long
                if len(title) > 40:
                    title = title[:37] + "..."
                
                guides_text += f"{i}. {featured}**{title}**\n"
                guides_text += f"   Category: {category_name} | Views: {view_count}\n\n"
            
            # Create embed
            title = "Guides"
            if category:
                title += f" in {category}"
            if search:
                title += f" (search: {search})"
            title += f" ({len(guides)})"
            
            embed = EmbedBuilder.create_info_embed(
                title,
                guides_text
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing guides: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to retrieve guides.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="guide", description="View a specific guide")
    @app_commands.describe(guide_id="Guide ID")
    async def view_guide(self, interaction: discord.Interaction, guide_id: int):
        """View a specific guide by ID"""
        await interaction.response.defer()
        
        try:
            # Get guide details
            guide_query = """
                SELECT g.*, gc.name as category_name
                FROM guides g
                LEFT JOIN guide_categories gc ON g.category_id = gc.id
                WHERE g.id = ? AND g.is_published = 1
            """
            guides = await self.db_manager.execute_query(guide_query, (guide_id,))
            
            if not guides:
                embed = EmbedBuilder.create_error_embed("Guide Not Found", f"Guide with ID {guide_id} not found.")
                await interaction.followup.send(embed=embed)
                return
            
            guide = guides[0]
            
            # Increment view count
            await self.db_manager.execute_update(
                "UPDATE guides SET view_count = view_count + 1 WHERE id = ?",
                (guide_id,)
            )
            
            # Create guide embed
            embed = EmbedBuilder.create_guide_embed(guide)
            
            # Add content (truncated if too long)
            content = guide.get('content', '')
            if len(content) > 1000:
                content = content[:997] + "..."
            
            embed.add_field(
                name="Content",
                value=content or "No content available",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing guide: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to load guide.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="searchguides", description="Search guides by content")
    @app_commands.describe(
        query="Search query",
        limit="Number of results (default: 10)"
    )
    async def search_guides(self, interaction: discord.Interaction, query: str, limit: int = 10):
        """Search guides by title and content"""
        await interaction.response.defer()
        
        try:
            # Limit the number of results
            if limit > 20:
                limit = 20
            elif limit < 1:
                limit = 10
            
            # Search guides
            guides = await DatabaseHelper.get_guides(
                self.db_manager,
                search_term=query,
                limit=limit
            )
            
            if not guides:
                embed = EmbedBuilder.create_info_embed(
                    "Search Results",
                    f"No guides found matching '{query}'."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format search results
            results_text = ""
            for i, guide in enumerate(guides, 1):
                title = guide['title']
                category_name = guide.get('category_name', 'Uncategorized')
                excerpt = guide.get('excerpt', '')
                
                # Truncate title and excerpt
                if len(title) > 50:
                    title = title[:47] + "..."
                if len(excerpt) > 100:
                    excerpt = excerpt[:97] + "..."
                
                results_text += f"{i}. **{title}**\n"
                results_text += f"   Category: {category_name}\n"
                if excerpt:
                    results_text += f"   {excerpt}\n"
                results_text += "\n"
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                f"Search Results for '{query}' ({len(guides)})",
                results_text
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error searching guides: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to search guides.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="categories", description="List guide categories")
    async def list_categories(self, interaction: discord.Interaction):
        """List all guide categories"""
        await interaction.response.defer()
        
        try:
            # Get categories
            categories_query = """
                SELECT gc.*, COUNT(g.id) as guide_count
                FROM guide_categories gc
                LEFT JOIN guides g ON gc.id = g.category_id AND g.is_published = 1
                WHERE gc.is_active = 1
                GROUP BY gc.id
                ORDER BY gc.sort_order, gc.name
            """
            categories = await self.db_manager.execute_query(categories_query)
            
            if not categories:
                embed = EmbedBuilder.create_info_embed(
                    "Categories",
                    "No categories found."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format categories list
            categories_text = ""
            for category in categories:
                name = category['name']
                description = category.get('description', '')
                guide_count = category.get('guide_count', 0)
                icon = category.get('icon', '📁')
                
                categories_text += f"{icon} **{name}** ({guide_count} guides)\n"
                if description:
                    categories_text += f"   {description}\n"
                categories_text += "\n"
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                f"Guide Categories ({len(categories)})",
                categories_text
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing categories: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to retrieve categories.")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="featuredguides", description="Show featured guides")
    @app_commands.describe(limit="Number of guides to show (default: 5)")
    async def featured_guides(self, interaction: discord.Interaction, limit: int = 5):
        """Show featured guides"""
        await interaction.response.defer()
        
        try:
            # Limit the number of guides
            if limit > 10:
                limit = 10
            elif limit < 1:
                limit = 5
            
            # Get featured guides
            featured_query = """
                SELECT g.*, gc.name as category_name
                FROM guides g
                LEFT JOIN guide_categories gc ON g.category_id = gc.id
                WHERE g.is_published = 1 AND g.is_featured = 1
                ORDER BY g.created_at DESC
                LIMIT ?
            """
            guides = await self.db_manager.execute_query(featured_query, (limit,))
            
            if not guides:
                embed = EmbedBuilder.create_info_embed(
                    "Featured Guides",
                    "No featured guides found."
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format featured guides
            guides_text = ""
            for i, guide in enumerate(guides, 1):
                title = guide['title']
                category_name = guide.get('category_name', 'Uncategorized')
                view_count = guide.get('view_count', 0)
                excerpt = guide.get('excerpt', '')
                
                # Truncate title and excerpt
                if len(title) > 50:
                    title = title[:47] + "..."
                if len(excerpt) > 150:
                    excerpt = excerpt[:147] + "..."
                
                guides_text += f"⭐ **{title}**\n"
                guides_text += f"   Category: {category_name} | Views: {view_count}\n"
                if excerpt:
                    guides_text += f"   {excerpt}\n"
                guides_text += "\n"
            
            # Create embed
            embed = EmbedBuilder.create_info_embed(
                f"Featured Guides ({len(guides)})",
                guides_text
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing featured guides: {e}")
            embed = EmbedBuilder.create_error_embed("Error", "Failed to retrieve featured guides.")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(GuidesCog(bot))