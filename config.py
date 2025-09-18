"""
Configuration module for King's Choice Management App

Universal configuration system that works across different deployment environments.
Automatically detects paths and provides flexible configuration options.
"""

import os
from pathlib import Path

class Config:
    """Universal configuration class that adapts to any deployment environment"""
    
    # Get application directory (where this config.py file is located)
    APP_DIR = Path(__file__).parent.absolute()
    
    # Universal data directory - can be overridden by environment variables
    @classmethod
    def get_data_directory(cls):
        """Get the data directory where databases should be stored"""
        # Priority 1: Explicit environment variable
        if os.environ.get('KINGS_CHOICE_DATA_DIR'):
            return Path(os.environ.get('KINGS_CHOICE_DATA_DIR'))
        
        # Priority 2: XDG data directory (Linux standard)
        if os.environ.get('XDG_DATA_HOME'):
            return Path(os.environ.get('XDG_DATA_HOME')) / 'kings_choice'
        
        # Priority 3: User home directory data
        home = Path.home()
        if home != Path('/'):  # Not running as root or in container
            return home / '.local' / 'share' / 'kings_choice'
        
        # Priority 4: Application directory (fallback)
        return cls.APP_DIR / 'data'
    
    # Base directory for user databases
    @classmethod
    def get_user_database_directory(cls):
        """Get the directory where user databases are stored"""
        if os.environ.get('KINGS_CHOICE_USER_DB_DIR'):
            return Path(os.environ.get('KINGS_CHOICE_USER_DB_DIR'))
        return cls.get_data_directory() / 'user_databases'
    
    # Main application database path
    @classmethod
    def get_main_database_path(cls):
        """Get the path to the main application database"""
        if os.environ.get('KINGS_CHOICE_MAIN_DB_PATH'):
            return Path(os.environ.get('KINGS_CHOICE_MAIN_DB_PATH'))
        return cls.get_data_directory() / 'kings_choice.db'
    
    # Legacy properties for backward compatibility
    @property
    def USER_DATABASE_BASE_PATH(self):
        return str(self.get_user_database_directory())
    
    @property
    def MAIN_DATABASE_PATH(self):
        return str(self.get_main_database_path())
    
    @classmethod
    def get_user_database_path(cls, user_id, username):
        """
        Get the correct database path for a user
        
        Args:
            user_id: User ID
            username: Username
            
        Returns:
            str: Full path to user's database file
        """
        user_db_dir = cls.get_user_database_directory()
        return str(user_db_dir / f'user_{user_id}_{username}.db')
    
    @classmethod
    def ensure_data_directories(cls):
        """Ensure all necessary directories exist"""
        data_dir = cls.get_data_directory()
        user_db_dir = cls.get_user_database_directory()
        
        # Create directories
        data_dir.mkdir(parents=True, exist_ok=True)
        user_db_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Data directory: {data_dir}")
        print(f"📁 User databases directory: {user_db_dir}")
        
        return data_dir, user_db_dir
    
    @classmethod
    def get_main_database_uri(cls):
        """Get the main database URI for SQLAlchemy"""
        return f'sqlite:///{cls.get_main_database_path()}'
    
    @classmethod
    def print_config(cls):
        """Print current configuration for debugging"""
        print("🔧 King's Choice Universal Configuration:")
        print(f"   APP_DIR: {cls.APP_DIR}")
        print(f"   DATA_DIR: {cls.get_data_directory()}")
        print(f"   MAIN_DB: {cls.get_main_database_path()}")
        print(f"   USER_DB_DIR: {cls.get_user_database_directory()}")
        print()
        print("🌍 Environment Variables:")
        env_vars = [
            'KINGS_CHOICE_DATA_DIR',
            'KINGS_CHOICE_MAIN_DB_PATH', 
            'KINGS_CHOICE_USER_DB_DIR',
            'XDG_DATA_HOME',
            'HOME'
        ]
        for var in env_vars:
            value = os.environ.get(var, 'Not set')
            print(f"   {var}: {value}")
    
    @classmethod
    def detect_deployment_type(cls):
        """Detect what type of deployment this is"""
        app_dir_str = str(cls.APP_DIR)
        
        if '/root/' in app_dir_str:
            return 'vps_root'
        elif '/home/' in app_dir_str:
            return 'vps_user'
        elif '/workspace' in app_dir_str:
            return 'container'
        elif '/opt/' in app_dir_str:
            return 'system_install'
        else:
            return 'development'
    
    # Create a singleton instance for backward compatibility
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Create default instance for backward compatibility
Config = Config.get_instance()