"""
Configuration settings for the Discord bot
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class BotSettings:
    """Bot configuration settings"""
    
    # Discord Bot Settings
    discord_token: str
    command_prefix: str = "!kc"
    admin_role: str = "Admin"
    moderator_role: str = "Moderator"
    
    # Database Settings
    database_path: str = "kings_choice.db"
    
    # Language Settings
    default_language: str = "en"
    supported_languages: list = None
    
    # Bot Behavior
    auto_translate: bool = True
    log_level: str = "INFO"
    command_cooldown: int = 3
    
    # Feature Flags
    enable_rotation_logic: bool = True
    enable_auto_announcements: bool = True
    enable_guide_system: bool = True
    enable_blacklist: bool = True
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["en", "ru"]
    
    @classmethod
    def from_env(cls) -> 'BotSettings':
        """Create settings from environment variables"""
        return cls(
            discord_token=os.getenv('DISCORD_BOT_TOKEN', ''),
            command_prefix=os.getenv('BOT_PREFIX', '!kc'),
            admin_role=os.getenv('ADMIN_ROLE', 'Admin'),
            moderator_role=os.getenv('MODERATOR_ROLE', 'Moderator'),
            database_path=os.getenv('DATABASE_PATH', 'kings_choice.db'),
            default_language=os.getenv('DEFAULT_LANGUAGE', 'en'),
            auto_translate=os.getenv('AUTO_TRANSLATE', 'true').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            command_cooldown=int(os.getenv('COMMAND_COOLDOWN', '3')),
            enable_rotation_logic=os.getenv('ENABLE_ROTATION_LOGIC', 'true').lower() == 'true',
            enable_auto_announcements=os.getenv('ENABLE_AUTO_ANNOUNCEMENTS', 'true').lower() == 'true',
            enable_guide_system=os.getenv('ENABLE_GUIDE_SYSTEM', 'true').lower() == 'true',
            enable_blacklist=os.getenv('ENABLE_BLACKLIST', 'true').lower() == 'true'
        )
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        if not self.discord_token:
            raise ValueError("DISCORD_BOT_TOKEN is required")
        
        if not os.path.exists(self.database_path):
            raise ValueError(f"Database file not found: {self.database_path}")
        
        if self.default_language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {self.default_language}")
        
        return True

# Global settings instance
settings = BotSettings.from_env()