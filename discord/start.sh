#!/bin/bash

# King's Choice Discord Bot Startup Script
# This script helps manage the Discord bot

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Bot directory
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$BOT_DIR/discord_bot.log"
PID_FILE="$BOT_DIR/discord_bot.pid"

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

# Function to check if bot is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the bot
start_bot() {
    if is_running; then
        print_warning "Bot is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    print_status "Starting King's Choice Discord Bot..."
    
    # Check if .env file exists
    if [ ! -f "$BOT_DIR/.env" ]; then
        print_error ".env file not found. Please copy .env.example to .env and configure it."
        return 1
    fi
    
    # Check if database exists
    if [ ! -f "../kings_choice.db" ] && [ ! -f "kings_choice.db" ]; then
        print_error "Database file not found. Please ensure the web app database is accessible."
        return 1
    fi
    
    # Start the bot in background
    cd "$BOT_DIR"
    nohup python run.py > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 2
    if is_running; then
        print_success "Bot started successfully (PID: $pid)"
        print_status "Logs are being written to: $LOG_FILE"
    else
        print_error "Failed to start bot. Check the logs for details."
        return 1
    fi
}

# Function to stop the bot
stop_bot() {
    if ! is_running; then
        print_warning "Bot is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    print_status "Stopping bot (PID: $pid)..."
    
    kill "$pid"
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt 10 ] && is_running; do
        sleep 1
        count=$((count + 1))
    done
    
    if is_running; then
        print_warning "Bot didn't stop gracefully, forcing termination..."
        kill -9 "$pid" 2>/dev/null || true
    fi
    
    rm -f "$PID_FILE"
    print_success "Bot stopped"
}

# Function to restart the bot
restart_bot() {
    print_status "Restarting bot..."
    stop_bot
    sleep 2
    start_bot
}

# Function to show bot status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_success "Bot is running (PID: $pid)"
        
        # Show uptime
        local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null || echo "Unknown")
        print_status "Started: $start_time"
        
        # Show log file size
        if [ -f "$LOG_FILE" ]; then
            local log_size=$(du -h "$LOG_FILE" | cut -f1)
            print_status "Log file size: $log_size"
        fi
    else
        print_warning "Bot is not running"
    fi
}

# Function to show logs
show_logs() {
    local lines=${1:-50}
    
    if [ ! -f "$LOG_FILE" ]; then
        print_error "Log file not found: $LOG_FILE"
        return 1
    fi
    
    print_status "Showing last $lines lines of logs:"
    echo "----------------------------------------"
    tail -n "$lines" "$LOG_FILE"
}

# Function to install dependencies
install_deps() {
    print_status "Installing Python dependencies..."
    
    if ! command -v pip &> /dev/null; then
        print_error "pip is not installed. Please install Python and pip first."
        return 1
    fi
    
    cd "$BOT_DIR"
    pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Function to setup the bot
setup_bot() {
    print_status "Setting up King's Choice Discord Bot..."
    
    # Check Python version
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        print_error "Python 3.8 or higher is required"
        return 1
    fi
    
    # Install dependencies
    install_deps
    
    # Create .env file if it doesn't exist
    if [ ! -f "$BOT_DIR/.env" ]; then
        if [ -f "$BOT_DIR/.env.example" ]; then
            cp "$BOT_DIR/.env.example" "$BOT_DIR/.env"
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your configuration before starting the bot"
        else
            print_error ".env.example file not found"
            return 1
        fi
    fi
    
    print_success "Setup completed successfully"
    print_status "Next steps:"
    echo "1. Edit .env file with your Discord bot token and configuration"
    echo "2. Ensure the web app database is accessible"
    echo "3. Run './start.sh start' to start the bot"
}

# Function to show help
show_help() {
    echo "King's Choice Discord Bot Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the bot"
    echo "  stop        Stop the bot"
    echo "  restart     Restart the bot"
    echo "  status      Show bot status"
    echo "  logs [N]    Show last N lines of logs (default: 50)"
    echo "  install     Install Python dependencies"
    echo "  setup       Initial setup (install deps, create .env)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs 100"
    echo "  $0 restart"
}

# Main script logic
case "${1:-help}" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    install)
        install_deps
        ;;
    setup)
        setup_bot
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac