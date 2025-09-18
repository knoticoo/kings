#!/bin/bash

# Diagnostic script to check VPS setup
# This will help us identify exactly what's wrong

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

print_step "Diagnosing VPS setup..."

# Check current directory
print_status "Current directory: $(pwd)"
print_status "Contents:"
ls -la

# Check Python installation
print_status "Python version:"
python3 --version

# Check if python3-venv is available
print_status "Checking python3-venv:"
if python3 -m venv --help >/dev/null 2>&1; then
    print_success "python3-venv is available"
else
    print_error "python3-venv is NOT available"
fi

# Check for existing virtual environments
print_status "Looking for virtual environments:"
if [ -d "env" ]; then
    print_status "Found 'env' directory"
    ls -la env/
    if [ -f "env/bin/activate" ]; then
        print_success "env/bin/activate exists"
    else
        print_error "env/bin/activate NOT found"
    fi
else
    print_warning "No 'env' directory found"
fi

if [ -d "venv" ]; then
    print_status "Found 'venv' directory"
    ls -la venv/
    if [ -f "venv/bin/activate" ]; then
        print_success "venv/bin/activate exists"
    else
        print_error "venv/bin/activate NOT found"
    fi
else
    print_warning "No 'venv' directory found"
fi

# Check if we can create a virtual environment
print_status "Testing virtual environment creation:"
if python3 -m venv test_venv >/dev/null 2>&1; then
    print_success "Can create virtual environment"
    rm -rf test_venv
else
    print_error "Cannot create virtual environment"
fi

# Check if Flask is installed globally
print_status "Checking if Flask is installed globally:"
if python3 -c "import flask; print('Flask version:', flask.__version__)" 2>/dev/null; then
    print_success "Flask is installed globally"
else
    print_warning "Flask is NOT installed globally"
fi

# Check requirements.txt
print_status "Checking requirements.txt:"
if [ -f "requirements.txt" ]; then
    print_success "requirements.txt exists"
    print_status "First 10 lines:"
    head -10 requirements.txt
else
    print_error "requirements.txt NOT found"
fi

# Check app.py
print_status "Checking app.py:"
if [ -f "app.py" ]; then
    print_success "app.py exists"
    print_status "First 10 lines:"
    head -10 app.py
else
    print_error "app.py NOT found"
fi

print_step "Diagnosis complete!"