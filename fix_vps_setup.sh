#!/bin/bash

# Quick fix script for VPS setup
# This script ensures the virtual environment and dependencies are properly set up

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Configuration
APP_DIR="/workspace"
VENV_DIR="$APP_DIR/env"

print_step "Fixing VPS setup for King's Choice Management..."

# Check if we're in the right directory
if [ ! -f "$APP_DIR/app.py" ]; then
    print_error "app.py not found. Please run this script from the application directory."
    exit 1
fi

# Install python3-venv if not available
print_status "Checking for python3-venv..."
if ! python3 -m venv --help >/dev/null 2>&1; then
    print_warning "python3-venv not available, installing..."
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt update && sudo apt install -y python3-venv
    else
        print_error "Please install python3-venv manually for your system"
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "$APP_DIR/requirements.txt" ]; then
    pip install -r "$APP_DIR/requirements.txt"
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create logs directory
mkdir -p "$APP_DIR/logs"

# Test if app can be imported
print_status "Testing application..."
if python -c "from app import app; print('App imported successfully')" 2>/dev/null; then
    print_success "Application test passed"
else
    print_error "Application test failed"
    exit 1
fi

print_success "VPS setup completed successfully!"
print_status "You can now run: ./install_and_start.sh start"