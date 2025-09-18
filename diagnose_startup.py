#!/usr/bin/env python3
"""
Diagnostic script to identify startup issues on VPS
"""

import sys
import os
import traceback

print("🔍 King's Choice App - Startup Diagnostics")
print("=" * 50)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports step by step"""
    print("\n📦 Testing imports...")
    
    try:
        print("  - Testing Flask...")
        from flask import Flask
        print("  ✅ Flask imported successfully")
    except Exception as e:
        print(f"  ❌ Flask import failed: {e}")
        return False
    
    try:
        print("  - Testing database...")
        from database import db, init_app, create_all_tables
        print("  ✅ Database modules imported successfully")
    except Exception as e:
        print(f"  ❌ Database import failed: {e}")
        return False
    
    try:
        print("  - Testing models...")
        from models import User
        print("  ✅ User model imported successfully")
    except Exception as e:
        print(f"  ❌ User model import failed: {e}")
        return False
    
    try:
        print("  - Testing SubUser model...")
        from models import SubUser
        print("  ✅ SubUser model imported successfully")
    except Exception as e:
        print(f"  ❌ SubUser model import failed: {e}")
        return False
    
    try:
        print("  - Testing auth...")
        from auth import auth_bp
        print("  ✅ Auth module imported successfully")
    except Exception as e:
        print(f"  ❌ Auth import failed: {e}")
        return False
    
    try:
        print("  - Testing routes...")
        from routes import main_routes, player_routes, alliance_routes, event_routes, blacklist_routes
        from routes import user_settings_routes, feedback_routes, subuser_routes
        print("  ✅ Routes imported successfully")
    except Exception as e:
        print(f"  ❌ Routes import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database connection and setup"""
    print("\n🗄️ Testing database...")
    
    try:
        from flask import Flask
        from database import db, init_app, create_all_tables
        from models import User, SubUser
        
        # Create test app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-key'
        
        # Initialize database
        init_app(app)
        
        with app.app_context():
            print("  - Testing database connection...")
            # Try to create tables
            create_all_tables(app)
            print("  ✅ Database tables created successfully")
            
            # Test query
            users = User.query.all()
            print(f"  ✅ Found {len(users)} users in database")
            
            # Test SubUser table
            subusers = SubUser.query.all()
            print(f"  ✅ Found {len(subusers)} sub-users in database")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def test_app_creation():
    """Test creating the actual app"""
    print("\n🚀 Testing app creation...")
    
    try:
        # Import app
        from app import app
        print("  ✅ App imported successfully")
        
        # Test app configuration
        print(f"  - Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        print(f"  - Secret Key: {'Set' if app.config.get('SECRET_KEY') else 'Not set'}")
        print(f"  - Debug: {app.config.get('DEBUG')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ App creation failed: {e}")
        traceback.print_exc()
        return False

def check_file_permissions():
    """Check file permissions"""
    print("\n📁 Checking file permissions...")
    
    files_to_check = [
        'app.py',
        'models.py',
        'database.py',
        'auth.py',
        'kings_choice.db'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            if os.access(file, os.R_OK):
                print(f"  ✅ {file} is readable")
            else:
                print(f"  ❌ {file} is not readable")
            
            if os.access(file, os.W_OK):
                print(f"  ✅ {file} is writable")
            else:
                print(f"  ⚠️  {file} is not writable")
        else:
            print(f"  ❌ {file} does not exist")

def check_environment():
    """Check environment variables and Python version"""
    print("\n🌍 Checking environment...")
    
    print(f"  - Python version: {sys.version}")
    print(f"  - Python path: {sys.executable}")
    print(f"  - Working directory: {os.getcwd()}")
    print(f"  - PYTHONPATH: {sys.path[:3]}...")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("  ✅ Running in virtual environment")
    else:
        print("  ⚠️  Not running in virtual environment")

def main():
    """Run all diagnostics"""
    print("Starting comprehensive diagnostics...\n")
    
    # Check environment
    check_environment()
    
    # Check file permissions
    check_file_permissions()
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Check dependencies.")
        return False
    
    # Test database
    if not test_database():
        print("\n❌ Database tests failed. Check database setup.")
        return False
    
    # Test app creation
    if not test_app_creation():
        print("\n❌ App creation failed. Check app.py configuration.")
        return False
    
    print("\n🎉 All diagnostics passed! App should start successfully.")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
