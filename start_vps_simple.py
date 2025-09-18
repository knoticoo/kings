#!/usr/bin/env python3
"""
Simple VPS Startup Script - No shell permissions required
This script can be run directly with python3 without needing chmod
"""

import os
import sys
import subprocess
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_permissions():
    """Fix file permissions using Python"""
    print("🔧 Fixing permissions...")
    
    try:
        # Make Python files readable
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    os.chmod(filepath, 0o644)
        
        # Make database file writable
        if os.path.exists('kings_choice.db'):
            os.chmod('kings_choice.db', 0o664)
            print("✅ Database permissions fixed")
        
        # Create directories
        dirs_to_create = [
            'user_databases', 'logs', 'static/css', 'static/js', 'static/icons',
            'templates/auth', 'templates/admin', 'templates/feedback',
            'templates/modern/alliances', 'templates/modern/events', 'templates/modern/players',
            'translations/en/LC_MESSAGES', 'translations/ru/LC_MESSAGES'
        ]
        
        for dir_path in dirs_to_create:
            os.makedirs(dir_path, exist_ok=True)
            os.chmod(dir_path, 0o755)
        
        print("✅ Permissions and directories fixed")
        return True
        
    except Exception as e:
        print(f"⚠️  Permission fix failed: {e}")
        return False

def setup_database():
    """Setup database with migration"""
    print("🗄️ Setting up database...")
    
    try:
        from flask import Flask
        from database import db, init_app, create_all_tables
        from models import User, SubUser
        
        # Create Flask app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vps-secret-key-12345')
        
        # Initialize database
        init_app(app)
        
        with app.app_context():
            # Create all tables
            create_all_tables(app)
            print("✅ Database tables created/updated")
            
            # Check SubUser table
            try:
                SubUser.query.first()
                print("✅ SubUser table is working")
            except Exception as e:
                print(f"⚠️  SubUser table issue: {e}")
                # Create SubUser table manually
                from sqlalchemy import text
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS sub_users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        parent_user_id INTEGER NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        permissions TEXT DEFAULT '{}',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME,
                        FOREIGN KEY (parent_user_id) REFERENCES users(id)
                    )
                """))
                db.session.commit()
                print("✅ SubUser table created manually")
            
            # Check users
            user_count = User.query.count()
            print(f"✅ Found {user_count} users in database")
            
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📚 Installing dependencies...")
    
    try:
        # Check if virtual environment exists
        if not os.path.exists('venv'):
            print("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
        # Get virtual environment Python path
        if os.name == 'nt':  # Windows
            venv_python = os.path.join('venv', 'Scripts', 'python.exe')
        else:  # Linux/Unix
            venv_python = os.path.join('venv', 'bin', 'python')
        
        if not os.path.exists(venv_python):
            print("❌ Virtual environment not found")
            return False
        
        # Install dependencies
        if os.path.exists('requirements.txt'):
            subprocess.run([venv_python, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        else:
            # Install basic dependencies
            basic_deps = [
                'flask', 'flask-login', 'flask-sqlalchemy', 'flask-babel', 
                'python-dotenv', 'werkzeug'
            ]
            subprocess.run([venv_python, '-m', 'pip', 'install'] + basic_deps, check=True)
        
        print("✅ Dependencies installed")
        return True
        
    except Exception as e:
        print(f"❌ Dependency installation failed: {e}")
        return False

def start_application():
    """Start the application"""
    print("🚀 Starting King's Choice Management App...")
    
    try:
        # Set environment variables
        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'production'
        os.environ['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vps-secret-key-12345')
        os.environ['HOST'] = '0.0.0.0'
        os.environ['PORT'] = '5000'
        os.environ['DEBUG'] = 'False'
        
        # Import and start the app
        from app import app
        
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        print(f"Starting on {host}:{port}")
        print(f"Access at: http://{host}:{port}")
        print("Press Ctrl+C to stop")
        
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🎯 King's Choice App - Simple VPS Startup")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print()
    
    # Step 1: Fix permissions
    fix_permissions()
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Step 3: Setup database
    if not setup_database():
        print("❌ Database setup failed")
        sys.exit(1)
    
    # Step 4: Start application
    print("\n✅ Setup completed successfully!")
    try:
        start_application()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Application crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
