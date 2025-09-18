#!/usr/bin/env python3
"""
Fix Syntax Errors Script
This script fixes common syntax and import errors
"""

import os
import sys
import ast
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_syntax(file_path):
    """Check syntax of a Python file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Try to parse the file
        ast.parse(content, filename=file_path)
        return True, None
    except SyntaxError as e:
        return False, e
    except Exception as e:
        return False, e

def fix_import_issues():
    """Fix common import issues"""
    print("🔧 Fixing import issues...")
    
    # Check app.py imports
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if Feedback is imported
        if 'from models import' in content and 'Feedback' not in content:
            print("   ⚠️  Feedback model not imported in app.py")
            # Fix the import
            content = content.replace(
                'from models import User, SubUser, Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist',
                'from models import User, SubUser, Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist, Feedback'
            )
            
            with open('app.py', 'w') as f:
                f.write(content)
            print("   ✅ Fixed Feedback import in app.py")
        
    except Exception as e:
        print(f"   ❌ Error fixing app.py: {e}")

def check_all_python_files():
    """Check all Python files for syntax errors"""
    print("🔍 Checking all Python files for syntax errors...")
    
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
            print(f"   ❌ Syntax error in {file_path}: {error}")
            errors_found = True
        else:
            print(f"   ✅ {file_path} syntax OK")
    
    return not errors_found

def test_imports():
    """Test all imports"""
    print("🧪 Testing imports...")
    
    try:
        print("   - Testing models import...")
        from models import User, SubUser, Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist, Feedback
        print("   ✅ All models imported successfully")
    except Exception as e:
        print(f"   ❌ Models import failed: {e}")
        return False
    
    try:
        print("   - Testing routes import...")
        from routes import main_routes, player_routes, alliance_routes, event_routes, blacklist_routes
        from routes import user_settings_routes, feedback_routes, subuser_routes
        print("   ✅ All routes imported successfully")
    except Exception as e:
        print(f"   ❌ Routes import failed: {e}")
        return False
    
    try:
        print("   - Testing app import...")
        from app import app
        print("   ✅ App imported successfully")
    except Exception as e:
        print(f"   ❌ App import failed: {e}")
        return False
    
    return True

def main():
    """Main fix function"""
    print("🔧 King's Choice App - Syntax Fix Script")
    print("=" * 50)
    
    # Step 1: Fix import issues
    fix_import_issues()
    
    # Step 2: Check syntax
    if not check_all_python_files():
        print("❌ Syntax errors found")
        return False
    
    # Step 3: Test imports
    if not test_imports():
        print("❌ Import test failed")
        return False
    
    print("\n🎉 All syntax and import issues fixed!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
