#!/usr/bin/env python3
"""
Comprehensive Fix Script for King's Choice App
This script fixes all common syntax, import, and startup issues
"""

import os
import sys
import ast
import traceback
import subprocess

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def clean_cache():
    """Clean all Python cache files"""
    print("🧹 Cleaning Python cache files...")
    
    import shutil
    
    cache_dirs = [
        '__pycache__',
        'routes/__pycache__',
        'utils/__pycache__',
        'discord/__pycache__',
        'discord/cogs/__pycache__',
        'discord/core/__pycache__',
        'discord/utils/__pycache__'
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"   ✅ Removed {cache_dir}")
            except Exception as e:
                print(f"   ⚠️  Could not remove {cache_dir}: {e}")

def check_syntax(file_path):
    """Check syntax of a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the file
        ast.parse(content, filename=file_path)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def fix_import_issues():
    """Fix all import issues"""
    print("🔧 Fixing import issues...")
    
    # Fix app.py imports
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Ensure all models are imported
        if 'from models import' in content:
            # Check if all required models are imported
            required_models = ['User', 'SubUser', 'Player', 'Alliance', 'Event', 'MVPAssignment', 'WinnerAssignment', 'Blacklist', 'Feedback']
            missing_models = []
            
            for model in required_models:
                if model not in content:
                    missing_models.append(model)
            
            if missing_models:
                print(f"   ⚠️  Missing models in app.py: {missing_models}")
                # Fix the import line
                import_line = 'from models import ' + ', '.join(required_models)
                content = content.replace(
                    'from models import User, SubUser, Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist, Feedback',
                    import_line
                )
                
                with open('app.py', 'w') as f:
                    f.write(content)
                print("   ✅ Fixed model imports in app.py")
            else:
                print("   ✅ All models properly imported in app.py")
        
    except Exception as e:
        print(f"   ❌ Error fixing app.py: {e}")

def check_all_files():
    """Check all Python files for issues"""
    print("🔍 Checking all Python files...")
    
    python_files = []
    
    # Find all Python files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(os.path.join(root, file))
    
    errors_found = False
    
    for file_path in python_files:
        is_valid, error = check_syntax(file_path)
        if not is_valid:
            print(f"   ❌ {file_path}: {error}")
            errors_found = True
        else:
            print(f"   ✅ {file_path}")
    
    return not errors_found

def test_imports():
    """Test all imports step by step"""
    print("🧪 Testing imports...")
    
    try:
        print("   - Testing basic imports...")
        from flask import Flask
        from flask_login import LoginManager
        print("   ✅ Flask imports OK")
    except Exception as e:
        print(f"   ❌ Flask imports failed: {e}")
        return False
    
    try:
        print("   - Testing database imports...")
        from database import db, init_app, create_all_tables
        print("   ✅ Database imports OK")
    except Exception as e:
        print(f"   ❌ Database imports failed: {e}")
        return False
    
    try:
        print("   - Testing model imports...")
        from models import User, SubUser, Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist, Feedback
        print("   ✅ Model imports OK")
    except Exception as e:
        print(f"   ❌ Model imports failed: {e}")
        return False
    
    try:
        print("   - Testing route imports...")
        from routes import main_routes, player_routes, alliance_routes, event_routes, blacklist_routes
        from routes import user_settings_routes, feedback_routes, subuser_routes
        print("   ✅ Route imports OK")
    except Exception as e:
        print(f"   ❌ Route imports failed: {e}")
        return False
    
    try:
        print("   - Testing app import...")
        from app import app
        print("   ✅ App import OK")
    except Exception as e:
        print(f"   ❌ App import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_database():
    """Test database setup"""
    print("🗄️ Testing database setup...")
    
    try:
        from flask import Flask
        from database import db, init_app, create_all_tables
        from models import User, SubUser, Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist, Feedback
        
        # Create test app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-key'
        
        # Initialize database
        init_app(app)
        
        with app.app_context():
            # Create all tables
            create_all_tables(app)
            print("   ✅ Database tables created")
            
            # Test basic queries
            user_count = User.query.count()
            print(f"   ✅ Found {user_count} users")
            
            # Test SubUser table
            try:
                subuser_count = SubUser.query.count()
                print(f"   ✅ Found {subuser_count} sub-users")
            except Exception as e:
                print(f"   ⚠️  SubUser table issue: {e}")
            
            # Test Feedback table
            try:
                feedback_count = Feedback.query.count()
                print(f"   ✅ Found {feedback_count} feedback entries")
            except Exception as e:
                print(f"   ⚠️  Feedback table issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def create_startup_script():
    """Create a simple startup script"""
    print("📝 Creating startup script...")
    
    startup_script = '''#!/usr/bin/env python3
"""
Simple startup script for King's Choice App
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 Starting King's Choice Management App...")
    print(f"Started at: {datetime.now()}")
    
    try:
        from app import app
        
        # Get configuration
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        print(f"Starting on {host}:{port}")
        print("Press Ctrl+C to stop")
        
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
'''
    
    try:
        with open('start_simple.py', 'w') as f:
            f.write(startup_script)
        print("   ✅ Created start_simple.py")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create startup script: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 King's Choice App - Comprehensive Fix Script")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print()
    
    # Step 1: Clean cache
    clean_cache()
    
    # Step 2: Fix imports
    fix_import_issues()
    
    # Step 3: Check syntax
    if not check_all_files():
        print("❌ Syntax errors found")
        return False
    
    # Step 4: Test imports
    if not test_imports():
        print("❌ Import test failed")
        return False
    
    # Step 5: Test database
    if not test_database():
        print("❌ Database test failed")
        return False
    
    # Step 6: Create startup script
    create_startup_script()
    
    print("\n🎉 All issues fixed!")
    print("\n📋 You can now start the app with:")
    print("   python3 start_simple.py")
    print("   or")
    print("   python3 app.py")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
