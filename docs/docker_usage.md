# Docker Usage Guide

This guide explains how to use Docker with the Python Playwright MCP Testing Framework for containerized testing.

## Overview

The framework provides comprehensive Docker support for:
- Isolated test execution environments
- Consistent testing across different systems
- CI/CD pipeline integration
- Development environment standardization

## Docker Components

### Dockerfile
- Multi-stage build for optimized image size
- Pre-installed Playwright browsers and dependencies
- Non-root user for security
- Health checks for container monitoring

### Docker Compose Services

#### Core Services
- **playwright-tests**: Main test execution service
- **playwright-dev**: Development environment service
- **playwright-api-tests**: API-specific test service
- **playwright-ui-tests**: UI-specific test service
- **playwright-integration-tests**: Integration test service
- **playwright-smoke-tests**: Smoke test service
- **playwright-coverage**: Coverage reporting service

## Quick Commands

### Building and Setup
```bash
# Build Docker image
./scripts/docker-tests.sh build

# Build with no cache
./scripts/docker-tests.sh build --no-cache

# Setup complete Docker environment
./scripts/setup.sh -e docker
```

### Running Tests
```bash
# Run all tests
./scripts/docker-tests.sh test

# Run specific test types
./scripts/docker-tests.sh api
./scripts/docker-tests.sh ui
./scripts/docker-tests.sh integration
./scripts/docker-tests.sh smoke

# Run with coverage
./scripts/docker-tests.sh coverage
```

### Development Environment
```bash
# Start development container
./scripts/docker-tests.sh dev

# Open shell in development container
./scripts/docker-tests.sh shell

# View logs
./scripts/docker-tests.sh logs

# Check container status
./scripts/docker-tests.sh status
```

### Cleanup
```bash
# Clean up all Docker resources
./scripts/docker-tests.sh clean
```

## Direct Docker Compose Usage

### Running Tests
```bash
# Run all tests
docker-compose run --rm playwright-tests

# Run API tests
docker-compose run --rm playwright-api-tests

# Run UI tests  
docker-compose run --rm playwright-ui-tests

# Run with custom command
docker-compose run --rm playwright-tests python -m pytest -k "test_homepage" -v
```

### Development Workflow
```bash
# Start development environment
docker-compose up -d playwright-dev

# Execute commands in running container
docker-compose exec playwright-dev python -m pytest -k "test_api"

# View logs
docker-compose logs -f playwright-dev

# Stop development environment
docker-compose down
```

## Environment Variables

Set these in `.env` file or pass directly to Docker:

### Test Configuration
```bash
HEADLESS=true                    # Run browsers in headless mode
SLOW_MO=0                       # Slow down operations (ms)
TIMEOUT=30000                   # Default timeout (ms)
BROWSER_TIMEOUT=30000           # Browser timeout (ms)
BASE_URL=http://localhost:3000  # Base URL for testing
```

### API Configuration
```bash
API_BASE_URL=https://jsonplaceholder.typicode.com
API_TIMEOUT=30000
```

### Test Environment
```bash
TEST_ENV=docker                 # Test environment
DEBUG=false                     # Debug mode
LOG_LEVEL=INFO                  # Logging level
CI=true                         # CI environment flag
```

### Performance
```bash
PYTEST_WORKERS=4                # Parallel test workers
MAX_RESPONSE_TIME=5.0           # Max API response time
CONCURRENT_USERS=10             # Concurrent users for load testing
```

### Recording and Reporting
```bash
SCREENSHOT_ON_FAILURE=true      # Take screenshots on failure
VIDEO_ON_FAILURE=true           # Record videos on failure
TRACE_ON_FAILURE=true           # Record traces on failure
```

## Volume Mounts

### Development Volumes
```yaml
volumes:
  - .:/app                      # Source code for live editing
  - ./test-results:/app/test-results  # Test results output
  - playwright-cache:/home/playwright/.cache  # Playwright cache
```

### Production Volumes
```yaml
volumes:
  - ./test-results:/app/test-results  # Results only
```

## Networking

### Default Network
All services use the `playwright-network` bridge network for isolation.

### External Services
To test against external services, ensure proper network configuration:

```yaml
services:
  playwright-tests:
    networks:
      - playwright-network
      - external-network
```

## Performance Optimization

### Image Size Optimization
- Multi-stage build process
- Minimal base image (python:3.13-slim)
- Cleanup of unnecessary packages
- Layer caching optimization

### Runtime Optimization
- Shared Playwright cache volume
- Parallel test execution
- Resource limits configuration

### Build Optimization
```bash
# Use build cache
docker-compose build

# Force rebuild without cache
docker-compose build --no-cache

# Pull latest base images
docker-compose build --pull
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Docker Tests
on: [push, pull_request]

jobs:
  docker-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and test
        run: |
          ./scripts/docker-tests.sh build
          ./scripts/docker-tests.sh test
          
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

### GitLab CI Example
```yaml
test:
  image: docker:latest
  services:
    - docker:dind
  script:
    - ./scripts/docker-tests.sh build
    - ./scripts/docker-tests.sh test
  artifacts:
    when: always
    paths:
      - test-results/
    expire_in: 1 week
```

## Troubleshooting

### Common Issues

#### Browser Installation
If Playwright browsers fail to install:
```bash
# Rebuild with fresh browser installation
./scripts/docker-tests.sh build --no-cache
```

#### Permission Issues
Ensure proper file permissions:
```bash
# Fix permissions for test results
sudo chown -R $USER:$USER test-results/
```

#### Memory Issues
For large test suites, increase Docker memory:
```bash
# In docker-compose.yml
services:
  playwright-tests:
    mem_limit: 2g
    memswap_limit: 2g
```

#### Network Issues
For external API testing:
```bash
# Test network connectivity
docker-compose run --rm playwright-tests curl -I https://example.com
```

### Debugging

#### Interactive Debugging
```bash
# Start container with shell
./scripts/docker-tests.sh shell

# Run specific test with debugging
python -m pytest tests/api/test_example.py -v -s --tb=long
```

#### Log Analysis
```bash
# View container logs
./scripts/docker-tests.sh logs --follow

# Export logs
docker-compose logs playwright-tests > test-logs.txt
```

#### Performance Analysis
```bash
# Monitor resource usage
docker stats

# Analyze image layers
docker history py-mcp-playwright_playwright-tests
```

## Best Practices

### Development
1. Use development service for interactive work
2. Mount source code for live editing
3. Use separate containers for different test types
4. Keep test data isolated

### Production
1. Use immutable image builds
2. Run tests with read-only containers
3. Implement proper health checks
4. Use resource limits

### Security
1. Run as non-root user
2. Use minimal base images
3. Scan images for vulnerabilities
4. Keep dependencies updated

### Performance
1. Use layer caching effectively
2. Optimize Dockerfile for build speed
3. Use parallel test execution
4. Monitor resource usage