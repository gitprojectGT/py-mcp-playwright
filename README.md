# Python Playwright MCP Testing Framework

A comprehensive Python testing framework using Playwright with Model Context Protocol (MCP) integration for automated web application and API testing.

## 🤖 AI-Powered Automation

**This entire project was fully automated using AI Claude as an agent configured through the command line.**

Using Claude Code's specialized testing agents, this framework was systematically generated through:

- **Automated Project Generation**: Claude Code agents analyzed requirements and generated the complete testing infrastructure
- **Intelligent Test Creation**: Specialized agents (playwright-test-generator, playwright-api-test-creator, playwright-api-explorer) created comprehensive test suites
- **Full CI/CD Pipeline**: Automated creation of GitHub Actions workflows with security scanning, multi-browser testing, and deployment
- **Docker Integration**: Automated containerization with multi-stage builds and optimized configurations
- **Documentation Generation**: AI-generated comprehensive documentation including this README, workflow guides, and code comments

The `.claude/` directory contains the agent configurations that powered this automation, demonstrating how AI can accelerate modern software development workflows.

## Features

- **Comprehensive API Testing**: Full CRUD operations testing with sync and async support
- **UI Testing**: Web application testing with accessibility and responsive design checks
- **MCP Integration**: Specialized Claude Code agents for test generation
- **Performance Testing**: Response time monitoring and concurrent request handling
- **Cross-browser Support**: Testing across Chromium, Firefox, and WebKit
- **Visual Testing**: Screenshot and video recording capabilities
- **Flexible Configuration**: Environment-based configuration with sensible defaults

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for containerized testing)

### Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd py-mcp-playwright
```

2. Run the setup script:
```bash
./scripts/setup.sh
```

Or manually:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### Docker Installation

```bash
# Build and setup Docker environment
./scripts/setup.sh -e docker

# Or manually
docker-compose build
```

### Running Tests

#### Local Testing
```bash
# Quick test runner
./scripts/quick-test.sh                    # Run smoke tests
./scripts/quick-test.sh api               # Run API tests
./scripts/quick-test.sh ui                # Run UI tests

# Full test runner
./scripts/run-tests.sh                    # Run all tests
./scripts/run-tests.sh -t api -v          # Run API tests with verbose output
./scripts/run-tests.sh -t ui --headed     # Run UI tests with browser GUI
./scripts/run-tests.sh -p -c              # Run with parallel execution and coverage

# Direct pytest usage
pytest                                    # Run all tests
pytest -m api                            # API tests only
pytest -m ui                             # UI tests only
pytest -m integration                    # Integration tests only
```

#### Docker Testing
```bash
# Docker test runner
./scripts/docker-tests.sh build          # Build Docker image
./scripts/docker-tests.sh test           # Run all tests
./scripts/docker-tests.sh api            # Run API tests
./scripts/docker-tests.sh ui             # Run UI tests
./scripts/docker-tests.sh coverage       # Run with coverage
./scripts/docker-tests.sh dev            # Start development environment

# Direct docker-compose usage
docker-compose run --rm playwright-tests
docker-compose run --rm playwright-api-tests
docker-compose run --rm playwright-ui-tests
```

#### Makefile Commands
```bash
make help                                 # Show available commands
make setup                               # Full project setup
make test                                # Run all tests
make test-api                            # Run API tests
make test-ui                             # Run UI tests
make test-coverage                       # Run with coverage
```

## Project Structure

```
py-mcp-playwright/
├── .claude/
│   └── agents/                 # Claude Code testing agents
├── src/                        # Source code modules
├── tests/
│   ├── api/                   # API testing suites
│   ├── ui/                    # UI testing suites
│   └── integration/           # Integration tests
├── utils/                     # Testing utilities
├── examples/                  # Example test implementations
├── docs/                      # Documentation
├── test-results/              # Test artifacts (screenshots, videos, reports)
├── conftest.py               # Pytest configuration and fixtures
├── playwright.config.py      # Playwright configuration
├── pyproject.toml           # Project configuration
└── requirements.txt         # Dependencies
```

## Configuration

### Environment Variables

- `HEADLESS`: Run browsers in headless mode (default: true)
- `SLOW_MO`: Slow down operations by milliseconds (default: 0)
- `TIMEOUT`: Default timeout for operations (default: 30000ms)
- `BASE_URL`: Base URL for testing (default: http://localhost:3000)
- `CI`: Enable CI-specific optimizations

### Test Markers

- `@pytest.mark.api`: API tests
- `@pytest.mark.ui`: UI tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Long-running tests
- `@pytest.mark.smoke`: Quick smoke tests

## Claude Code Agents

This project includes three specialized agents for test generation:

### 1. playwright-test-generator
Generates comprehensive Playwright tests for web applications with focus on:
- Role-based locators and semantic selectors
- Auto-retrying assertions
- Proper test structure and organization

### 2. playwright-api-test-creator
Creates API tests with full CRUD operation coverage:
- GET, POST, PUT, PATCH, DELETE operations
- Error handling and edge cases
- Authentication and authorization testing

### 3. playwright-api-explorer
Systematically explores APIs and generates comprehensive test suites:
- Resource discovery and documentation
- Test case design for all endpoints
- TypeScript test implementation

## Advanced Features

### Visual Testing
```python
# Take screenshots for visual regression testing
page.screenshot(path="test-results/screenshots/homepage.png")

# Element-specific screenshots
element.screenshot(path="test-results/screenshots/button.png")
```

### Performance Testing
```python
# Measure response times
import time
start_time = time.time()
response = api_context.get("/api/endpoint")
response_time = time.time() - start_time
assert response_time < 2.0
```

### Concurrent Testing
```python
# Test with multiple parallel requests
import threading
threads = []
for i in range(10):
    thread = threading.Thread(target=make_api_request, args=(i,))
    threads.append(thread)
    thread.start()
```

## Development

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy src/

# Linting
flake8 .
```

### Pre-commit Hooks

Install pre-commit hooks to maintain code quality:
```bash
pre-commit install
```

## GitHub Actions CI/CD

### Workflows

- **CI/CD Pipeline** (`ci.yml`): Main continuous integration with comprehensive testing
- **Pull Request** (`pr.yml`): PR validation, security scanning, and automated feedback
- **Release** (`release.yml`): Automated releases with staging and production deployment
- **Security** (`security.yml`): Daily security scans and vulnerability management

### Local Testing

```bash
# Test workflows locally
./scripts/test-workflows.sh ci
./scripts/test-workflows.sh pr
./scripts/test-workflows.sh security
./scripts/test-workflows.sh all

# Test with act (GitHub Actions locally)
./scripts/test-workflows.sh ci --act
```

### Features

✅ **Multi-platform Docker builds** (AMD64, ARM64)  
✅ **Cross-browser testing** (Chromium, Firefox, WebKit)  
✅ **Security scanning** (Bandit, Semgrep, Trivy, GitLeaks)  
✅ **Code coverage** with Codecov integration  
✅ **Automated releases** with changelog generation  
✅ **Performance testing** and monitoring  
✅ **Container registry** publishing  

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

The project is now fully set up with comprehensive CI/CD pipelines and ready for production deployment!