#!/bin/bash

# Python Playwright MCP Testing Framework - Test Runner Script
# Usage: ./scripts/run-tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
ENVIRONMENT="local"
HEADLESS=true
PARALLEL=false
COVERAGE=false
VERBOSE=false
BROWSER="chromium"
OUTPUT_DIR="test-results"

# Help function
show_help() {
    echo "Python Playwright MCP Testing Framework - Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  -t, --type TYPE          Test type: all, api, ui, integration, smoke (default: all)"
    echo "  -e, --env ENV           Environment: local, docker (default: local)"
    echo "  -b, --browser BROWSER   Browser: chromium, firefox, webkit (default: chromium)"
    echo "  -H, --headless          Run in headless mode (default: true)"
    echo "  --headed                Run in headed mode"
    echo "  -p, --parallel          Run tests in parallel"
    echo "  -c, --coverage          Run with coverage reporting"
    echo "  -v, --verbose           Verbose output"
    echo "  -o, --output DIR        Output directory for test results (default: test-results)"
    echo "  --clean                 Clean test results before running"
    echo "  --smoke                 Run only smoke tests"
    echo "  --slow                  Include slow tests"
    echo "  --docker-build          Force Docker image rebuild"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all tests locally"
    echo "  $0 -t api -v                        # Run API tests with verbose output"
    echo "  $0 -t ui --headed -b firefox        # Run UI tests in Firefox with GUI"
    echo "  $0 -e docker -p -c                  # Run all tests in Docker with parallel execution and coverage"
    echo "  $0 --smoke                          # Run only smoke tests"
    echo "  $0 -t integration --slow            # Run integration tests including slow ones"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        -H|--headless)
            HEADLESS=true
            shift
            ;;
        --headed)
            HEADLESS=false
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --smoke)
            TEST_TYPE="smoke"
            shift
            ;;
        --slow)
            INCLUDE_SLOW=true
            shift
            ;;
        --docker-build)
            DOCKER_BUILD=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

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

# Function to clean test results
clean_results() {
    if [[ "$CLEAN" == "true" ]]; then
        print_status "Cleaning test results..."
        rm -rf $OUTPUT_DIR/*
        mkdir -p $OUTPUT_DIR/{screenshots,videos,traces,reports}
    fi
}

# Function to build pytest command
build_pytest_cmd() {
    local cmd="python -m pytest"
    
    # Add test type marker
    case $TEST_TYPE in
        api)
            cmd="$cmd -m api"
            ;;
        ui)
            cmd="$cmd -m ui"
            ;;
        integration)
            cmd="$cmd -m integration"
            ;;
        smoke)
            cmd="$cmd -m smoke"
            ;;
        all)
            # Run all tests
            ;;
        *)
            print_error "Invalid test type: $TEST_TYPE"
            exit 1
            ;;
    esac
    
    # Add slow tests if requested
    if [[ "$INCLUDE_SLOW" == "true" ]]; then
        if [[ "$cmd" == *"-m"* ]]; then
            cmd="$cmd or slow"
        else
            cmd="$cmd -m slow"
        fi
    fi
    
    # Add parallel execution
    if [[ "$PARALLEL" == "true" ]]; then
        cmd="$cmd -n auto"
    fi
    
    # Add coverage
    if [[ "$COVERAGE" == "true" ]]; then
        cmd="$cmd --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=80"
    fi
    
    # Add verbose output
    if [[ "$VERBOSE" == "true" ]]; then
        cmd="$cmd -v"
    else
        cmd="$cmd --tb=short"
    fi
    
    # Add browser selection
    cmd="$cmd --browser $BROWSER"
    
    echo "$cmd"
}

# Function to run tests locally
run_local_tests() {
    print_status "Running tests locally..."
    
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
    
    # Set environment variables
    export HEADLESS=$HEADLESS
    export PLAYWRIGHT_BROWSER=$BROWSER
    
    # Clean results if requested
    clean_results
    
    # Build and run pytest command
    local pytest_cmd=$(build_pytest_cmd)
    print_status "Executing: $pytest_cmd"
    
    if eval "$pytest_cmd"; then
        print_success "Tests completed successfully!"
    else
        print_error "Tests failed!"
        exit 1
    fi
}

# Function to run tests in Docker
run_docker_tests() {
    print_status "Running tests in Docker..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Build Docker image if requested
    if [[ "$DOCKER_BUILD" == "true" ]]; then
        print_status "Building Docker image..."
        docker-compose build playwright-tests
    fi
    
    # Clean results if requested
    clean_results
    
    # Set environment variables for Docker
    export HEADLESS=$HEADLESS
    export PLAYWRIGHT_BROWSER=$BROWSER
    
    # Build pytest command for Docker
    local pytest_cmd=$(build_pytest_cmd)
    
    # Run tests in Docker
    case $TEST_TYPE in
        api)
            print_status "Running API tests in Docker..."
            docker-compose run --rm playwright-api-tests
            ;;
        ui)
            print_status "Running UI tests in Docker..."
            docker-compose run --rm playwright-ui-tests
            ;;
        integration)
            print_status "Running integration tests in Docker..."
            docker-compose run --rm playwright-integration-tests
            ;;
        smoke)
            print_status "Running smoke tests in Docker..."
            docker-compose run --rm playwright-smoke-tests
            ;;
        all)
            if [[ "$COVERAGE" == "true" ]]; then
                print_status "Running all tests with coverage in Docker..."
                docker-compose run --rm playwright-coverage
            else
                print_status "Running all tests in Docker..."
                docker-compose run --rm playwright-tests
            fi
            ;;
    esac
    
    if [[ $? -eq 0 ]]; then
        print_success "Docker tests completed successfully!"
    else
        print_error "Docker tests failed!"
        exit 1
    fi
}

# Main execution
main() {
    print_status "Python Playwright MCP Testing Framework"
    print_status "Test Type: $TEST_TYPE"
    print_status "Environment: $ENVIRONMENT"
    print_status "Browser: $BROWSER"
    print_status "Headless: $HEADLESS"
    print_status "Parallel: $PARALLEL"
    print_status "Coverage: $COVERAGE"
    echo ""
    
    # Create output directory
    mkdir -p $OUTPUT_DIR/{screenshots,videos,traces,reports}
    
    case $ENVIRONMENT in
        local)
            run_local_tests
            ;;
        docker)
            run_docker_tests
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"