#!/bin/bash

# Setup script for Python Playwright MCP Testing Framework
# Usage: ./scripts/setup.sh [options]

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

# Default values
ENVIRONMENT="local"
SKIP_BROWSERS=false
DEV_DEPENDENCIES=true

# Help function
show_help() {
    echo "Setup script for Python Playwright MCP Testing Framework"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  -e, --env ENV           Environment: local, docker (default: local)"
    echo "  --skip-browsers         Skip Playwright browser installation"
    echo "  --no-dev               Skip development dependencies"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                      # Full local setup"
    echo "  $0 --skip-browsers      # Setup without browser installation"
    echo "  $0 -e docker            # Setup for Docker environment"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-browsers)
            SKIP_BROWSERS=true
            shift
            ;;
        --no-dev)
            DEV_DEPENDENCIES=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check Python version
check_python() {
    print_status "Checking Python version..."
    
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    python_version=$(python --version 2>&1 | awk '{print $2}')
    major_version=$(echo $python_version | cut -d. -f1)
    minor_version=$(echo $python_version | cut -d. -f2)
    
    if [[ $major_version -lt 3 ]] || [[ $major_version -eq 3 && $minor_version -lt 9 ]]; then
        print_error "Python 3.9 or higher is required. Found: $python_version"
        exit 1
    fi
    
    print_success "Python version: $python_version"
}

# Setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [[ ! -d ".venv" ]]; then
        python -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        source .venv/Scripts/activate
        python_path=".venv/Scripts/python.exe"
    else
        source .venv/bin/activate
        python_path=".venv/bin/python"
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    $python_path -m pip install --upgrade pip
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        python_path=".venv/Scripts/python.exe"
    else
        python_path=".venv/bin/python"
    fi
    
    # Install core dependencies
    $python_path -m pip install -r requirements.txt
    
    # Install development dependencies if requested
    if [[ "$DEV_DEPENDENCIES" == "true" ]]; then
        print_status "Installing development dependencies..."
        $python_path -m pip install -r requirements-dev.txt
    fi
    
    print_success "Dependencies installed successfully"
}

# Install Playwright browsers
install_browsers() {
    if [[ "$SKIP_BROWSERS" == "true" ]]; then
        print_warning "Skipping Playwright browser installation"
        return
    fi
    
    print_status "Installing Playwright browsers..."
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        python_path=".venv/Scripts/python.exe"
    else
        python_path=".venv/bin/python"
    fi
    
    $python_path -m playwright install
    
    print_success "Playwright browsers installed successfully"
}

# Create directories
create_directories() {
    print_status "Creating project directories..."
    
    mkdir -p test-results/{screenshots,videos,traces,reports}
    mkdir -p logs
    
    print_success "Directories created successfully"
}

# Setup Docker environment
setup_docker() {
    print_status "Setting up Docker environment..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Build Docker image
    print_status "Building Docker image..."
    docker-compose build playwright-tests
    
    if [[ $? -eq 0 ]]; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Create environment file
create_env_file() {
    if [[ ! -f ".env" ]]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_success ".env file created. Please customize it as needed."
    else
        print_warning ".env file already exists"
    fi
}

# Setup pre-commit hooks
setup_pre_commit() {
    if [[ "$DEV_DEPENDENCIES" == "true" ]]; then
        print_status "Setting up pre-commit hooks..."
        
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
            python_path=".venv/Scripts/python.exe"
        else
            python_path=".venv/bin/python"
        fi
        
        $python_path -m pre_commit install
        print_success "Pre-commit hooks installed"
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        python_path=".venv/Scripts/python.exe"
    else
        python_path=".venv/bin/python"
    fi
    
    # Test imports
    $python_path -c "import playwright; import pytest; import requests; import pydantic; print('All core packages imported successfully')"
    
    # Test pytest collection
    $python_path -m pytest --collect-only --quiet > /dev/null
    
    print_success "Installation verified successfully"
}

# Main setup function
main() {
    print_status "Python Playwright MCP Testing Framework Setup"
    print_status "Environment: $ENVIRONMENT"
    echo ""
    
    case $ENVIRONMENT in
        local)
            check_python
            setup_venv
            install_dependencies
            install_browsers
            create_directories
            create_env_file
            setup_pre_commit
            verify_installation
            ;;
        docker)
            setup_docker
            create_directories
            create_env_file
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    echo ""
    print_success "Setup completed successfully!"
    
    if [[ "$ENVIRONMENT" == "local" ]]; then
        echo ""
        print_status "Next steps:"
        echo "  1. Activate virtual environment: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)"
        echo "  2. Run tests: ./scripts/run-tests.sh"
        echo "  3. Run quick tests: ./scripts/quick-test.sh"
        echo "  4. Check available commands: make help"
    else
        echo ""
        print_status "Next steps:"
        echo "  1. Run tests: ./scripts/docker-tests.sh test"
        echo "  2. Start development environment: ./scripts/docker-tests.sh dev"
        echo "  3. Check Docker status: ./scripts/docker-tests.sh status"
    fi
}

# Run main function
main "$@"