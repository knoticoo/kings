#!/usr/bin/env python3
"""
Fix Import Issues Script
This script fixes common import issues that cause startup failures
"""

import os
import sys
import shutil
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def clean_python_cache():
    """Clean Python cache files"""
    print("🧹 Cleaning Python cache files...")
    
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
        else:
            print(f"   ✅ {cache_dir} does not exist")

def fix_models_imports():
    """Fix any issues in models.py"""
    print("🔧 Checking models.py for issues...")
    
    try:
        with open('models.py', 'r') as f:
            content = f.read()
        
        # Check for any problematic imports or references
        issues_found = False
        
        # Check for guide references
        if 'guide' in content.lower():
            print("   ⚠️  Found 'guide' references in models.py")
            issues_found = True
        
        # Check for syntax errors
        try:
            compile(content, 'models.py', 'exec')
            print("   ✅ models.py syntax is valid")
        except SyntaxError as e:
            print(f"   ❌ models.py syntax error: {e}")
            return False
        
        if not issues_found:
            print("   ✅ No issues found in models.py")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading models.py: {e}")
        return False

def create_minimal_app():
    """Create a minimal app.py for testing"""
    print("🔧 Creating minimal app.py for testing...")
    
    minimal_app = '''#!/usr/bin/env python3
"""
Minimal King's Choice App for Testing
"""

from flask import Flask
from flask_login import LoginManager
from database import db, init_app, create_all_tables
from models import User, SubUser

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'

# Initialize database
init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    # Try to find regular user first
    user = User.query.get(int(user_id))
    if user:
        return user
    # If not found, try sub-user
    return SubUser.query.get(int(user_id))

# Create tables
with app.app_context():
    create_all_tables(app)

@app.route('/')
def index():
    return "King's Choice App is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
'''
    
    try:
        with open('app_minimal.py', 'w') as f:
            f.write(minimal_app)
        print("   ✅ Created app_minimal.py")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create minimal app: {e}")
        return False

def test_minimal_app():
    """Test the minimal app"""
    print("🧪 Testing minimal app...")
    
    try:
        from app_minimal import app
        print("   ✅ Minimal app imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Minimal app import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_route_imports():
    """Fix route import issues"""
    print("🔧 Checking route imports...")
    
    route_files = [
        'routes/main_routes.py',
        'routes/player_routes.py',
        'routes/alliance_routes.py',
        'routes/event_routes.py',
        'routes/blacklist_routes.py',
        'routes/user_settings_routes.py',
        'routes/feedback_routes.py',
        'routes/subuser_routes.py'
    ]
    
    for route_file in route_files:
        if os.path.exists(route_file):
            try:
                with open(route_file, 'r') as f:
                    content = f.read()
                
                # Check for guide references
                if 'guide' in content.lower():
                    print(f"   ⚠️  Found 'guide' references in {route_file}")
                    # Remove guide references
                    lines = content.split('\n')
                    new_lines = []
                    for line in lines:
                        if 'guide' not in line.lower():
                            new_lines.append(line)
                    
                    with open(route_file, 'w') as f:
                        f.write('\n'.join(new_lines))
                    print(f"   ✅ Cleaned {route_file}")
                else:
                    print(f"   ✅ {route_file} is clean")
                    
            except Exception as e:
                print(f"   ⚠️  Error processing {route_file}: {e}")

def main():
    """Main fix function"""
    print("🔧 King's Choice App - Import Fix Script")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Step 1: Clean cache
    clean_python_cache()
    
    # Step 2: Fix models
    if not fix_models_imports():
        print("❌ Models fix failed")
        return False
    
    # Step 3: Fix route imports
    fix_route_imports()
    
    # Step 4: Create minimal app
    if not create_minimal_app():
        print("❌ Minimal app creation failed")
        return False
    
    # Step 5: Test minimal app
    if not test_minimal_app():
        print("❌ Minimal app test failed")
        return False
    
    print("\n🎉 Import fixes completed!")
    print("\n📋 Next steps:")
    print("1. Try running: python3 app_minimal.py")
    print("2. If that works, try: python3 app.py")
    print("3. If app.py still fails, run: python3 debug_imports.py")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
