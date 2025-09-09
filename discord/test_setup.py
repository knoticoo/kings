#!/usr/bin/env python3
"""
Test script to verify Discord bot setup
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the discord directory to Python path
discord_dir = Path(__file__).parent
sys.path.insert(0, str(discord_dir))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import discord
        print(f"✅ discord.py version: {discord.__version__}")
    except ImportError as e:
        print(f"❌ discord.py import failed: {e}")
        return False
    
    try:
        import aiosqlite
        print("✅ aiosqlite imported successfully")
    except ImportError as e:
        print(f"❌ aiosqlite import failed: {e}")
        return False
    
    try:
        from deep_translator import GoogleTranslator
        print("✅ deep-translator imported successfully")
    except ImportError as e:
        print(f"❌ deep-translator import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config.settings import settings
        print("✅ Configuration loaded successfully")
        
        # Check if .env file exists
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            print("✅ .env file found")
        else:
            print("⚠️  .env file not found (using defaults)")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from core.database import DatabaseManager
        
        # Check if database file exists
        db_path = "../kings_choice.db"
        if not os.path.exists(db_path):
            db_path = "kings_choice.db"
        
        if not os.path.exists(db_path):
            print(f"❌ Database file not found at {db_path}")
            return False
        
        print(f"✅ Database file found at {db_path}")
        
        # Test database connection
        async def test_db():
            db_manager = DatabaseManager(db_path)
            try:
                await db_manager.validate_database()
                print("✅ Database connection successful")
                return True
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
        
        return asyncio.run(test_db())
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_bot_import():
    """Test if bot can be imported"""
    print("\nTesting bot import...")
    
    try:
        from bot import bot
        print("✅ Bot imported successfully")
        
        # Check bot configuration
        if hasattr(bot, 'settings'):
            print("✅ Bot settings loaded")
        else:
            print("⚠️  Bot settings not found")
        
        return True
    except Exception as e:
        print(f"❌ Bot import failed: {e}")
        return False

def test_cogs():
    """Test if all cogs can be imported"""
    print("\nTesting cogs...")
    
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
    
    all_imported = True
    for cog in cogs:
        try:
            __import__(cog)
            print(f"✅ {cog} imported successfully")
        except Exception as e:
            print(f"❌ {cog} import failed: {e}")
            all_imported = False
    
    return all_imported

def main():
    """Run all tests"""
    print("King's Choice Discord Bot Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_bot_import,
        test_cogs
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot setup is ready.")
        print("\nNext steps:")
        print("1. Configure your Discord bot token in .env file")
        print("2. Run './start.sh start' to start the bot")
    else:
        print("❌ Some tests failed. Please fix the issues before running the bot.")
        print("\nCommon fixes:")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Create .env file: cp .env.example .env")
        print("- Ensure database file exists and is accessible")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)