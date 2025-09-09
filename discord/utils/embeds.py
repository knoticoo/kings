"""
Utility functions for creating Discord embeds
"""

import discord
from typing import List, Dict, Any, Optional
from datetime import datetime

class EmbedBuilder:
    """Helper class for building Discord embeds"""
    
    @staticmethod
    def create_success_embed(title: str, description: str = "", fields: List[Dict] = None) -> discord.Embed:
        """Create a success embed with green color"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', ''),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
        
        return embed
    
    @staticmethod
    def create_error_embed(title: str, description: str = "", fields: List[Dict] = None) -> discord.Embed:
        """Create an error embed with red color"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', ''),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
        
        return embed
    
    @staticmethod
    def create_info_embed(title: str, description: str = "", fields: List[Dict] = None) -> discord.Embed:
        """Create an info embed with blue color"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', ''),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
        
        return embed
    
    @staticmethod
    def create_warning_embed(title: str, description: str = "", fields: List[Dict] = None) -> discord.Embed:
        """Create a warning embed with yellow color"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=0xffaa00,
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', ''),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
        
        return embed
    
    @staticmethod
    def create_player_embed(player: Dict[str, Any]) -> discord.Embed:
        """Create an embed for player information"""
        embed = discord.Embed(
            title=f"👤 Player: {player['name']}",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="MVP Status",
            value="🏆 Current MVP" if player.get('is_current_mvp') else "Not MVP",
            inline=True
        )
        
        embed.add_field(
            name="MVP Count",
            value=str(player.get('mvp_count', 0)),
            inline=True
        )
        
        embed.add_field(
            name="Excluded",
            value="Yes" if player.get('is_excluded') else "No",
            inline=True
        )
        
        if player.get('created_at'):
            embed.add_field(
                name="Created",
                value=player['created_at'][:10],  # Just the date part
                inline=True
            )
        
        return embed
    
    @staticmethod
    def create_alliance_embed(alliance: Dict[str, Any]) -> discord.Embed:
        """Create an embed for alliance information"""
        embed = discord.Embed(
            title=f"🏰 Alliance: {alliance['name']}",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Winner Status",
            value="🏆 Current Winner" if alliance.get('is_current_winner') else "Not Winner",
            inline=True
        )
        
        embed.add_field(
            name="Win Count",
            value=str(alliance.get('win_count', 0)),
            inline=True
        )
        
        if alliance.get('created_at'):
            embed.add_field(
                name="Created",
                value=alliance['created_at'][:10],
                inline=True
            )
        
        return embed
    
    @staticmethod
    def create_event_embed(event: Dict[str, Any]) -> discord.Embed:
        """Create an embed for event information"""
        embed = discord.Embed(
            title=f"🎯 Event: {event['name']}",
            description=event.get('description', ''),
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Date",
            value=event.get('event_date', 'Unknown')[:10] if event.get('event_date') else 'Unknown',
            inline=True
        )
        
        embed.add_field(
            name="Has MVP",
            value="Yes" if event.get('has_mvp') else "No",
            inline=True
        )
        
        embed.add_field(
            name="Has Winner",
            value="Yes" if event.get('has_winner') else "No",
            inline=True
        )
        
        return embed
    
    @staticmethod
    def create_guide_embed(guide: Dict[str, Any]) -> discord.Embed:
        """Create an embed for guide information"""
        embed = discord.Embed(
            title=f"📖 {guide['title']}",
            description=guide.get('excerpt', '')[:200] + "..." if len(guide.get('excerpt', '')) > 200 else guide.get('excerpt', ''),
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        if guide.get('category_name'):
            embed.add_field(
                name="Category",
                value=guide['category_name'],
                inline=True
            )
        
        embed.add_field(
            name="Views",
            value=str(guide.get('view_count', 0)),
            inline=True
        )
        
        embed.add_field(
            name="Featured",
            value="Yes" if guide.get('is_featured') else "No",
            inline=True
        )
        
        if guide.get('created_at'):
            embed.add_field(
                name="Created",
                value=guide['created_at'][:10],
                inline=True
            )
        
        return embed
    
    @staticmethod
    def create_blacklist_embed(entry: Dict[str, Any]) -> discord.Embed:
        """Create an embed for blacklist entry"""
        display_name = entry.get('display_name', 'Unknown')
        
        embed = discord.Embed(
            title=f"🚫 Blacklist Entry",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Entry",
            value=display_name,
            inline=False
        )
        
        if entry.get('alliance_name'):
            embed.add_field(
                name="Alliance",
                value=entry['alliance_name'],
                inline=True
            )
        
        if entry.get('player_name'):
            embed.add_field(
                name="Player",
                value=entry['player_name'],
                inline=True
            )
        
        if entry.get('created_at'):
            embed.add_field(
                name="Added",
                value=entry['created_at'][:10],
                inline=True
            )
        
        return embed
    
    @staticmethod
    def create_rotation_status_embed(status: Dict[str, Any]) -> discord.Embed:
        """Create an embed for rotation status"""
        embed = discord.Embed(
            title="🔄 Rotation Status",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        # MVP Status
        mvp_status = status.get('mvp', {})
        mvp_can_assign = mvp_status.get('can_assign', False)
        mvp_stats = mvp_status.get('stats', {})
        
        embed.add_field(
            name="MVP Rotation",
            value=f"{'✅ Can assign' if mvp_can_assign else '❌ Cannot assign'}\n"
                  f"Players with MVP: {mvp_stats.get('players_with_mvp', 0)}/{mvp_stats.get('total_players', 0)}",
            inline=True
        )
        
        # Winner Status
        winner_status = status.get('winner', {})
        winner_can_assign = winner_status.get('can_assign', False)
        winner_stats = winner_status.get('stats', {})
        
        embed.add_field(
            name="Winner Rotation",
            value=f"{'✅ Can assign' if winner_can_assign else '❌ Cannot assign'}\n"
                  f"Alliances with wins: {winner_stats.get('alliances_with_wins', 0)}/{winner_stats.get('total_alliances', 0)}",
            inline=True
        )
        
        return embed
    
    @staticmethod
    def create_stats_embed(stats: Dict[str, int]) -> discord.Embed:
        """Create an embed for statistics"""
        embed = discord.Embed(
            title="📊 King's Choice Statistics",
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Players",
            value=str(stats.get('total_players', 0)),
            inline=True
        )
        
        embed.add_field(
            name="Alliances",
            value=str(stats.get('total_alliances', 0)),
            inline=True
        )
        
        embed.add_field(
            name="Events",
            value=str(stats.get('total_events', 0)),
            inline=True
        )
        
        embed.add_field(
            name="Guides",
            value=str(stats.get('total_guides', 0)),
            inline=True
        )
        
        embed.add_field(
            name="Blacklist Entries",
            value=str(stats.get('total_blacklist', 0)),
            inline=True
        )
        
        return embed