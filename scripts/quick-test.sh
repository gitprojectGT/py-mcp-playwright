#!/bin/bash

# Quick test runner for Python Playwright MCP Testing Framework
# Usage: ./scripts/quick-test.sh [test-pattern]

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Quick test patterns
TEST_PATTERN="${1:-smoke}"

print_status "Running quick tests with pattern: $TEST_PATTERN"

# Check if virtual environment exists
if [[ ! -d ".venv" ]]; then
    print_error "Virtual environment not found. Please run 'make setup' first."
    exit 1
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Set environment for quick testing
export HEADLESS=true
export SLOW_MO=0
export TIMEOUT=10000

# Create test results directory
mkdir -p test-results/{screenshots,videos,traces}

# Run tests based on pattern
case $TEST_PATTERN in
    smoke)
        print_status "Running smoke tests..."
        python -m pytest -m smoke --tb=short -v --no-cov
        ;;
    api)
        print_status "Running API tests..."
        python -m pytest -m api --tb=short -v --no-cov
        ;;
    ui)
        print_status "Running UI tests..."
        python -m pytest -m ui --tb=short -v --no-cov
        ;;
    fast)
        print_status "Running fast tests (excluding slow)..."
        python -m pytest -m "not slow" --tb=short -v --no-cov
        ;;
    single)
        if [[ -z "$2" ]]; then
            print_error "Please provide a test file or test name for single test run"
            echo "Usage: $0 single tests/api/test_jsonplaceholder_api.py::TestJSONPlaceholderAPI::test_get_single_post"
            exit 1
        fi
        print_status "Running single test: $2"
        python -m pytest "$2" --tb=short -v --no-cov
        ;;
    *)
        print_status "Running tests matching pattern: $TEST_PATTERN"
        python -m pytest -k "$TEST_PATTERN" --tb=short -v --no-cov
        ;;
esac

if [[ $? -eq 0 ]]; then
    print_success "Quick tests completed successfully!"
else
    print_error "Quick tests failed!"
    exit 1
fi