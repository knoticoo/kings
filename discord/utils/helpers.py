"""
Helper utility functions
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class TextHelper:
    """Text processing and formatting utilities"""
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def clean_name(name: str) -> str:
        """Clean and normalize names"""
        if not name:
            return ""
        
        # Remove extra whitespace
        name = " ".join(name.split())
        
        # Remove special characters that might cause issues
        name = re.sub(r'[<>@#!&]', '', name)
        
        return name.strip()
    
    @staticmethod
    def format_datetime(dt_string: str, format_type: str = "short") -> str:
        """Format datetime string for display"""
        if not dt_string:
            return "Unknown"
        
        try:
            # Parse the datetime string
            if 'T' in dt_string:
                dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(dt_string)
            
            if format_type == "short":
                return dt.strftime("%Y-%m-%d")
            elif format_type == "long":
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            elif format_type == "time":
                return dt.strftime("%H:%M:%S")
            else:
                return dt.strftime("%Y-%m-%d")
                
        except Exception as e:
            logger.error(f"Failed to format datetime {dt_string}: {e}")
            return "Invalid Date"
    
    @staticmethod
    def create_pagination_embed(title: str, items: List[Dict[str, Any]], 
                              page: int = 1, per_page: int = 10, 
                              item_formatter: callable = None) -> Dict[str, Any]:
        """Create pagination data for embeds"""
        total_items = len(items)
        total_pages = (total_items + per_page - 1) // per_page
        
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_items = items[start_idx:end_idx]
        
        # Format items if formatter provided
        if item_formatter:
            formatted_items = [item_formatter(item) for item in page_items]
        else:
            formatted_items = [str(item) for item in page_items]
        
        return {
            'title': title,
            'items': formatted_items,
            'page': page,
            'total_pages': total_pages,
            'total_items': total_items,
            'has_previous': page > 1,
            'has_next': page < total_pages
        }

class ValidationHelper:
    """Input validation utilities"""
    
    @staticmethod
    def validate_name(name: str, min_length: int = 1, max_length: int = 100) -> tuple[bool, str]:
        """Validate a name field"""
        if not name or not name.strip():
            return False, "Name cannot be empty"
        
        name = name.strip()
        
        if len(name) < min_length:
            return False, f"Name must be at least {min_length} characters long"
        
        if len(name) > max_length:
            return False, f"Name must be no more than {max_length} characters long"
        
        # Check for invalid characters
        if re.search(r'[<>@#!&]', name):
            return False, "Name contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_id(id_value: Union[str, int]) -> tuple[bool, Optional[int]]:
        """Validate and convert ID to integer"""
        try:
            if isinstance(id_value, str):
                id_int = int(id_value)
            else:
                id_int = int(id_value)
            
            if id_int <= 0:
                return False, None
            
            return True, id_int
        except (ValueError, TypeError):
            return False, None
    
    @staticmethod
    def validate_language(lang: str, supported_languages: List[str]) -> tuple[bool, str]:
        """Validate language code"""
        if not lang:
            return False, "Language cannot be empty"
        
        if lang.lower() not in [l.lower() for l in supported_languages]:
            return False, f"Unsupported language. Supported: {', '.join(supported_languages)}"
        
        return True, lang.lower()

class PermissionHelper:
    """Permission checking utilities"""
    
    @staticmethod
    def has_admin_role(member, admin_role_name: str) -> bool:
        """Check if member has admin role"""
        if not member or not hasattr(member, 'roles'):
            return False
        
        return any(role.name.lower() == admin_role_name.lower() for role in member.roles)
    
    @staticmethod
    def has_moderator_role(member, moderator_role_name: str) -> bool:
        """Check if member has moderator role"""
        if not member or not hasattr(member, 'roles'):
            return False
        
        return any(role.name.lower() == moderator_role_name.lower() for role in member.roles)
    
    @staticmethod
    def has_required_permission(member, required_role: str = None, 
                               admin_role: str = "Admin", 
                               moderator_role: str = "Moderator") -> bool:
        """Check if member has required permission level"""
        if not member:
            return False
        
        # Check for specific role
        if required_role:
            return any(role.name.lower() == required_role.lower() for role in member.roles)
        
        # Check for admin or moderator
        return (PermissionHelper.has_admin_role(member, admin_role) or 
                PermissionHelper.has_moderator_role(member, moderator_role))

class SearchHelper:
    """Search and filtering utilities"""
    
    @staticmethod
    def search_items(items: List[Dict[str, Any]], search_term: str, 
                    search_fields: List[str]) -> List[Dict[str, Any]]:
        """Search items by term in specified fields"""
        if not search_term or not search_fields:
            return items
        
        search_term = search_term.lower()
        results = []
        
        for item in items:
            for field in search_fields:
                if field in item and item[field]:
                    field_value = str(item[field]).lower()
                    if search_term in field_value:
                        results.append(item)
                        break
        
        return results
    
    @staticmethod
    def filter_items(items: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter items by specified criteria"""
        if not filters:
            return items
        
        results = []
        
        for item in items:
            match = True
            for field, value in filters.items():
                if field not in item:
                    match = False
                    break
                
                item_value = item[field]
                if isinstance(value, str):
                    if str(item_value).lower() != value.lower():
                        match = False
                        break
                else:
                    if item_value != value:
                        match = False
                        break
            
            if match:
                results.append(item)
        
        return results

class FormatHelper:
    """Data formatting utilities"""
    
    @staticmethod
    def format_player_list(players: List[Dict[str, Any]], show_mvp: bool = True) -> str:
        """Format list of players for display"""
        if not players:
            return "No players found"
        
        lines = []
        for i, player in enumerate(players, 1):
            name = player.get('name', 'Unknown')
            mvp_count = player.get('mvp_count', 0)
            is_current = player.get('is_current_mvp', False)
            is_excluded = player.get('is_excluded', False)
            
            status = ""
            if is_current:
                status = " 🏆"
            elif is_excluded:
                status = " 🚫"
            
            if show_mvp:
                lines.append(f"{i}. {name} (MVP: {mvp_count}){status}")
            else:
                lines.append(f"{i}. {name}{status}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_alliance_list(alliances: List[Dict[str, Any]]) -> str:
        """Format list of alliances for display"""
        if not alliances:
            return "No alliances found"
        
        lines = []
        for i, alliance in enumerate(alliances, 1):
            name = alliance.get('name', 'Unknown')
            win_count = alliance.get('win_count', 0)
            is_current = alliance.get('is_current_winner', False)
            
            status = " 🏆" if is_current else ""
            lines.append(f"{i}. {name} (Wins: {win_count}){status}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_event_list(events: List[Dict[str, Any]]) -> str:
        """Format list of events for display"""
        if not events:
            return "No events found"
        
        lines = []
        for i, event in enumerate(events, 1):
            name = event.get('name', 'Unknown')
            date = event.get('event_date', 'Unknown')
            has_mvp = event.get('has_mvp', False)
            has_winner = event.get('has_winner', False)
            
            # Format date
            if date and date != 'Unknown':
                date = TextHelper.format_datetime(date, "short")
            
            status_icons = ""
            if has_mvp:
                status_icons += " 🏆"
            if has_winner:
                status_icons += " 🏰"
            
            lines.append(f"{i}. {name} ({date}){status_icons}")
        
        return "\n".join(lines)