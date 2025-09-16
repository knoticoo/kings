#!/bin/bash

# King's Choice Management Multi-User System - Complete Installation & Service Management
# This script handles complete setup, installation, multi-user configuration, and deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="King's Choice Management Multi-User System"
APP_DIR="/workspace"
VENV_DIR="$APP_DIR/env"
LOG_DIR="$APP_DIR/logs"
PID_FILE="$APP_DIR/app.pid"
LOG_FILE="$LOG_DIR/app.log"
ERROR_LOG="$LOG_DIR/error.log"
TELEGRAM_PID_FILE="$APP_DIR/telegram_bot.pid"
DISCORD_PID_FILE="$APP_DIR/discord_bot.pid"
PORT=5000
HOST="0.0.0.0"

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

print_header() {
    echo -e "${PURPLE}[HEADER]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create directories
create_directories() {
    print_step "Creating necessary directories..."
    mkdir -p "$LOG_DIR"
    mkdir -p "$APP_DIR/static/uploads" 2>/dev/null || true
    mkdir -p "$APP_DIR/backups" 2>/dev/null || true
    mkdir -p "$APP_DIR/user_databases" 2>/dev/null || true
    print_success "Directories created"
}

# Function to install system dependencies
install_system_deps() {
    print_step "Installing system dependencies..."
    
    # Check if we're on Ubuntu/Debian
    if command_exists apt-get; then
        print_status "Detected Debian/Ubuntu system"
        
        # Update package list
        if [ "$EUID" -eq 0 ]; then
            apt-get update -qq
            apt-get install -y python3 python3-pip python3-venv python3-dev sqlite3 curl wget build-essential
        else
            print_warning "Not running as root. System packages may need manual installation."
            print_warning "Required packages: python3 python3-pip python3-venv python3-dev sqlite3 curl wget build-essential"
        fi
    
    # Check if we're on CentOS/RHEL/Fedora
    elif command_exists yum || command_exists dnf; then
        print_status "Detected RedHat/CentOS/Fedora system"
        
        if command_exists dnf; then
            PKG_MANAGER="dnf"
        else
            PKG_MANAGER="yum"
        fi
        
        if [ "$EUID" -eq 0 ]; then
            $PKG_MANAGER install -y python3 python3-pip python3-venv python3-devel sqlite curl wget gcc
        else
            print_warning "Not running as root. System packages may need manual installation."
            print_warning "Required packages: python3 python3-pip python3-venv python3-devel sqlite curl wget gcc"
        fi
    
    # Check if we're on Alpine
    elif command_exists apk; then
        print_status "Detected Alpine Linux system"
        
        if [ "$EUID" -eq 0 ]; then
            apk add --no-cache python3 py3-pip python3-dev sqlite curl wget gcc musl-dev
        else
            print_warning "Not running as root. System packages may need manual installation."
        fi
    else
        print_warning "Unknown system. Please ensure Python 3.8+, pip, venv, and sqlite3 are installed."
    fi
    
    # Verify Python installation
    if ! command_exists python3; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    print_status "Python version: $PYTHON_VERSION"
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_success "Python version is compatible"
    else
        print_error "Python 3.8 or higher is required"
        exit 1
    fi
}

# Function to setup virtual environment
setup_virtualenv() {
    print_step "Setting up Python virtual environment..."
    
    # Remove existing venv if it exists
    if [ -d "$VENV_DIR" ]; then
        print_warning "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    # Create new virtual environment
    python3 -m venv "$VENV_DIR"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment created and activated"
}

# Function to install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."
    
    # Ensure we're in the virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install dependencies
    if [ -f "$APP_DIR/requirements.txt" ]; then
        pip install -r "$APP_DIR/requirements.txt"
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Function to setup multi-user database
setup_multi_user_database() {
    print_step "Setting up multi-user database system..."
    
    # Ensure we're in the virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Change to app directory
    cd "$APP_DIR"
    
    # Run the multi-user setup script
    if [ -f "$APP_DIR/setup_multi_user.py" ]; then
        print_status "Running multi-user database setup..."
        python3 setup_multi_user.py
        print_success "Multi-user database setup completed"
    else
        print_error "setup_multi_user.py not found"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_step "Running application tests..."
    
    # Ensure we're in the virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Change to app directory
    cd "$APP_DIR"
    
    # Basic import test
    python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from app import app
    from models import User, Player, Alliance, Event, MVPAssignment, WinnerAssignment
    from utils.rotation_logic import can_assign_mvp, can_assign_winner
    print('✓ All imports successful')
    
    # Test app creation
    with app.app_context():
        print('✓ Flask app context works')
    
    print('✓ All tests passed')
except Exception as e:
    print(f'✗ Test failed: {e}')
    sys.exit(1)
"
    
    print_success "All tests passed"
}

# Function to check if app is running
is_app_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # App is running
        else
            rm -f "$PID_FILE"  # Remove stale PID file
            return 1  # App is not running
        fi
    else
        return 1  # PID file doesn't exist
    fi
}

# Function to check if telegram bot is running
is_telegram_running() {
    if [ -f "$TELEGRAM_PID_FILE" ]; then
        PID=$(cat "$TELEGRAM_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$TELEGRAM_PID_FILE"
            return 1
        fi
    else
        return 1
    fi
}

# Function to check if discord bot is running
is_discord_running() {
    if [ -f "$DISCORD_PID_FILE" ]; then
        PID=$(cat "$DISCORD_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$DISCORD_PID_FILE"
            return 1
        fi
    else
        return 1
    fi
}

# Function to stop the application
stop_app() {
    print_status "Stopping application..."
    
    if is_app_running; then
        PID=$(cat "$PID_FILE")
        print_status "Stopping process $PID..."
        
        # Try graceful shutdown first
        kill -TERM "$PID" 2>/dev/null || true
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Forcing application shutdown..."
            kill -KILL "$PID" 2>/dev/null || true
        fi
        
        rm -f "$PID_FILE"
        print_success "Application stopped"
    else
        print_warning "Application is not running"
    fi
}

# Function to stop telegram bot
stop_telegram() {
    if is_telegram_running; then
        PID=$(cat "$TELEGRAM_PID_FILE")
        print_status "Stopping Telegram bot (PID: $PID)..."
        kill -TERM "$PID" 2>/dev/null || true
        sleep 2
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -KILL "$PID" 2>/dev/null || true
        fi
        rm -f "$TELEGRAM_PID_FILE"
        print_success "Telegram bot stopped"
    fi
}

# Function to stop discord bot
stop_discord() {
    if is_discord_running; then
        PID=$(cat "$DISCORD_PID_FILE")
        print_status "Stopping Discord bot (PID: $PID)..."
        kill -TERM "$PID" 2>/dev/null || true
        sleep 2
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -KILL "$PID" 2>/dev/null || true
        fi
        rm -f "$DISCORD_PID_FILE"
        print_success "Discord bot stopped"
    fi
}

# Function to start the application
start_app() {
    print_step "Starting application..."
    
    if is_app_running; then
        print_warning "Application is already running (PID: $(cat $PID_FILE))"
        return
    fi
    
    # Ensure we're in the virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Change to app directory
    cd "$APP_DIR"
    
    # Create log files if they don't exist
    touch "$LOG_FILE" "$ERROR_LOG"
    
    # Start the application
    print_status "Starting $APP_NAME on $HOST:$PORT..."
    
    # Use gunicorn if available, otherwise use Flask development server
    if command_exists gunicorn; then
        print_status "Starting with Gunicorn (production server)..."
        nohup gunicorn \
            --bind "$HOST:$PORT" \
            --workers 1 \
            --worker-class sync \
            --timeout 120 \
            --max-requests 500 \
            --max-requests-jitter 50 \
            --worker-connections 1000 \
            --preload \
            --access-logfile "$LOG_FILE" \
            --error-logfile "$ERROR_LOG" \
            --log-level info \
            --daemon \
            --pid "$PID_FILE" \
            app:app > /dev/null 2>&1 &
    else
        print_warning "Gunicorn not found, using Flask development server..."
        nohup python3 app.py > "$LOG_FILE" 2> "$ERROR_LOG" &
        echo $! > "$PID_FILE"
    fi
    
    # Wait a moment and check if the app started
    sleep 3
    
    if is_app_running; then
        print_success "Application started successfully!"
        print_success "PID: $(cat $PID_FILE)"
        print_success "Access the application at: http://localhost:$PORT"
        print_success "Logs: $LOG_FILE"
        print_success "Error logs: $ERROR_LOG"
    else
        print_error "Failed to start application"
        print_error "Check logs for details:"
        print_error "  Main log: $LOG_FILE"
        print_error "  Error log: $ERROR_LOG"
        exit 1
    fi
}

# Function to check if telegram bot is configured
is_telegram_configured() {
    # Check if any user has telegram configured
    source "$VENV_DIR/bin/activate"
    cd "$APP_DIR"
    
    python3 -c "
import sys
sys.path.insert(0, '.')
from models import User
from database import db, init_app
from app import app

with app.app_context():
    users = User.query.filter(
        User.telegram_enabled == True,
        User.telegram_bot_token.isnot(None),
        User.telegram_chat_id.isnot(None)
    ).all()
    if users:
        print('configured')
    else:
        print('not_configured')
" 2>/dev/null | grep -q "configured"
}

# Function to start telegram bot
start_telegram() {
    if [ -f "$APP_DIR/telegram_bot.py" ]; then
        print_step "Starting Telegram bot..."
        
        if is_telegram_running; then
            print_warning "Telegram bot is already running"
            return
        fi
        
        # Check if telegram is configured
        if ! is_telegram_configured; then
            print_warning "Telegram bot not configured - no users have set up Telegram API keys"
            return
        fi
        
        source "$VENV_DIR/bin/activate"
        cd "$APP_DIR"
        
        nohup python3 telegram_bot.py > "$LOG_DIR/telegram.log" 2> "$LOG_DIR/telegram_error.log" &
        echo $! > "$TELEGRAM_PID_FILE"
        
        sleep 2
        if is_telegram_running; then
            print_success "Telegram bot started (PID: $(cat $TELEGRAM_PID_FILE))"
        else
            print_warning "Telegram bot failed to start"
        fi
    fi
}

# Function to check if discord bot is configured
is_discord_configured() {
    # Check if any user has discord configured
    source "$VENV_DIR/bin/activate"
    cd "$APP_DIR"
    
    python3 -c "
import sys
sys.path.insert(0, '.')
from models import User
from database import db, init_app
from app import app

with app.app_context():
    users = User.query.filter(
        User.discord_enabled == True,
        User.discord_bot_token.isnot(None),
        User.discord_channel_id.isnot(None)
    ).all()
    if users:
        print('configured')
    else:
        print('not_configured')
" 2>/dev/null | grep -q "configured"
}

# Function to start discord bot
start_discord() {
    if [ -f "$APP_DIR/discord_bot.py" ]; then
        print_step "Starting Discord bot..."
        
        if is_discord_running; then
            print_warning "Discord bot is already running"
            return
        fi
        
        # Check if discord is configured
        if ! is_discord_configured; then
            print_warning "Discord bot not configured - no users have set up Discord API keys"
            return
        fi
        
        source "$VENV_DIR/bin/activate"
        cd "$APP_DIR"
        
        nohup python3 discord_bot.py > "$LOG_DIR/discord.log" 2> "$LOG_DIR/discord_error.log" &
        echo $! > "$DISCORD_PID_FILE"
        
        sleep 2
        if is_discord_running; then
            print_success "Discord bot started (PID: $(cat $DISCORD_PID_FILE))"
        else
            print_warning "Discord bot failed to start"
        fi
    fi
}

# Function to show application status
show_status() {
    print_header "Application Status:"
    
    # Main application status
    if is_app_running; then
        PID=$(cat "$PID_FILE")
        MEMORY=$(ps -p "$PID" -o rss= 2>/dev/null | awk '{print int($1/1024) " MB"}' || echo "Unknown")
        CPU=$(ps -p "$PID" -o %cpu= 2>/dev/null | awk '{print $1"%"}' || echo "Unknown")
        UPTIME=$(ps -p "$PID" -o etime= 2>/dev/null | awk '{print $1}' || echo "Unknown")
        
        echo -e "${GREEN}Main App:${NC} Running (PID: $PID)"
        echo -e "${GREEN}Memory:${NC} $MEMORY"
        echo -e "${GREEN}CPU:${NC} $CPU"
        echo -e "${GREEN}Uptime:${NC} $UPTIME"
        echo -e "${GREEN}URL:${NC} http://localhost:$PORT"
        
        # Check if port is accessible
        if command_exists curl; then
            if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" | grep -q "200"; then
                echo -e "${GREEN}Health:${NC} OK"
            else
                echo -e "${YELLOW}Health:${NC} Not responding"
            fi
        fi
    else
        echo -e "${RED}Main App:${NC} Not running"
    fi
    
    # Telegram bot status
    if is_telegram_running; then
        echo -e "${GREEN}Telegram Bot:${NC} Running (PID: $(cat $TELEGRAM_PID_FILE))"
    elif is_telegram_configured; then
        echo -e "${YELLOW}Telegram Bot:${NC} Not running (configured)"
    else
        echo -e "${RED}Telegram Bot:${NC} Not running (not configured)"
    fi
    
    # Discord bot status
    if is_discord_running; then
        echo -e "${GREEN}Discord Bot:${NC} Running (PID: $(cat $DISCORD_PID_FILE))"
    elif is_discord_configured; then
        echo -e "${YELLOW}Discord Bot:${NC} Not running (configured)"
    else
        echo -e "${RED}Discord Bot:${NC} Not running (not configured)"
    fi
    
    echo -e "${BLUE}Logs:${NC} $LOG_FILE"
    echo -e "${BLUE}Error Logs:${NC} $ERROR_LOG"
}

# Function to show logs
show_logs() {
    local lines=${1:-50}
    
    print_status "Showing last $lines lines of logs:"
    
    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}=== Main Log ===${NC}"
        tail -n "$lines" "$LOG_FILE"
    else
        print_warning "Log file not found: $LOG_FILE"
    fi
    
    if [ -f "$ERROR_LOG" ]; then
        echo -e "${RED}=== Error Log ===${NC}"
        tail -n "$lines" "$ERROR_LOG"
    else
        print_warning "Error log file not found: $ERROR_LOG"
    fi
}

# Function to restart all services
restart_all() {
    print_step "Restarting all services..."
    stop_all
    sleep 3
    start_all
}

# Function to stop all services
stop_all() {
    print_step "Stopping all services..."
    stop_app
    stop_telegram
    stop_discord
}

# Function to start all services
start_all() {
    print_step "Starting all services..."
    start_app
    start_telegram
    start_discord
}

# Function to backup database
backup_database() {
    print_step "Creating database backup..."
    
    BACKUP_DIR="$APP_DIR/backups"
    BACKUP_FILE="$BACKUP_DIR/kings_choice_$(date +%Y%m%d_%H%M%S).db"
    
    mkdir -p "$BACKUP_DIR"
    
    if [ -f "$APP_DIR/kings_choice.db" ]; then
        cp "$APP_DIR/kings_choice.db" "$BACKUP_FILE"
        print_success "Database backed up to: $BACKUP_FILE"
    else
        print_warning "Database file not found: $APP_DIR/kings_choice.db"
    fi
}

# Function to show help
show_help() {
    echo -e "${PURPLE}$APP_NAME - Complete Installation & Service Management${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     - Complete installation (system deps, venv, app deps, multi-user setup)"
    echo "  start       - Start all services (app, telegram, discord)"
    echo "  start-app   - Start only the main application"
    echo "  start-telegram - Start only the Telegram bot"
    echo "  start-discord  - Start only the Discord bot"
    echo "  stop        - Stop all services"
    echo "  stop-app    - Stop only the main application"
    echo "  stop-telegram - Stop only the Telegram bot"
    echo "  stop-discord  - Stop only the Discord bot"
    echo "  restart     - Restart all services"
    echo "  status      - Show status of all services"
    echo "  logs [N]    - Show last N lines of logs (default: 50)"
    echo "  backup      - Backup the database"
    echo "  test        - Run application tests"
    echo "  update      - Update dependencies and restart all services"
    echo "  clean       - Clean up temporary files and logs"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install              # Full installation"
    echo "  $0 start                # Start all services"
    echo "  $0 logs 100             # Show last 100 log lines"
    echo "  $0 backup               # Backup database"
    echo ""
}

# Function to update the application
update_app() {
    print_step "Updating application..."
    
    # Stop all services if running
    stop_all
    
    # Backup database
    backup_database
    
    # Update Python dependencies
    source "$VENV_DIR/bin/activate"
    pip install --upgrade -r "$APP_DIR/requirements.txt"
    
    # Run tests
    run_tests
    
    # Start all services
    start_all
    
    print_success "Application updated successfully"
}

# Function to clean up
clean_app() {
    print_step "Cleaning up temporary files..."
    
    # Stop all services if running
    stop_all
    
    # Clean Python cache
    find "$APP_DIR" -name "*.pyc" -delete 2>/dev/null || true
    find "$APP_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Clean old logs (keep last 10)
    if [ -d "$LOG_DIR" ]; then
        find "$LOG_DIR" -name "*.log.*" -type f | sort | head -n -10 | xargs rm -f 2>/dev/null || true
    fi
    
    # Clean old backups (keep last 5)
    if [ -d "$APP_DIR/backups" ]; then
        find "$APP_DIR/backups" -name "*.db" -type f | sort | head -n -5 | xargs rm -f 2>/dev/null || true
    fi
    
    print_success "Cleanup completed"
}

# Main script logic
main() {
    # Change to app directory
    cd "$APP_DIR"
    
    case "${1:-help}" in
        "install")
            print_header "Starting complete installation..."
            create_directories
            install_system_deps
            setup_virtualenv
            install_python_deps
            setup_multi_user_database
            run_tests
            print_success "Installation completed successfully!"
            echo ""
            print_status "To start all services, run: $0 start"
            print_status "To start only the app, run: $0 start-app"
            ;;
        "start")
            start_all
            ;;
        "start-app")
            start_app
            ;;
        "start-telegram")
            start_telegram
            ;;
        "start-discord")
            start_discord
            ;;
        "stop")
            stop_all
            ;;
        "stop-app")
            stop_app
            ;;
        "stop-telegram")
            stop_telegram
            ;;
        "stop-discord")
            stop_discord
            ;;
        "restart")
            restart_all
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "${2:-50}"
            ;;
        "backup")
            backup_database
            ;;
        "test")
            run_tests
            ;;
        "update")
            update_app
            ;;
        "clean")
            clean_app
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"