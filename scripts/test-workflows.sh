#!/bin/bash

# Test GitHub Actions workflows locally
# Usage: ./scripts/test-workflows.sh [workflow] [options]

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

# Help function
show_help() {
    echo "Test GitHub Actions workflows locally"
    echo ""
    echo "Usage: $0 [WORKFLOW] [OPTIONS]"
    echo ""
    echo "WORKFLOWS:"
    echo "  ci                      Test CI/CD workflow"
    echo "  pr                      Test PR workflow"
    echo "  security                Test security workflow"
    echo "  build                   Test Docker build only"
    echo "  smoke                   Test smoke tests"
    echo "  all                     Test all workflows"
    echo ""
    echo "OPTIONS:"
    echo "  --act                   Use act to simulate GitHub Actions"
    echo "  --docker-only           Test only Docker-based components"
    echo "  --verbose               Verbose output"
    echo "  --cleanup               Clean up after tests"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 ci                   # Test CI workflow with Docker"
    echo "  $0 pr --act             # Test PR workflow with act"
    echo "  $0 smoke --verbose      # Test smoke tests with verbose output"
    echo "  $0 all --cleanup        # Test all workflows and cleanup"
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is required but not installed"
        exit 1
    fi
    
    if [[ "$USE_ACT" == "true" ]] && ! command -v act &> /dev/null; then
        print_warning "act is not installed. Install with: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
        print_status "Falling back to Docker-only testing"
        USE_ACT="false"
    fi
    
    print_success "Dependencies check passed"
}

# Test Docker build
test_docker_build() {
    print_status "Testing Docker build..."
    
    # Build the test image
    docker build -t workflow-test:latest .
    
    if [[ $? -eq 0 ]]; then
        print_success "Docker build successful"
        return 0
    else
        print_error "Docker build failed"
        return 1
    fi
}

# Test smoke tests
test_smoke_tests() {
    print_status "Testing smoke tests..."
    
    mkdir -p test-results
    
    # Run smoke tests in Docker
    docker run --rm \
        -e HEADLESS=true \
        -e TEST_ENV=local-test \
        -v "$(pwd)/test-results:/app/test-results" \
        workflow-test:latest \
        python -m pytest -m smoke --tb=short -v \
        --junitxml=test-results/junit-smoke-local.xml
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        print_success "Smoke tests passed"
        return 0
    else
        print_error "Smoke tests failed"
        return 1
    fi
}

# Test CI workflow components
test_ci_workflow() {
    print_status "Testing CI workflow components..."
    
    local success=true
    
    # Test code quality
    print_status "Testing code quality checks..."
    if command -v python &> /dev/null && [[ -d ".venv" ]]; then
        source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || true
        
        # Run linting
        if command -v flake8 &> /dev/null; then
            flake8 src tests utils examples --select=E9,F63,F7,F82 --show-source --statistics || success=false
        fi
        
        # Run formatting check
        if command -v black &> /dev/null; then
            black --check --diff src tests utils examples || success=false
        fi
    else
        print_warning "Python environment not available, skipping code quality checks"
    fi
    
    # Test Docker build
    test_docker_build || success=false
    
    # Test smoke tests
    test_smoke_tests || success=false
    
    if [[ "$success" == "true" ]]; then
        print_success "CI workflow components passed"
        return 0
    else
        print_error "Some CI workflow components failed"
        return 1
    fi
}

# Test PR workflow components
test_pr_workflow() {
    print_status "Testing PR workflow components..."
    
    local success=true
    
    # Test quick validation
    print_status "Testing quick validation..."
    if command -v python &> /dev/null; then
        python -c "
import sys
sys.path.append('src')
try:
    from src.config import get_test_config, get_api_config
    from src.test_helpers import TestDataGenerator, APITestHelper
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || success=false
    fi
    
    # Test smoke tests (same as CI)
    test_smoke_tests || success=false
    
    if [[ "$success" == "true" ]]; then
        print_success "PR workflow components passed"
        return 0
    else
        print_error "Some PR workflow components failed"
        return 1
    fi
}

# Test security workflow components
test_security_workflow() {
    print_status "Testing security workflow components..."
    
    local success=true
    
    # Test with available security tools
    if command -v python &> /dev/null && [[ -d ".venv" ]]; then
        source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || true
        
        # Install security tools if needed
        pip install bandit safety 2>/dev/null || true
        
        # Run bandit if available
        if command -v bandit &> /dev/null; then
            print_status "Running Bandit security scan..."
            bandit -r src/ -f json -o test-results/bandit-local.json || success=false
        fi
        
        # Run safety if available
        if command -v safety &> /dev/null; then
            print_status "Running Safety dependency scan..."
            safety check --json --output test-results/safety-local.json || true
        fi
    else
        print_warning "Python environment not available, skipping security scans"
    fi
    
    # Test container security with Trivy if available
    if command -v trivy &> /dev/null; then
        print_status "Running Trivy container scan..."
        trivy image workflow-test:latest --format json --output test-results/trivy-local.json || success=false
    else
        print_warning "Trivy not available, skipping container security scan"
    fi
    
    if [[ "$success" == "true" ]]; then
        print_success "Security workflow components passed"
        return 0
    else
        print_error "Some security workflow components failed"
        return 1
    fi
}

# Test with act (GitHub Actions local runner)
test_with_act() {
    local workflow="$1"
    
    print_status "Testing workflow with act: $workflow"
    
    case $workflow in
        ci)
            act push -W .github/workflows/ci.yml --container-architecture linux/amd64
            ;;
        pr)
            act pull_request -W .github/workflows/pr.yml --container-architecture linux/amd64
            ;;
        security)
            act push -W .github/workflows/security.yml --container-architecture linux/amd64
            ;;
        *)
            print_error "Unknown workflow for act: $workflow"
            return 1
            ;;
    esac
}

# Cleanup function
cleanup() {
    if [[ "$CLEANUP" == "true" ]]; then
        print_status "Cleaning up..."
        
        # Remove test images
        docker rmi workflow-test:latest 2>/dev/null || true
        
        # Clean up test results if requested
        if [[ "$VERBOSE" != "true" ]]; then
            rm -rf test-results/junit-*-local.xml 2>/dev/null || true
            rm -rf test-results/*-local.json 2>/dev/null || true
        fi
        
        print_success "Cleanup completed"
    fi
}

# Parse command line arguments
WORKFLOW=""
USE_ACT=false
DOCKER_ONLY=false
VERBOSE=false
CLEANUP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        ci|pr|security|build|smoke|all)
            WORKFLOW="$1"
            shift
            ;;
        --act)
            USE_ACT=true
            shift
            ;;
        --docker-only)
            DOCKER_ONLY=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --cleanup)
            CLEANUP=true
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

# Default to ci if no workflow specified
if [[ -z "$WORKFLOW" ]]; then
    WORKFLOW="ci"
fi

# Main execution
main() {
    print_status "Testing GitHub Actions workflows locally"
    print_status "Workflow: $WORKFLOW"
    print_status "Use act: $USE_ACT"
    print_status "Docker only: $DOCKER_ONLY"
    print_status "Verbose: $VERBOSE"
    echo ""
    
    # Setup cleanup trap
    trap cleanup EXIT
    
    # Check dependencies
    check_dependencies
    
    # Create test results directory
    mkdir -p test-results
    
    # Run tests based on workflow
    case $WORKFLOW in
        build)
            test_docker_build
            ;;
        smoke)
            test_docker_build && test_smoke_tests
            ;;
        ci)
            if [[ "$USE_ACT" == "true" ]]; then
                test_with_act "ci"
            else
                test_ci_workflow
            fi
            ;;
        pr)
            if [[ "$USE_ACT" == "true" ]]; then
                test_with_act "pr"
            else
                test_pr_workflow
            fi
            ;;
        security)
            if [[ "$USE_ACT" == "true" ]]; then
                test_with_act "security"
            else
                test_security_workflow
            fi
            ;;
        all)
            local overall_success=true
            
            test_ci_workflow || overall_success=false
            test_pr_workflow || overall_success=false
            test_security_workflow || overall_success=false
            
            if [[ "$overall_success" == "true" ]]; then
                print_success "All workflow tests passed!"
            else
                print_error "Some workflow tests failed!"
                exit 1
            fi
            ;;
        *)
            print_error "Unknown workflow: $WORKFLOW"
            show_help
            exit 1
            ;;
    esac
    
    print_success "Workflow testing completed!"
}

# Run main function
main "$@"