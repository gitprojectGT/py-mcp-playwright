# GitHub Actions CI/CD Documentation

This document describes the GitHub Actions workflows for the Python Playwright MCP Testing Framework.

## Overview

The project includes four main GitHub Actions workflows:

1. **CI/CD Pipeline** (`ci.yml`) - Main continuous integration and deployment
2. **Pull Request** (`pr.yml`) - PR validation and testing
3. **Release** (`release.yml`) - Automated releases and deployments
4. **Security** (`security.yml`) - Security scanning and compliance

## Workflows

### 1. CI/CD Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch with test type selection

**Jobs:**
- **code-quality**: Code formatting, linting, type checking, security scanning
- **build**: Docker image building with multi-platform support
- **test-matrix**: Test execution across browsers and test types
- **smoke-tests**: Quick validation tests
- **coverage**: Code coverage analysis with Codecov integration
- **performance**: Performance testing (main branch only)
- **manual-tests**: Manual workflow dispatch testing
- **test-summary**: Aggregated test results
- **deploy**: Production deployment (main branch only)
- **cleanup**: Artifact management and cleanup

**Features:**
- ✅ Multi-platform Docker builds (AMD64, ARM64)
- ✅ Test matrix across Chromium, Firefox, WebKit
- ✅ Parallel test execution
- ✅ Coverage reporting with Codecov
- ✅ Performance benchmarking
- ✅ Container registry publishing
- ✅ Automated deployment

### 2. Pull Request (`pr.yml`)

**Triggers:**
- PR opened, synchronized, reopened, or ready for review
- Targets `main` or `develop` branches

**Jobs:**
- **check-draft**: Skip detailed checks for draft PRs
- **pr-validation**: PR title validation, auto-labeling, breaking change detection
- **quick-validation**: Fast code quality and import checks
- **pr-smoke-tests**: Essential smoke tests for PRs
- **pr-security**: Security scanning of changed files
- **changes-analysis**: Analyze changed files and provide feedback
- **size-check**: PR size analysis and warnings
- **pr-status**: Final PR status summary

**Features:**
- ✅ Semantic PR title validation
- ✅ Automatic labeling based on file changes
- ✅ Security scan of changed files only
- ✅ PR size warnings for large changes
- ✅ Test coverage feedback for source changes
- ✅ Breaking change detection
- ✅ Comprehensive PR commenting

### 3. Release (`release.yml`)

**Triggers:**
- Tag push matching `v*.*.*`
- Manual workflow dispatch with version input

**Jobs:**
- **validate-release**: Version validation and pre-release detection
- **release-tests**: Comprehensive testing across all browsers and test types
- **build-release**: Multi-platform Docker image building
- **generate-changelog**: Automated changelog generation
- **create-release**: GitHub release creation
- **security-scan**: Security scanning of release images
- **deploy-staging**: Staging deployment
- **deploy-production**: Production deployment with approval
- **notify-release**: Release notifications and failure handling

**Features:**
- ✅ Semantic version validation
- ✅ Pre-release support
- ✅ Automated changelog generation
- ✅ Comprehensive release testing
- ✅ Security scanning with Trivy
- ✅ Staged deployment (staging → production)
- ✅ Failure notifications and issue creation

### 4. Security (`security.yml`)

**Triggers:**
- Daily scheduled scan at 2 AM UTC
- Push/PR with security-relevant file changes
- Manual workflow dispatch with scan type selection

**Jobs:**
- **code-security**: Bandit and Semgrep code analysis
- **dependency-security**: Safety and pip-audit dependency scanning
- **container-security**: Trivy and Docker Scout container scanning
- **secret-scan**: GitLeaks and TruffleHog secret detection
- **license-check**: License compliance validation
- **security-policy**: Security policy presence check
- **security-report**: Aggregated security reporting

**Features:**
- ✅ Multi-tool security scanning
- ✅ SARIF format for GitHub Security tab integration
- ✅ License compliance checking
- ✅ Secret detection across repository history
- ✅ Container vulnerability scanning
- ✅ Automated security issue creation
- ✅ Security policy compliance

## Configuration Files

### Auto-labeler (`.github/labeler.yml`)

Automatically labels PRs based on:
- **File changes**: API, UI, testing, documentation, configuration
- **Branch patterns**: Feature, bug fix, chore, refactor
- **Security relevance**: Security, performance, Docker changes

### Secret Detection (`.gitleaks.toml`)

Configured to detect:
- API keys and tokens
- Database URLs and passwords
- Private keys and certificates
- Cloud provider credentials
- Framework-specific secrets

## Testing Locally

### Using Docker

```bash
# Test workflow components
./scripts/test-workflows.sh ci
./scripts/test-workflows.sh pr
./scripts/test-workflows.sh security
./scripts/test-workflows.sh smoke

# Test all workflows
./scripts/test-workflows.sh all
```

### Using act (GitHub Actions locally)

```bash
# Install act (macOS)
brew install act

# Install act (Linux)
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Test workflows with act
./scripts/test-workflows.sh ci --act
./scripts/test-workflows.sh pr --act
```

### Manual Testing

```bash
# Test Docker build
docker build -t test-image .

# Run smoke tests
docker run --rm -e HEADLESS=true test-image python -m pytest -m smoke

# Test API endpoints
docker run --rm -e HEADLESS=true test-image python -m pytest -m api

# Test UI with headed mode (requires display)
docker run --rm -e HEADLESS=false -e DISPLAY=$DISPLAY test-image python -m pytest -m ui
```

## Environment Variables

### CI/CD Configuration

```bash
# Test execution
HEADLESS=true              # Run browsers in headless mode
SLOW_MO=0                 # Slow down operations (milliseconds)
TIMEOUT=30000             # Default timeout (milliseconds)
BROWSER_TIMEOUT=30000     # Browser-specific timeout
PYTEST_WORKERS=4          # Parallel test workers

# Environment
TEST_ENV=github-actions   # Test environment identifier
DEBUG=false              # Debug mode
LOG_LEVEL=INFO           # Logging level
CI=true                  # CI environment flag

# Reporting
SCREENSHOT_ON_FAILURE=true # Take screenshots on test failure
VIDEO_ON_FAILURE=true     # Record videos on test failure  
TRACE_ON_FAILURE=true     # Record traces on test failure

# Performance
MAX_RESPONSE_TIME=5.0     # Maximum API response time (seconds)
CONCURRENT_USERS=10       # Concurrent users for load testing
LOAD_TEST_DURATION=60     # Load test duration (seconds)
```

### Secrets Configuration

Required secrets in GitHub repository settings:

```bash
# Container Registry
GITHUB_TOKEN              # Provided automatically by GitHub

# Code Coverage  
CODECOV_TOKEN             # Optional: Codecov integration token

# Deployment (if used)
DEPLOY_TOKEN              # Deployment service token
SLACK_WEBHOOK             # Notification webhook (optional)

# Security Scanning (optional)
GITLEAKS_LICENSE          # GitLeaks license key
SNYK_TOKEN               # Snyk security scanning token
```

## Workflow Triggers

### Automatic Triggers

```yaml
# CI Pipeline
- push: [main, develop]
- pull_request: [main, develop]
- schedule: "0 6 * * 1"    # Weekly on Monday at 6 AM

# Security Scanning  
- push: security-related files
- pull_request: security-related files
- schedule: "0 2 * * *"    # Daily at 2 AM

# Release
- push: tags matching "v*.*.*"
```

### Manual Triggers

```yaml
# CI Pipeline - Manual Dispatch
inputs:
  test_type: [all, smoke, api, ui, integration]
  environment: [staging, production]

# Security Scanning - Manual Dispatch  
inputs:
  scan_type: [all, code, dependencies, containers, secrets]

# Release - Manual Dispatch
inputs:
  version: "v1.0.0"
  prerelease: [true, false]
```

## Monitoring and Notifications

### GitHub Integration

- **Security Tab**: SARIF uploads for security findings
- **Actions Tab**: Workflow run history and logs
- **Packages**: Container registry for Docker images
- **Releases**: Automated release creation with changelogs

### External Integrations

- **Codecov**: Code coverage reporting and trends
- **Container Registry**: Multi-platform Docker images
- **Security Advisories**: Automated vulnerability alerts

## Best Practices

### Workflow Design

1. **Fail Fast**: Quick validation before expensive operations
2. **Parallel Execution**: Independent jobs run concurrently
3. **Cache Utilization**: Docker layer and dependency caching
4. **Resource Optimization**: Appropriate runner sizes and timeouts
5. **Error Handling**: Comprehensive failure scenarios and recovery

### Security

1. **Principle of Least Privilege**: Minimal required permissions
2. **Secret Management**: Proper secret scoping and rotation
3. **Audit Trail**: Comprehensive logging and monitoring
4. **Vulnerability Management**: Automated scanning and alerting
5. **Compliance**: License and security policy enforcement

### Testing

1. **Test Pyramid**: Unit → Integration → E2E testing strategy
2. **Browser Coverage**: Multi-browser testing matrix
3. **Environment Parity**: Consistent testing environments
4. **Performance Benchmarks**: Automated performance regression detection
5. **Quality Gates**: Coverage and quality thresholds

## Troubleshooting

### Common Issues

#### Workflow Failures

```bash
# Check workflow logs
gh run list --repo OWNER/REPO
gh run view RUN_ID --log

# Debug specific job
gh run view RUN_ID --job JOB_ID
```

#### Docker Issues

```bash
# Test locally
docker build -t debug-image .
docker run -it --entrypoint bash debug-image

# Check browser installation
docker run debug-image playwright install --help
```

#### Test Failures

```bash
# Run tests with debug info
pytest -v -s --tb=long

# Check browser compatibility
playwright install --help
playwright install chromium firefox webkit
```

### Performance Issues

#### Slow Workflows

1. **Cache Optimization**: Ensure Docker layer caching is effective
2. **Parallel Jobs**: Increase parallel test execution
3. **Resource Allocation**: Use appropriate GitHub runner sizes
4. **Test Filtering**: Run only relevant tests for changes

#### Resource Limits

1. **Memory**: Monitor container memory usage
2. **Storage**: Clean up artifacts and caches regularly  
3. **Network**: Optimize image layers and downloads
4. **Compute**: Balance speed vs. cost considerations

## Maintenance

### Regular Tasks

1. **Dependency Updates**: Automated or manual dependency updates
2. **Browser Updates**: Playwright browser version updates
3. **Security Updates**: Security tool and signature updates
4. **Performance Review**: Workflow performance analysis
5. **Cost Optimization**: Resource usage and cost analysis

### Monitoring

1. **Workflow Success Rates**: Track failure patterns
2. **Performance Metrics**: Execution time trends
3. **Security Alerts**: Vulnerability and compliance alerts
4. **Resource Usage**: Compute and storage utilization
5. **Quality Metrics**: Test coverage and quality trends