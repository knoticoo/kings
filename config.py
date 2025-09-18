"""
Configuration module for King's Choice Management App

Handles environment-specific configuration including database paths.
"""

import os

class Config:
    """Base configuration class"""
    
    # Get application directory (where this config.py file is located)
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Base directory for user databases - configurable via environment variable
    USER_DATABASE_BASE_PATH = os.environ.get(
        'KINGS_CHOICE_DB_PATH', 
        os.path.join(APP_DIR, 'user_databases')
    )
    
    # Alternative: Check for common deployment patterns
    if not os.environ.get('KINGS_CHOICE_DB_PATH'):
        # If we're in /root/kings or similar structure, use that
        if '/root/kings' in APP_DIR or APP_DIR.endswith('/kings'):
            USER_DATABASE_BASE_PATH = os.path.join(APP_DIR, 'user_databases')
        # If we detect we're in a workspace-like environment
        elif '/workspace' in APP_DIR:
            USER_DATABASE_BASE_PATH = os.path.join(APP_DIR, 'user_databases')
        # Default to app directory + user_databases
        else:
            USER_DATABASE_BASE_PATH = os.path.join(APP_DIR, 'user_databases')
    
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
    
    # Main application database path - also configurable
    MAIN_DATABASE_PATH = os.environ.get(
        'KINGS_CHOICE_MAIN_DB_PATH',
        os.path.join(APP_DIR, 'kings_choice.db')
    )
    
    @staticmethod
    def ensure_user_database_directory():
        """Ensure the user database directory exists"""
        os.makedirs(Config.USER_DATABASE_BASE_PATH, exist_ok=True)
        print(f"📁 User databases directory: {Config.USER_DATABASE_BASE_PATH}")
    
    @staticmethod
    def get_main_database_uri():
        """Get the main database URI for SQLAlchemy"""
        return f'sqlite:///{Config.MAIN_DATABASE_PATH}'
    
    @staticmethod
    def print_config():
        """Print current configuration for debugging"""
        print("🔧 King's Choice Configuration:")
        print(f"   APP_DIR: {Config.APP_DIR}")
        print(f"   MAIN_DATABASE_PATH: {Config.MAIN_DATABASE_PATH}")
        print(f"   USER_DATABASE_BASE_PATH: {Config.USER_DATABASE_BASE_PATH}")
        print(f"   Environment DB Path: {os.environ.get('KINGS_CHOICE_DB_PATH', 'Not set')}")
        print(f"   Environment Main DB: {os.environ.get('KINGS_CHOICE_MAIN_DB_PATH', 'Not set')}")