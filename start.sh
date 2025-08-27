#!/bin/bash

# King's Choice Management App - Production Start Script
# This script handles complete setup, installation, and deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="Kings Choice Management"
APP_DIR="/workspace"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"
PID_FILE="$APP_DIR/app.pid"
LOG_FILE="$LOG_DIR/app.log"
ERROR_LOG="$LOG_DIR/error.log"
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p "$LOG_DIR"
    mkdir -p "$APP_DIR/static/uploads" 2>/dev/null || true
    mkdir -p "$APP_DIR/backups" 2>/dev/null || true
    print_success "Directories created"
}

# Function to install system dependencies
install_system_deps() {
    print_status "Checking system dependencies..."
    
    # Check if we're on Ubuntu/Debian
    if command_exists apt-get; then
        print_status "Detected Debian/Ubuntu system"
        
        # Update package list
        if [ "$EUID" -eq 0 ]; then
            apt-get update -qq
            apt-get install -y python3 python3-pip python3-venv sqlite3 curl wget
        else
            print_warning "Not running as root. System packages may need manual installation."
            print_warning "Required packages: python3 python3-pip python3-venv sqlite3 curl wget"
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
            $PKG_MANAGER install -y python3 python3-pip python3-venv sqlite curl wget
        else
            print_warning "Not running as root. System packages may need manual installation."
            print_warning "Required packages: python3 python3-pip python3-venv sqlite curl wget"
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
    print_status "Setting up Python virtual environment..."
    
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
    print_status "Installing Python dependencies..."
    
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

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    # Ensure we're in the virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Change to app directory
    cd "$APP_DIR"
    
    # Initialize database
    python3 -c "
from app import app, db, create_tables
print('Creating database tables...')
create_tables()
print('Database setup complete!')
"
    
    print_success "Database initialized"
}

# Function to run tests
run_tests() {
    print_status "Running application tests..."
    
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
    from models import Player, Alliance, Event, MVPAssignment, WinnerAssignment
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

# Function to start the application
start_app() {
    print_status "Starting application..."
    
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
            --workers 4 \
            --worker-class sync \
            --timeout 60 \
            --keepalive 2 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --log-file "$LOG_FILE" \
            --error-logfile "$ERROR_LOG" \
            --log-level info \
            --daemon \
            --pid "$PID_FILE" \
            app:app
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

# Function to show application status
show_status() {
    print_status "Application Status:"
    
    if is_app_running; then
        PID=$(cat "$PID_FILE")
        MEMORY=$(ps -p "$PID" -o rss= 2>/dev/null | awk '{print int($1/1024) " MB"}' || echo "Unknown")
        CPU=$(ps -p "$PID" -o %cpu= 2>/dev/null | awk '{print $1"%"}' || echo "Unknown")
        UPTIME=$(ps -p "$PID" -o etime= 2>/dev/null | awk '{print $1}' || echo "Unknown")
        
        echo -e "${GREEN}Status:${NC} Running"
        echo -e "${GREEN}PID:${NC} $PID"
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
        echo -e "${RED}Status:${NC} Not running"
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

# Function to restart the application
restart_app() {
    print_status "Restarting application..."
    stop_app
    sleep 2
    start_app
}

# Function to backup database
backup_database() {
    print_status "Creating database backup..."
    
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
    echo -e "${BLUE}$APP_NAME - Production Management Script${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     - Complete installation (system deps, venv, app deps, database)"
    echo "  start       - Start the application"
    echo "  stop        - Stop the application"
    echo "  restart     - Restart the application"
    echo "  status      - Show application status"
    echo "  logs [N]    - Show last N lines of logs (default: 50)"
    echo "  backup      - Backup the database"
    echo "  test        - Run application tests"
    echo "  update      - Update dependencies and restart"
    echo "  clean       - Clean up temporary files and logs"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install              # Full installation"
    echo "  $0 start                # Start application"
    echo "  $0 logs 100             # Show last 100 log lines"
    echo "  $0 backup               # Backup database"
    echo ""
}

# Function to update the application
update_app() {
    print_status "Updating application..."
    
    # Stop app if running
    if is_app_running; then
        stop_app
    fi
    
    # Backup database
    backup_database
    
    # Update Python dependencies
    source "$VENV_DIR/bin/activate"
    pip install --upgrade -r "$APP_DIR/requirements.txt"
    
    # Run any database migrations (if needed)
    setup_database
    
    # Run tests
    run_tests
    
    # Start application
    start_app
    
    print_success "Application updated successfully"
}

# Function to clean up
clean_app() {
    print_status "Cleaning up temporary files..."
    
    # Stop app if running
    if is_app_running; then
        stop_app
    fi
    
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
            print_status "Starting complete installation..."
            create_directories
            install_system_deps
            setup_virtualenv
            install_python_deps
            setup_database
            run_tests
            print_success "Installation completed successfully!"
            echo ""
            print_status "To start the application, run: $0 start"
            ;;
        "start")
            start_app
            ;;
        "stop")
            stop_app
            ;;
        "restart")
            restart_app
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