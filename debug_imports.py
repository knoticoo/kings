#!/usr/bin/env python3
"""
Debug Import Issues Script
This script helps identify exactly where the import error is occurring
"""

import sys
import os
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test imports step by step to find the exact error"""
    print("🔍 Debugging Import Issues")
    print("=" * 40)
    
    try:
        print("1. Testing Flask import...")
        from flask import Flask
        print("   ✅ Flask imported successfully")
    except Exception as e:
        print(f"   ❌ Flask import failed: {e}")
        return False
    
    try:
        print("2. Testing database import...")
        from database import db, init_app, create_all_tables
        print("   ✅ Database modules imported successfully")
    except Exception as e:
        print(f"   ❌ Database import failed: {e}")
        return False
    
    try:
        print("3. Testing models import...")
        from models import User, SubUser, Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist
        print("   ✅ All models imported successfully")
    except Exception as e:
        print(f"   ❌ Models import failed: {e}")
        print("   Full error:")
        traceback.print_exc()
        return False
    
    try:
        print("4. Testing auth import...")
        from auth import auth_bp
        print("   ✅ Auth module imported successfully")
    except Exception as e:
        print(f"   ❌ Auth import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("5. Testing main_routes import...")
        from routes import main_routes
        print("   ✅ main_routes imported successfully")
    except Exception as e:
        print(f"   ❌ main_routes import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("6. Testing player_routes import...")
        from routes import player_routes
        print("   ✅ player_routes imported successfully")
    except Exception as e:
        print(f"   ❌ player_routes import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("7. Testing alliance_routes import...")
        from routes import alliance_routes
        print("   ✅ alliance_routes imported successfully")
    except Exception as e:
        print(f"   ❌ alliance_routes import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("8. Testing event_routes import...")
        from routes import event_routes
        print("   ✅ event_routes imported successfully")
    except Exception as e:
        print(f"   ❌ event_routes import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("9. Testing blacklist_routes import...")
        from routes import blacklist_routes
        print("   ✅ blacklist_routes imported successfully")
    except Exception as e:
        print(f"   ❌ blacklist_routes import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("10. Testing user_settings_routes import...")
        from routes import user_settings_routes
        print("   ✅ user_settings_routes imported successfully")
    except Exception as e:
        print(f"   ❌ user_settings_routes import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("11. Testing feedback_routes import...")
        from routes import feedback_routes
        print("   ✅ feedback_routes imported successfully")
    except Exception as e:
        print(f"   ❌ feedback_routes import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("12. Testing subuser_routes import...")
        from routes import subuser_routes
        print("   ✅ subuser_routes imported successfully")
    except Exception as e:
        print(f"   ❌ subuser_routes import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("13. Testing full app import...")
        from app import app
        print("   ✅ App imported successfully")
    except Exception as e:
        print(f"   ❌ App import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def check_models_file():
    """Check the models.py file for any issues"""
    print("\n🔍 Checking models.py file...")
    
    try:
        with open('models.py', 'r') as f:
            content = f.read()
        
        # Check for any guide references
        if 'guide' in content.lower():
            print("   ⚠️  Found 'guide' references in models.py")
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'guide' in line.lower():
                    print(f"   Line {i}: {line.strip()}")
        else:
            print("   ✅ No 'guide' references found in models.py")
        
        # Check for syntax errors
        try:
            compile(content, 'models.py', 'exec')
            print("   ✅ models.py syntax is valid")
        except SyntaxError as e:
            print(f"   ❌ models.py syntax error: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error reading models.py: {e}")
        return False
    
    return True

def main():
    """Main debug function"""
    print("🐛 King's Choice App - Import Debug Script")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Check models file first
    if not check_models_file():
        print("❌ Models file has issues")
        return False
    
    # Test imports
    if test_imports():
        print("\n🎉 All imports successful!")
        return True
    else:
        print("\n❌ Import test failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
