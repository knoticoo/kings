"""
Configuration module for King's Choice Management App

Handles environment-specific configuration including database paths.
"""

import os

class Config:
    """Base configuration class"""
    
    # Detect if we're running on VPS (you can set this environment variable)
    IS_VPS = os.environ.get('KINGS_CHOICE_VPS', 'false').lower() == 'true'
    
    # Base directory for user databases
    if IS_VPS:
        # VPS configuration
        USER_DATABASE_BASE_PATH = '/root/kings/user_databases'
    else:
        # Local development configuration
        USER_DATABASE_BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_databases')
    
    @staticmethod
    def get_user_database_path(user_id, username):
        """
        Get the correct database path for a user based on environment
        
        Args:
            user_id: User ID
            username: Username
            
        Returns:
            str: Full path to user's database file
        """
        return os.path.join(Config.USER_DATABASE_BASE_PATH, f'user_{user_id}_{username}.db')
    
    @staticmethod
    def ensure_user_database_directory():
        """Ensure the user database directory exists"""
        os.makedirs(Config.USER_DATABASE_BASE_PATH, exist_ok=True)