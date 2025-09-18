#!/bin/bash

# King's Choice Management App - Complete VPS Installation and Startup Script
# This script handles everything: dependencies, environment, migration, and startup

set -e  # Exit on any error

echo "🚀 King's Choice Management App - VPS Installation Script"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This is not recommended for security reasons."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_status "Working directory: $SCRIPT_DIR"

# Fix permissions first
print_status "Fixing file permissions..."
chmod +x *.sh 2>/dev/null || true
chmod +x *.py 2>/dev/null || true
chmod 644 *.py 2>/dev/null || true
chmod 755 . 2>/dev/null || true

# Check if Python 3 is installed
print_status "Checking Python 3 installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    print_status "On Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    print_status "On CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python 3.$PYTHON_VERSION found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed from requirements.txt"
else
    print_warning "requirements.txt not found, installing basic dependencies..."
    pip install flask flask-login flask-sqlalchemy flask-babel python-dotenv werkzeug
    print_success "Basic dependencies installed"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p user_databases
mkdir -p logs
mkdir -p static/css
mkdir -p static/js
mkdir -p static/icons
mkdir -p templates/auth
mkdir -p templates/admin
mkdir -p templates/feedback
mkdir -p templates/modern/alliances
mkdir -p templates/modern/events
mkdir -p templates/modern/players
mkdir -p translations/en/LC_MESSAGES
mkdir -p translations/ru/LC_MESSAGES

# Fix directory permissions
chmod 755 user_databases logs 2>/dev/null || true
chmod 755 static templates translations 2>/dev/null || true

print_success "Directories created with proper permissions"

# Set up environment variables
print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Database Configuration
DATABASE_URL=sqlite:///kings_choice.db

# Language Configuration
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,ru

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=False
EOF
    print_success "Environment file created"
else
    print_status "Environment file already exists"
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Database migration and setup
print_status "Setting up database..."
python3 -c "
import os
import sys
sys.path.insert(0, '.')

from flask import Flask
from database import db, init_app, create_all_tables
from models import User, SubUser

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')

# Initialize database
init_app(app)

with app.app_context():
    try:
        # Create all tables
        create_all_tables(app)
        print('✅ Database tables created successfully')
        
        # Check if SubUser table exists and works
        try:
            SubUser.query.first()
            print('✅ SubUser table is working')
        except Exception as e:
            print(f'⚠️  SubUser table issue: {e}')
            # Create SubUser table manually
            from sqlalchemy import text
            db.session.execute(text('''
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
            '''))
            db.session.commit()
            print('✅ SubUser table created manually')
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='knotico').first()
        if not admin_user:
            print('⚠️  No admin user found. You may need to create one.')
        else:
            print('✅ Admin user found')
            
        # Check users
        user_count = User.query.count()
        print(f'✅ Found {user_count} users in database')
            
    except Exception as e:
        print(f'❌ Database setup failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Database setup completed"
else
    print_error "Database setup failed"
    exit 1
fi

# Create systemd service file
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/kings-choice.service > /dev/null << EOF
[Unit]
Description=King's Choice Management App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment=PATH=$SCRIPT_DIR/venv/bin
Environment=SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
Environment=HOST=0.0.0.0
Environment=PORT=5000
Environment=DEBUG=False
ExecStart=$SCRIPT_DIR/venv/bin/python start_app_safe.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
print_status "Configuring systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable kings-choice.service
print_success "Systemd service configured"

# Create startup script
print_status "Creating startup script..."
cat > start_app.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)
python3 start_app_safe.py
EOF

chmod +x start_app.sh
print_success "Startup script created"

# Create stop script
print_status "Creating stop script..."
cat > stop_app.sh << 'EOF'
#!/bin/bash
sudo systemctl stop kings-choice.service
pkill -f "python.*app.py" || true
echo "Application stopped"
EOF

chmod +x stop_app.sh
print_success "Stop script created"

# Create status script
print_status "Creating status script..."
cat > status_app.sh << 'EOF'
#!/bin/bash
echo "=== King's Choice App Status ==="
echo "Systemd Service:"
sudo systemctl status kings-choice.service --no-pager -l
echo ""
echo "Process Status:"
ps aux | grep "python.*app.py" | grep -v grep || echo "No app processes running"
echo ""
echo "Port Status:"
netstat -tulpn | grep :5000 || echo "Port 5000 not in use"
EOF

chmod +x status_app.sh
print_success "Status script created"

# Test the application first
print_status "Testing application startup..."
python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from app import app
    print('✅ App imports successfully')
    
    # Test basic configuration
    print(f'  - Database: {app.config.get(\"SQLALCHEMY_DATABASE_URI\")}')
    print(f'  - Secret Key: {\"Set\" if app.config.get(\"SECRET_KEY\") else \"Not set\"}')
    
except Exception as e:
    print(f'❌ App test failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Application test passed"
else
    print_warning "Application test failed, but continuing with service setup"
fi

# Start the application
print_status "Starting application..."
sudo systemctl start kings-choice.service

# Wait a moment for startup
sleep 5

# Check if application is running
if systemctl is-active --quiet kings-choice.service; then
    print_success "Application started successfully!"
    print_status "Service status:"
    sudo systemctl status kings-choice.service --no-pager -l
else
    print_error "Failed to start application"
    print_status "Checking logs:"
    sudo journalctl -u kings-choice.service --no-pager -l
    print_status "Trying manual startup for debugging..."
    python3 start_app_safe.py
    exit 1
fi

# Display final information
echo ""
echo "🎉 Installation and startup completed successfully!"
echo "=================================================="
echo ""
echo "📋 Service Management Commands:"
echo "  Start:   sudo systemctl start kings-choice.service"
echo "  Stop:    sudo systemctl stop kings-choice.service"
echo "  Restart: sudo systemctl restart kings-choice.service"
echo "  Status:  sudo systemctl status kings-choice.service"
echo "  Logs:    sudo journalctl -u kings-choice.service -f"
echo ""
echo "📋 Quick Scripts:"
echo "  Start:   ./start_app.sh"
echo "  Stop:    ./stop_app.sh"
echo "  Status:  ./status_app.sh"
echo ""
echo "🌐 Application Access:"
echo "  Local:   http://localhost:5000"
echo "  Network: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "📁 Important Files:"
echo "  App Directory: $SCRIPT_DIR"
echo "  Database:      $SCRIPT_DIR/kings_choice.db"
echo "  Logs:          sudo journalctl -u kings-choice.service"
echo "  Config:        $SCRIPT_DIR/.env"
echo ""

# Test the application
print_status "Testing application..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200"; then
    print_success "Application is responding correctly"
else
    print_warning "Application may not be responding correctly. Check logs for details."
fi

echo ""
print_success "Setup complete! Your King's Choice Management App is now running."