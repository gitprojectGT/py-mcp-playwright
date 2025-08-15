#!/bin/bash

# Docker-specific test runner for Python Playwright MCP Testing Framework
# Usage: ./scripts/docker-tests.sh [command] [options]

set -e

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

# Help function
show_help() {
    echo "Docker Test Runner for Python Playwright MCP Testing Framework"
    echo ""
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo ""
    echo "COMMANDS:"
    echo "  build                   Build Docker image"
    echo "  test                    Run all tests"
    echo "  api                     Run API tests only"
    echo "  ui                      Run UI tests only"
    echo "  integration             Run integration tests only"
    echo "  smoke                   Run smoke tests only"
    echo "  coverage                Run tests with coverage"
    echo "  dev                     Start development container"
    echo "  shell                   Open shell in development container"
    echo "  clean                   Clean up Docker resources"
    echo "  logs                    Show logs from test runs"
    echo "  status                  Show container status"
    echo ""
    echo "OPTIONS:"
    echo "  --rebuild               Force rebuild of Docker image"
    echo "  --no-cache              Build without using cache"
    echo "  --pull                  Pull latest base image before build"
    echo "  -f, --follow            Follow logs in real-time"
    echo "  -v, --verbose           Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 build                           # Build Docker image"
    echo "  $0 test                            # Run all tests"
    echo "  $0 api --verbose                   # Run API tests with verbose output"
    echo "  $0 coverage                        # Run tests with coverage"
    echo "  $0 dev                             # Start development environment"
    echo "  $0 shell                           # Open interactive shell"
    echo "  $0 clean                           # Clean up resources"
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
}

# Build Docker image
build_image() {
    local build_args=""
    
    if [[ "$NO_CACHE" == "true" ]]; then
        build_args="$build_args --no-cache"
    fi
    
    if [[ "$PULL" == "true" ]]; then
        build_args="$build_args --pull"
    fi
    
    print_status "Building Docker image..."
    docker-compose build $build_args playwright-tests
    
    if [[ $? -eq 0 ]]; then
        print_success "Docker image built successfully!"
    else
        print_error "Failed to build Docker image!"
        exit 1
    fi
}

# Run tests
run_tests() {
    local service="$1"
    local extra_args="${@:2}"
    
    print_status "Running tests with service: $service"
    
    if [[ "$VERBOSE" == "true" ]]; then
        docker-compose run --rm $service $extra_args
    else
        docker-compose run --rm $service $extra_args
    fi
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        print_success "Tests completed successfully!"
    else
        print_error "Tests failed with exit code: $exit_code"
        exit $exit_code
    fi
}

# Start development environment
start_dev() {
    print_status "Starting development environment..."
    docker-compose up -d playwright-dev
    
    if [[ $? -eq 0 ]]; then
        print_success "Development environment started!"
        print_status "Use '$0 shell' to access the container"
        print_status "Use 'docker-compose logs -f playwright-dev' to follow logs"
    else
        print_error "Failed to start development environment!"
        exit 1
    fi
}

# Open shell in development container
open_shell() {
    print_status "Opening shell in development container..."
    
    # Check if development container is running
    if ! docker-compose ps playwright-dev | grep -q "Up"; then
        print_status "Development container not running. Starting it first..."
        start_dev
        sleep 5
    fi
    
    docker-compose exec playwright-dev /bin/bash
}

# Show logs
show_logs() {
    local service="${1:-playwright-tests}"
    
    if [[ "$FOLLOW" == "true" ]]; then
        print_status "Following logs for service: $service"
        docker-compose logs -f $service
    else
        print_status "Showing logs for service: $service"
        docker-compose logs $service
    fi
}

# Show container status
show_status() {
    print_status "Container status:"
    docker-compose ps
    
    echo ""
    print_status "Docker images:"
    docker images | grep py-mcp-playwright
}

# Clean up Docker resources
clean_up() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker-compose down
    
    # Remove images
    print_status "Removing Docker images..."
    docker images -q py-mcp-playwright* | xargs -r docker rmi
    
    # Remove volumes
    print_status "Removing Docker volumes..."
    docker volume ls -q | grep py-mcp-playwright | xargs -r docker volume rm
    
    # Prune dangling images and containers
    docker system prune -f
    
    print_success "Cleanup completed!"
}

# Parse command line arguments
COMMAND=""
REBUILD=false
NO_CACHE=false
PULL=false
FOLLOW=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        build|test|api|ui|integration|smoke|coverage|dev|shell|clean|logs|status)
            COMMAND="$1"
            shift
            ;;
        --rebuild)
            REBUILD=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --pull)
            PULL=true
            shift
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
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

# Check if command is provided
if [[ -z "$COMMAND" ]]; then
    print_error "No command provided"
    show_help
    exit 1
fi

# Main execution
main() {
    check_docker
    
    # Rebuild if requested
    if [[ "$REBUILD" == "true" ]]; then
        build_image
    fi
    
    case $COMMAND in
        build)
            build_image
            ;;
        test)
            run_tests "playwright-tests"
            ;;
        api)
            run_tests "playwright-api-tests"
            ;;
        ui)
            run_tests "playwright-ui-tests"
            ;;
        integration)
            run_tests "playwright-integration-tests"
            ;;
        smoke)
            run_tests "playwright-smoke-tests"
            ;;
        coverage)
            run_tests "playwright-coverage"
            ;;
        dev)
            start_dev
            ;;
        shell)
            open_shell
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        clean)
            clean_up
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"